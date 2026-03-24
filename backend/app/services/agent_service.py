from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone

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


@dataclass(frozen=True)
class SummaryContextSnapshot:
    baby_name: str
    birth_date: str
    gender: str
    age_days: int
    age_months: int
    period_start: date
    period_end: date
    growth_records: list[str]
    media_assets: list[str]
    reminders: list[str]
    vaccine_updates: list[str]


# 计算给定日期的周报或月报统计范围。
def build_summary_period(summary_type: str, anchor_date: date | None) -> tuple[date, date]:
    target_date = anchor_date or datetime.now().date()
    if summary_type == "weekly":
        period_start = target_date - timedelta(days=target_date.weekday())
        period_end = period_start + timedelta(days=6)
        return period_start, period_end
    if summary_type == "monthly":
        period_start = target_date.replace(day=1)
        if period_start.month == 12:
            next_month = period_start.replace(year=period_start.year + 1, month=1, day=1)
        else:
            next_month = period_start.replace(month=period_start.month + 1, day=1)
        period_end = next_month - timedelta(days=1)
        return period_start, period_end
    raise ValueError(f"Unsupported summary type: {summary_type}")


# 将日期范围转换为数据库查询使用的闭开区间时间边界。
def build_datetime_bounds(period_start: date, period_end: date) -> tuple[datetime, datetime]:
    start_datetime = datetime.combine(period_start, time.min, tzinfo=timezone.utc)
    end_datetime = datetime.combine(period_end + timedelta(days=1), time.min, tzinfo=timezone.utc)
    return start_datetime, end_datetime


# 生成宝宝近期上下文快照，供问答时使用真实档案数据。
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


