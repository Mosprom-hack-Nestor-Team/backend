"""
Basic stats and visit logging endpoints
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from fastapi import APIRouter, Depends, status, HTTPException

from app.api.v1.endpoints.auth import get_current_active_user
from app.models import User
from app.mongodb_models import Spreadsheet, SpreadsheetChange
from app.core.mongodb import MongoDB
from app.core.config import settings


router = APIRouter(prefix="/stats", tags=["stats"])


@router.post("/visit", status_code=status.HTTP_204_NO_CONTENT)
async def log_visit(
    event: str,
    spreadsheet_id: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
):
    event = (event or '').strip().lower()
    if event not in {"dashboard", "spreadsheet_open"}:
        raise HTTPException(status_code=400, detail="Invalid event")
    if MongoDB.client is None:
        raise HTTPException(status_code=500, detail="Mongo is not initialized")
    db = MongoDB.client[settings.MONGODB_DB_NAME]
    await db["visits"].insert_one({
        "event_type": event,
        "user_id": current_user.id,
        "user_email": current_user.email,
        "spreadsheet_id": spreadsheet_id,
        "timestamp": datetime.utcnow(),
    })


@router.get("/summary")
async def stats_summary(
    days: int = 7,
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    # Spreadsheets owned and shared
    owned_count = await Spreadsheet.find(Spreadsheet.owner_id == current_user.id).count()
    shared_count = await Spreadsheet.find(Spreadsheet.permissions.user_email == current_user.email).count()
    total_accessible = owned_count + shared_count

    # Visits
    since = datetime.utcnow() - timedelta(days=max(0, days))
    if MongoDB.client is None:
        raise HTTPException(status_code=500, detail="Mongo is not initialized")
    db = MongoDB.client[settings.MONGODB_DB_NAME]
    total_visits = await db["visits"].count_documents({"user_id": current_user.id})
    dashboard_visits = await db["visits"].count_documents({
        "user_id": current_user.id, "event_type": "dashboard"
    })
    spreadsheet_opens = await db["visits"].count_documents({
        "user_id": current_user.id, "event_type": "spreadsheet_open"
    })
    opens_last_period = await db["visits"].count_documents({
        "user_id": current_user.id,
        "event_type": "spreadsheet_open",
        "timestamp": {"$gte": since},
    })

    return {
        "owned": owned_count,
        "shared": shared_count,
        "total": total_accessible,
        "visits": {
            "total": total_visits,
            "dashboard": dashboard_visits,
            "opens_total": spreadsheet_opens,
            "opens_last_days": opens_last_period,
            "days": days,
        },
    }


@router.get("/spreadsheets/{spreadsheet_id}/history")
async def spreadsheet_history(
    spreadsheet_id: str,
    limit: int = 100,
    days: int = 30,
    current_user: User = Depends(get_current_active_user),
):
    # Check access: owner or in permissions
    spreadsheet = await Spreadsheet.get(spreadsheet_id)
    if not spreadsheet:
        return {"changes": [], "total": 0}
    if spreadsheet.owner_id != current_user.id and all(
        p.user_email != current_user.email for p in spreadsheet.permissions
    ):
        return {"changes": [], "total": 0}

    since = datetime.utcnow() - timedelta(days=max(0, days))
    cursor = SpreadsheetChange.find(
        SpreadsheetChange.spreadsheet_id == str(spreadsheet_id),
        SpreadsheetChange.timestamp >= since,
    ).sort(-SpreadsheetChange.timestamp).limit(max(1, min(limit, 1000)))
    changes = [
        {
            "timestamp": ch.timestamp,
            "user_email": ch.user_email,
            "change_type": ch.change_type,
            "cell_ref": ch.cell_ref,
            "old_value": ch.old_value,
            "new_value": ch.new_value,
            "version": ch.version,
        }
        async for ch in cursor
    ]
    return {"changes": changes, "total": len(changes)}
