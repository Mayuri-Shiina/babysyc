from dataclasses import dataclass
from datetime import datetime, timezone

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.agent import AgentMessage, AgentSession
from app.models.baby import Baby
from app.models.growth import GrowthRecord
from app.models.media import MediaAsset
from app.models.reminder import Reminder
from app.models.vaccine import VaccinePlan, VaccineRecord


@dataclass(frozen=True)
class AgentContextSnapshot:
    baby_name: str
    birth_date: str
    gender: str
    age_days: int
    age_months: int
    recent_growth: list[str]
    recent_media: list[str]
    upcoming_reminders: list[str]
    vaccine_status: list[str]


# 生成宝宝近期上下文快照，供模型回答时使用真实档案数据。
def build_agent_context_snapshot(db: Session, family_id: str, baby: Baby) -> AgentContextSnapshot:
    age_days = max((datetime.now().date() - baby.birth_date).days, 0)

    growth_records = db.scalars(
        select(GrowthRecord)
        .where(GrowthRecord.baby_id == baby.id)
        .order_by(GrowthRecord.recorded_at.desc())
        .limit(5)
    ).all()
    media_assets = db.scalars(
        select(MediaAsset)
        .where(MediaAsset.family_id == family_id, MediaAsset.baby_id == baby.id)
        .order_by(MediaAsset.captured_at.desc())
        .limit(5)
    ).all()
    reminders = db.scalars(
        select(Reminder)
        .where(Reminder.family_id == family_id, Reminder.baby_id == baby.id, Reminder.status == "pending")
        .order_by(Reminder.due_at.asc())
        .limit(5)
    ).all()
    vaccine_plans = db.scalars(
        select(VaccinePlan)
        .where(VaccinePlan.family_id == family_id, VaccinePlan.baby_id == baby.id)
        .order_by(VaccinePlan.scheduled_date.asc())
        .limit(5)
    ).all()
    vaccine_records = db.scalars(
        select(VaccineRecord)
        .where(VaccineRecord.family_id == family_id, VaccineRecord.baby_id == baby.id)
        .order_by(VaccineRecord.administered_date.desc())
        .limit(3)
    ).all()

    recent_growth = [
        f"{record.record_type}: {record.value}{record.unit} at {record.recorded_at.isoformat()}"
        + (f" note={record.note}" if record.note else "")
        for record in growth_records
    ]
    recent_media = [
        f"{asset.media_type}: {asset.file_name} at {asset.captured_at.isoformat()}"
        + (f" desc={asset.description}" if asset.description else "")
        + (f" tags={asset.tags}" if asset.tags else "")
        for asset in media_assets
    ]
    upcoming_reminders = [
        f"{reminder.reminder_type}: {reminder.title} due {reminder.due_at.isoformat()}"
        + (f" desc={reminder.description}" if reminder.description else "")
        for reminder in reminders
    ]
    vaccine_status = [
        f"plan {plan.vaccine_name} {plan.dose_label} on {plan.scheduled_date.isoformat()} status={plan.status}"
        for plan in vaccine_plans
    ] + [
        f"record on {record.administered_date.isoformat()} status={record.status} provider={record.provider or 'unknown'}"
        for record in vaccine_records
    ]

    return AgentContextSnapshot(
        baby_name=baby.nickname,
        birth_date=baby.birth_date.isoformat(),
        gender=baby.gender,
        age_days=age_days,
        age_months=age_days // 30,
        recent_growth=recent_growth,
        recent_media=recent_media,
        upcoming_reminders=upcoming_reminders,
        vaccine_status=vaccine_status,
    )


# 将最近对话历史转换为兼容 OpenAI 接口的消息格式。
def build_conversation_messages(db: Session, session_id: str) -> list[dict[str, str]]:
    messages = db.scalars(
        select(AgentMessage)
        .where(AgentMessage.session_id == session_id)
        .order_by(AgentMessage.created_at.asc())
        .limit(12)
    ).all()

    payload_messages: list[dict[str, str]] = []
    for message in messages:
        if message.role not in {"user", "assistant"}:
            continue
        payload_messages.append(
            {
                "role": message.role,
                "content": message.content,
            }
        )
    return payload_messages


