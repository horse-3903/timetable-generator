from typing import Literal

from util.google_calendar.api_util import get_service

def get_acl(cal_id: str) -> dict:
    service = get_service()

    rule = service.acl().get(calendarId=cal_id, ruleId="ruleId").execute()

    return rule

def list_acl(cal_id: str) -> dict:
    service = get_service()

    rule = service.acl().list(calendarId=cal_id).execute()

    return rule

def insert_acl(cal_id: str, scope: Literal["default", "user", "group", "domain"], email: str, role: Literal["none", "freeBusyReader", "reader", "writer", "owner"]) -> dict:
    service = get_service()

    body = {
        "role": role,
        "scope": {
            "type": scope,
            "value": email,
        },
    }

    rule = service.acl().insert(calendarId=cal_id, body=body).execute()

    return rule

def delete_acl(cal_id: str, email: str) -> None:
    service = get_service()

    lst = list_acl(cal_id=cal_id)
    lst = lst["items"]

    rule = None

    for it in lst:
        if it["scope"]["value"] == email:
            rule = it
            break

    if not rule:
        raise Exception(f"Rule with email {email} not found")
    
    rule_id = rule["id"]

    service.acl().delete(calendarId=cal_id, ruleId=rule_id).execute()