# 生成指定时间范围内的成长总结上下文，供周报和月报能力复用。
def build_summary_context_snapshot(
    db: Session,
    family_id: str,
    baby: Baby,
    period_start: date,
    period_end: date,
) -> SummaryContextSnapshot:
    age_days = max((datetime.now().date() - baby.birth_date).days, 0)
    start_datetime, end_datetime = build_datetime_bounds(period_start=period_start, period_end=period_end)

    growth_records = db.scalars(
        select(GrowthRecord)
        .where(
            GrowthRecord.baby_id == baby.id,
            GrowthRecord.recorded_at >= start_datetime,
            GrowthRecord.recorded_at < end_datetime,
        )
        .order_by(GrowthRecord.recorded_at.asc())
        .limit(20)
    ).all()
    media_assets = db.scalars(
        select(MediaAsset)
        .where(
            MediaAsset.family_id == family_id,
            MediaAsset.baby_id == baby.id,
            MediaAsset.captured_at >= start_datetime,
            MediaAsset.captured_at < end_datetime,
        )
        .order_by(MediaAsset.captured_at.asc())
        .limit(20)
    ).all()
    reminders = db.scalars(
        select(Reminder)
        .where(
            Reminder.family_id == family_id,
            Reminder.baby_id == baby.id,
            Reminder.due_at >= start_datetime,
            Reminder.due_at < end_datetime,
        )
        .order_by(Reminder.due_at.asc())
        .limit(20)
    ).all()
    vaccine_plans = db.scalars(
        select(VaccinePlan)
        .where(
            VaccinePlan.family_id == family_id,
            VaccinePlan.baby_id == baby.id,
            VaccinePlan.scheduled_date >= period_start,
            VaccinePlan.scheduled_date <= period_end,
        )
        .order_by(VaccinePlan.scheduled_date.asc())
        .limit(20)
    ).all()
    vaccine_records = db.scalars(
        select(VaccineRecord)
        .where(
            VaccineRecord.family_id == family_id,
            VaccineRecord.baby_id == baby.id,
            VaccineRecord.administered_date >= period_start,
            VaccineRecord.administered_date <= period_end,
        )
        .order_by(VaccineRecord.administered_date.asc())
        .limit(20)
    ).all()

    return SummaryContextSnapshot(
        baby_name=baby.nickname,
        birth_date=baby.birth_date.isoformat(),
        gender=baby.gender,
        age_days=age_days,
        age_months=age_days // 30,
        period_start=period_start,
        period_end=period_end,
        growth_records=[
            f"{record.record_type}: {record.value}{record.unit} at {record.recorded_at.isoformat()}"
            + (f" note={record.note}" if record.note else "")
            for record in growth_records
        ],
        media_assets=[
            f"{asset.media_type}: {asset.file_name} at {asset.captured_at.isoformat()}"
            + (f" desc={asset.description}" if asset.description else "")
            + (f" tags={asset.tags}" if asset.tags else "")
            for asset in media_assets
        ],
        reminders=[
            f"{reminder.reminder_type}: {reminder.title} at {reminder.due_at.isoformat()} status={reminder.status}"
            + (f" desc={reminder.description}" if reminder.description else "")
            for reminder in reminders
        ],
        vaccine_updates=[
            f"plan {plan.vaccine_name} {plan.dose_label} on {plan.scheduled_date.isoformat()} status={plan.status}"
            for plan in vaccine_plans
        ]
        + [
            f"record on {record.administered_date.isoformat()} status={record.status} provider={record.provider or 'unknown'}"
            for record in vaccine_records
        ],
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


# 将总结期内的数据整理为模型可直接生成周报或月报的文本块。
def build_summary_context_block(snapshot: SummaryContextSnapshot) -> str:
    sections = [
        f"宝宝昵称: {snapshot.baby_name}",
        f"出生日期: {snapshot.birth_date}",
        f"性别: {snapshot.gender}",
        f"日龄: {snapshot.age_days}",
        f"月龄: {snapshot.age_months}",
        f"统计范围: {snapshot.period_start.isoformat()} 到 {snapshot.period_end.isoformat()}",
        "本期成长记录:",
        *(snapshot.growth_records or ["本期暂无成长记录"]),
        "本期照片和视频:",
        *(snapshot.media_assets or ["本期暂无照片或视频"]),
        "本期提醒和待办:",
        *(snapshot.reminders or ["本期暂无提醒"]),
        "本期疫苗动态:",
        *(snapshot.vaccine_updates or ["本期暂无疫苗计划或接种记录"]),
    ]
    return "\n".join(sections)


# 构造问答系统提示词，约束助手围绕家庭档案提供建议且避免医疗诊断。
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


# 构造成长总结提示词，要求输出固定结构，便于保存成总结卡片。
def build_summary_prompt(summary_type: str, snapshot: SummaryContextSnapshot) -> str:
    summary_label = "周报" if summary_type == "weekly" else "月报"
    context_block = build_summary_context_block(snapshot)
    return (
        f"请基于以下真实档案内容，为宝宝生成一份{summary_label}成长总结。"
        "语气要温暖、克制、具体，不要编造未提供的信息，不要做医疗诊断。"
        "如果本期记录较少，要直接说明信息有限。"
        "请严格使用以下格式输出：\n"
        "标题：一句适合作为总结卡片标题的话\n"
        "总结：一段 80 到 180 字的总结\n"
        "关键点：\n"
        "- 第一条关键变化或亮点\n"
        "- 第二条关键变化或亮点\n"
        "- 第三条下阶段建议关注点\n\n"
        f"本期档案内容：\n{context_block}"
    )


# 调用百炼兼容接口并返回助手文本。
async def request_model_completion(messages: list[dict[str, str]]) -> str:
    if not settings.ai_api_key:
        raise RuntimeError("AI API key is not configured")

    endpoint = f"{settings.ai_base_url.rstrip('/')}/chat/completions"
    payload = {
        "model": settings.ai_model,
        "messages": messages,
        "temperature": 0.4,
    }

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

    return extract_assistant_content(response_data)


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


# 解析成长总结文本，拆出标题、总结正文和关键点列表。
def parse_growth_summary(raw_content: str, summary_type: str) -> tuple[str, str, list[str]]:
    title = ""
    summary_lines: list[str] = []
    key_points: list[str] = []
    current_section = ""

    for raw_line in raw_content.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("标题"):
            title = line.split("：", 1)[-1].split(":", 1)[-1].strip()
            current_section = "title"
            continue
        if line.startswith("总结"):
            summary_value = line.split("：", 1)[-1].split(":", 1)[-1].strip()
            if summary_value:
                summary_lines.append(summary_value)
            current_section = "summary"
            continue
        if line.startswith("关键点"):
            current_section = "key_points"
            continue
        if line.startswith("-") or line.startswith("•"):
            key_point = line[1:].strip()
            if key_point:
                key_points.append(key_point)
            current_section = "key_points"
            continue
        if current_section == "summary":
            summary_lines.append(line)
        elif current_section == "key_points":
            key_points.append(line)

    summary_content = "\n".join(summary_lines).strip() or raw_content.strip()
    if not title:
        summary_label = "本周成长总结" if summary_type == "weekly" else "本月成长总结"
        title = summary_label
    if not key_points:
        key_points = [segment.strip() for segment in summary_content.split("。") if segment.strip()][:3]
    return title, summary_content, key_points[:5]


# 调用阿里百炼兼容接口生成真实问答回复。
async def generate_agent_reply(db: Session, session: AgentSession, baby: Baby) -> tuple[str, str]:
    snapshot = build_agent_context_snapshot(db=db, family_id=session.family_id, baby=baby)
    assistant_content = await request_model_completion(
        [
            {"role": "system", "content": build_system_prompt(snapshot)},
            *build_conversation_messages(db=db, session_id=session.id),
        ]
    )
    conversation_messages = build_conversation_messages(db=db, session_id=session.id)
    latest_user_content = conversation_messages[-1]["content"] if conversation_messages else ""
    return assistant_content, infer_risk_level(latest_user_content, assistant_content)


# 调用阿里百炼兼容接口生成周报或月报总结。
async def generate_growth_summary(
    db: Session,
    family_id: str,
    baby: Baby,
    summary_type: str,
    anchor_date: date | None,
) -> tuple[date, date, str, str, list[str]]:
    period_start, period_end = build_summary_period(summary_type=summary_type, anchor_date=anchor_date)
    snapshot = build_summary_context_snapshot(
        db=db,
        family_id=family_id,
        baby=baby,
        period_start=period_start,
        period_end=period_end,
    )
    raw_summary = await request_model_completion(
        [
            {
                "role": "system",
                "content": "你是一个家庭宝宝成长档案总结助手，只能基于用户提供的档案内容生成中文总结。",
            },
            {
                "role": "user",
                "content": build_summary_prompt(summary_type=summary_type, snapshot=snapshot),
            },
        ]
    )
    title, content, key_points = parse_growth_summary(raw_content=raw_summary, summary_type=summary_type)
    return period_start, period_end, title, content, key_points

@dataclass(frozen=True)
class RecordSuggestionCandidate:
    kind: str
    title: str
    content: str
    reason: str
    priority: str


# 根据当前月龄返回一条更贴近阶段特征的记录建议。
def build_age_based_candidate(age_months: int) -> RecordSuggestionCandidate:
    if age_months <= 2:
        return RecordSuggestionCandidate(
            kind="age_based_prompt",
            title="记录今天的睡眠和喂养情况",
            content="这个阶段适合补一条睡眠、喂养或体重变化，后面看趋势会更有价值。",
            reason="低月龄阶段变化快，基础记录最有参考意义。",
            priority="medium",
        )
    if age_months <= 5:
        return RecordSuggestionCandidate(
            kind="age_based_prompt",
            title="关注一下抬头和翻身尝试",
            content="这个阶段可以多记录抬头、追视、翻身尝试或和家人的互动表现。",
            reason="这是这个月龄常见的发育观察点。",
            priority="medium",
        )
    if age_months <= 8:
        return RecordSuggestionCandidate(
            kind="age_based_prompt",
            title="记录辅食和坐立表现",
            content="可以补一条辅食接受度、独坐稳定性或翻身变化，方便后面回看阶段成长。",
            reason="这个阶段往往会出现饮食和动作能力的新变化。",
            priority="medium",
        )
    if age_months <= 12:
        return RecordSuggestionCandidate(
            kind="age_based_prompt",
            title="记录爬行和发声互动",
            content="这个阶段值得关注爬行、扶站、叫声变化或和家人的互动反应。",
            reason="接近一岁时，动作和语言互动通常更明显。",
            priority="medium",
        )
    return RecordSuggestionCandidate(
        kind="age_based_prompt",
        title="记录今天的新互动或新动作",
        content="可以补一条新的动作、发音、饮食偏好或出门小故事，让档案更完整。",
        reason="这个阶段的成长更适合通过日常片段持续积累。",
        priority="low",
    )


# 基于当前宝宝档案和最近记录生成原始记录引导建议。
def build_record_guidance_candidates(db: Session, family_id: str, baby: Baby) -> list[RecordSuggestionCandidate]:
    now = datetime.now(timezone.utc)
    candidates: list[RecordSuggestionCandidate] = []

    latest_growth = db.scalars(
        select(GrowthRecord)
        .where(GrowthRecord.baby_id == baby.id)
        .order_by(GrowthRecord.recorded_at.desc())
        .limit(1)
    ).first()
    if latest_growth is None:
        candidates.append(
            RecordSuggestionCandidate(
                kind="missing_growth_record",
                title="先补一条成长记录",
                content="现在还没有宝宝的成长记录，可以先从体重、睡眠或喂养情况开始。",
                reason="成长趋势判断依赖最基础的原始记录。",
                priority="high",
            )
        )
    else:
        last_growth_at = latest_growth.recorded_at
        if last_growth_at.tzinfo is None:
            last_growth_at = last_growth_at.replace(tzinfo=timezone.utc)
        days_since_growth = max((now - last_growth_at).days, 0)
        if days_since_growth >= 3:
            candidates.append(
                RecordSuggestionCandidate(
                    kind="missing_growth_record",
                    title="补一条最近的成长记录",
                    content=f"最近已经 {days_since_growth} 天没有新的成长记录了，可以补一条体重、睡眠或喂养情况。",
                    reason="连续缺少近期记录会影响趋势解读。",
                    priority="high" if days_since_growth >= 7 else "medium",
                )
            )

    recent_media_assets = db.scalars(
        select(MediaAsset)
        .where(MediaAsset.family_id == family_id, MediaAsset.baby_id == baby.id)
        .order_by(MediaAsset.captured_at.desc())
        .limit(8)
    ).all()
    missing_description_count = sum(1 for asset in recent_media_assets if not (asset.description or "").strip())
    if missing_description_count > 0:
        candidates.append(
            RecordSuggestionCandidate(
                kind="missing_media_description",
                title="给最近的照片补一句话",
                content=f"最近有 {missing_description_count} 张照片或视频还没有描述，补一句场景说明会让回忆更完整。",
                reason="媒体素材如果没有描述，后面回看会更难想起当时发生了什么。",
                priority="medium",
            )
        )

    upcoming_reminder = db.scalars(
        select(Reminder)
        .where(Reminder.family_id == family_id, Reminder.baby_id == baby.id, Reminder.status == "pending")
        .order_by(Reminder.due_at.asc())
        .limit(1)
    ).first()
    if upcoming_reminder is not None:
        due_at = upcoming_reminder.due_at
        if due_at.tzinfo is None:
            due_at = due_at.replace(tzinfo=timezone.utc)
        days_until_due = (due_at.date() - now.date()).days
        candidates.append(
            RecordSuggestionCandidate(
                kind="pending_reminder",
                title="留意一下最近的提醒事项",
                content=f"最近有一条待处理提醒：{upcoming_reminder.title}。如果方便，可以顺手补上相关记录。",
                reason="及时处理提醒能让成长档案和后续总结更完整。",
                priority="high" if days_until_due <= 1 else "medium",
            )
        )

    candidates.append(build_age_based_candidate(age_months=max((datetime.now().date() - baby.birth_date).days, 0) // 30))
    return candidates[:3]


# 构造记录引导提示词，让模型在不改变事实的前提下润色建议文案。
def build_record_suggestion_prompt(snapshot: AgentContextSnapshot, candidates: list[RecordSuggestionCandidate]) -> str:
    draft_lines = []
    for index, candidate in enumerate(candidates, start=1):
        draft_lines.extend(
            [
                f"建议{index}标题：{candidate.title}",
                f"建议{index}内容：{candidate.content}",
                f"建议{index}原因：{candidate.reason}",
                f"建议{index}优先级：{candidate.priority}",
            ]
        )
    return (
        "请把下面这些宝宝成长记录建议草稿润色成适合首页展示的中文卡片。"
        "不要改变事实，不要新增不存在的信息，不要做医疗诊断。"
        "请严格按照下面格式输出，每条建议之间用 --- 分隔：\n"
        "标题：...\n内容：...\n原因：...\n优先级：high/medium/low\n---\n"
        f"宝宝上下文：\n{build_context_block(snapshot)}\n\n"
        f"建议草稿：\n{'\n'.join(draft_lines)}"
    )


# 解析模型返回的记录建议；如果格式不稳定，则回退到原始规则建议。
def parse_record_suggestions(
    raw_content: str,
    fallback_candidates: list[RecordSuggestionCandidate],
) -> list[RecordSuggestionCandidate]:
    blocks = [block.strip() for block in raw_content.split("---") if block.strip()]
    parsed_candidates: list[RecordSuggestionCandidate] = []

    for index, block in enumerate(blocks):
        title = ""
        content = ""
        reason = ""
        priority = fallback_candidates[min(index, len(fallback_candidates) - 1)].priority
        for raw_line in block.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith("标题"):
                title = line.split("：", 1)[-1].split(":", 1)[-1].strip()
            elif line.startswith("内容"):
                content = line.split("：", 1)[-1].split(":", 1)[-1].strip()
            elif line.startswith("原因"):
                reason = line.split("：", 1)[-1].split(":", 1)[-1].strip()
            elif line.startswith("优先级"):
                priority = line.split("：", 1)[-1].split(":", 1)[-1].strip().lower()
        if title and content and reason and priority in {"high", "medium", "low"}:
            fallback = fallback_candidates[min(index, len(fallback_candidates) - 1)]
            parsed_candidates.append(
                RecordSuggestionCandidate(
                    kind=fallback.kind,
                    title=title,
                    content=content,
                    reason=reason,
                    priority=priority,
                )
            )

    if len(parsed_candidates) != len(fallback_candidates):
        return fallback_candidates
    return parsed_candidates


# 生成记录引导建议，优先返回模型润色结果，失败时回退到规则建议。
async def generate_record_suggestions(db: Session, family_id: str, baby: Baby) -> list[RecordSuggestionCandidate]:
    fallback_candidates = build_record_guidance_candidates(db=db, family_id=family_id, baby=baby)
    if not fallback_candidates:
        return [build_age_based_candidate(age_months=max((datetime.now().date() - baby.birth_date).days, 0) // 30)]

    if not settings.ai_api_key:
        return fallback_candidates

    snapshot = build_agent_context_snapshot(db=db, family_id=family_id, baby=baby)
    try:
        raw_content = await request_model_completion(
            [
                {
                    "role": "system",
                    "content": "你是一个宝宝成长档案记录引导助手，只能基于提供的建议草稿做中文润色。",
                },
                {
                    "role": "user",
                    "content": build_record_suggestion_prompt(snapshot=snapshot, candidates=fallback_candidates),
                },
            ]
        )
    except Exception:
        return fallback_candidates

    return parse_record_suggestions(raw_content=raw_content, fallback_candidates=fallback_candidates)
