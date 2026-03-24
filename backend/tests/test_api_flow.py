from fastapi.testclient import TestClient


# 验证后端主闭环接口能够按真实数据顺序完成家庭、宝宝、记录、媒体和提醒流程。
def test_core_api_flow(client: TestClient) -> None:
    family_response = client.post(
        "/api/v1/family",
        json={
            "name": "宝宝成长档案家庭",
            "description": "测试家庭",
            "creator_email": "superowner@example.com",
            "creator_display_name": "SuperOwner",
        },
    )
    assert family_response.status_code == 200
    family_data = family_response.json()["data"]
    family_id = family_data["family_id"]

    family_members_response = client.get(f"/api/v1/family/members?family_id={family_id}")
    assert family_members_response.status_code == 200
    super_owner_member = family_members_response.json()["data"][0]
    super_owner_user_id = super_owner_member["user_id"]

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "superowner@example.com", "invite_code": "demo-code"},
    )
    assert login_response.status_code == 200
    assert login_response.json()["data"]["role"] == "SuperOwner"

    invitation_response = client.post(
        "/api/v1/auth/invitations",
        json={
            "family_id": family_id,
            "invitee_name": "宝宝妈妈",
            "invitee_email": "mother@example.com",
            "role": "Editor",
            "note": "邀请加入家庭",
        },
    )
    assert invitation_response.status_code == 200
    invite_token = invitation_response.json()["data"]["invite_token"]

    accept_invitation_response = client.post(
        "/api/v1/auth/invitations/accept",
        json={"invite_token": invite_token, "display_name": "宝宝妈妈"},
    )
    assert accept_invitation_response.status_code == 200
    assert accept_invitation_response.json()["data"]["role"] == "Editor"

    baby_response = client.post(
        "/api/v1/baby-profile",
        json={
            "family_id": family_id,
            "nickname": "小宝宝",
            "birth_date": "2026-03-12",
            "birth_time": "08:30",
            "gender": "female",
            "birth_place": "上海",
            "birth_height_cm": 50.0,
            "birth_weight_kg": 3.2,
            "note": "出生记录",
        },
    )
    assert baby_response.status_code == 200
    baby_data = baby_response.json()["data"]
    baby_id = baby_data["baby_id"]

    growth_response = client.post(
        "/api/v1/growth",
        json={
            "baby_id": baby_id,
            "record_type": "weight",
            "value": 3.8,
            "unit": "kg",
            "recorded_at": "2026-03-24T10:00:00+08:00",
            "note": "测试新增体重记录",
        },
    )
    assert growth_response.status_code == 200
    assert growth_response.json()["data"]["value"] == 3.8

    media_response = client.post(
        "/api/v1/media",
        json={
            "family_id": family_id,
            "baby_id": baby_id,
            "uploaded_by_user_id": super_owner_user_id,
            "media_type": "image",
            "file_name": "baby-001.jpg",
            "file_url": "https://example.com/baby-001.jpg",
            "thumbnail_url": "https://example.com/baby-001-thumb.jpg",
            "mime_type": "image/jpeg",
            "description": "第一次在家拍照",
            "tags": ["home", "day1"],
            "captured_at": "2026-03-24T10:30:00+08:00",
            "visibility": "family",
        },
    )
    assert media_response.status_code == 200
    assert media_response.json()["data"]["media_type"] == "image"

    reminder_response = client.post(
        "/api/v1/reminder",
        json={
            "family_id": family_id,
            "baby_id": baby_id,
            "created_by_user_id": super_owner_user_id,
            "reminder_type": "missing_record",
            "title": "补一条今天的体重记录",
            "description": "最近 3 天没有新增体重记录",
            "due_at": "2026-03-25T09:00:00+08:00",
            "source": "system",
        },
    )
    assert reminder_response.status_code == 200
    reminder_id = reminder_response.json()["data"]["reminder_id"]

    upcoming_response = client.get(f"/api/v1/reminder/upcoming?family_id={family_id}&baby_id={baby_id}")
    assert upcoming_response.status_code == 200
    assert len(upcoming_response.json()["data"]) == 1

    confirm_response = client.patch(
        f"/api/v1/reminder/{reminder_id}/confirm",
        json={"status": "done"},
    )
    assert confirm_response.status_code == 200
    assert confirm_response.json()["data"]["status"] == "done"