# 将宝宝上下文整理为模型更易消费的文本块。
def build_context_block(snapshot: AgentContextSnapshot) -> str:
    sections = [
        f"宝宝昵称: {snapshot.baby_name}",
        f"出生日期: {snapshot.birth_date}",
        f"性别: {snapshot.gender}",
        f"日龄: {snapshot.age_days}",
        f"月龄: {snapshot.age_months}",
        "最近成长记录:",
        *(snapshot.recent_growth or ["暂无成长记录"]),
        "最近媒体记录:",
        *(snapshot.recent_media or ["暂无媒体记录"]),
        "待处理提醒:",
        *(snapshot.upcoming_reminders or ["暂无待处理提醒"]),
        "疫苗相关状态:",
        *(snapshot.vaccine_status or ["暂无疫苗计划或接种记录"]),
    ]
    return "\n".join(sections)


# 构造系统提示词，约束助手围绕家庭档案提供建议且避免医疗诊断。
def build_system_prompt(snapshot: AgentContextSnapshot) -> str:
    context_block = build_context_block(snapshot)
    today = datetime.now(timezone.utc).date().isoformat()
    return (
        "你是一个家庭宝宝成长档案助手，服务于私人家庭档案场景。"
        "你的目标是基于真实档案回答问题、整理成长信息、给出温和且可执行的建议。"
        "你必须优先使用提供的上下文，不要编造不存在的记录。"
        "如果信息不足，要明确说明依据不足。"
        "你不是医生，不能做医疗诊断；遇到高风险症状时，提醒尽快线下就医。"
        "回答请使用中文，尽量结构清晰，优先给出结论、依据、建议行动。"
        f"\n今天日期: {today}\n\n宝宝档案上下文:\n{context_block}"
    )


# 从兼容接口响应中提取助手文本，兼容字符串或分段内容。
def extract_assistant_content(response_data: dict) -> str:
    choices = response_data.get("choices") or []
    if not choices:
        raise ValueError("Model response does not include choices")

    message = choices[0].get("message") or {}
    content = message.get("content")
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if not isinstance(item, dict):
                continue
            text = item.get("text") or item.get("content")
            if text:
                parts.append(str(text).strip())
        joined = "\n".join(part for part in parts if part)
        if joined:
            return joined
    raise ValueError("Model response does not include assistant text")


# 根据用户问题和模型回复估算风险等级，供前端展示提醒强度。
def infer_risk_level(user_content: str, assistant_content: str) -> str:
    combined_text = f"{user_content}\n{assistant_content}"
    high_risk_keywords = ["发烧", "高烧", "抽搐", "呼吸", "昏迷", "便血", "过敏", "急诊", "紫绀"]
    medium_risk_keywords = ["咳嗽", "腹泻", "呕吐", "疫苗", "体温", "拒奶", "皮疹"]

    if any(keyword in combined_text for keyword in high_risk_keywords):
        return "high"
    if any(keyword in combined_text for keyword in medium_risk_keywords):
        return "medium"
    return "low"


# 调用阿里百炼兼容接口生成真实助手回复。
async def generate_agent_reply(db: Session, session: AgentSession, baby: Baby) -> tuple[str, str]:
    if not settings.ai_api_key:
        raise RuntimeError("AI API key is not configured")

    snapshot = build_agent_context_snapshot(db=db, family_id=session.family_id, baby=baby)
    payload = {
        "model": settings.ai_model,
        "messages": [
            {"role": "system", "content": build_system_prompt(snapshot)},
            *build_conversation_messages(db=db, session_id=session.id),
        ],
        "temperature": 0.4,
    }

    endpoint = f"{settings.ai_base_url.rstrip('/')}/chat/completions"
    async with httpx.AsyncClient(timeout=settings.ai_timeout_seconds) as client:
        response = await client.post(
            endpoint,
            headers={
                "Authorization": f"Bearer {settings.ai_api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        response.raise_for_status()
        response_data = response.json()

    assistant_content = extract_assistant_content(response_data)
    user_messages = [message["content"] for message in payload["messages"] if message["role"] == "user"]
    latest_user_content = user_messages[-1] if user_messages else ""
    return assistant_content, infer_risk_level(latest_user_content, assistant_content)
