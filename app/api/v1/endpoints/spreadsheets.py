"""
Spreadsheet endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.models import User
from app.api.v1.endpoints.auth import get_current_active_user
from app.services.spreadsheet_service import SpreadsheetService
from app.spreadsheet_schemas import (
    SpreadsheetCreate, SpreadsheetUpdate, SpreadsheetInfo,
    SpreadsheetDetail, SpreadsheetList, ShareSpreadsheet,
    CellUpdate, UpdatePermission
)


router = APIRouter(prefix="/spreadsheets", tags=["spreadsheets"])


@router.post("/", response_model=SpreadsheetInfo, status_code=status.HTTP_201_CREATED)
async def create_spreadsheet(
    spreadsheet_data: SpreadsheetCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Create a new spreadsheet"""
    spreadsheet = await SpreadsheetService.create_spreadsheet(spreadsheet_data, current_user)
    return SpreadsheetInfo(
        id=str(spreadsheet.id),
        title=spreadsheet.title,
        owner_id=spreadsheet.owner_id,
        owner_email=spreadsheet.owner_email,
        rows=spreadsheet.rows,
        cols=spreadsheet.cols,
        created_at=spreadsheet.created_at,
        updated_at=spreadsheet.updated_at,
        version=spreadsheet.version,
        my_permission="owner"
    )


@router.get("/", response_model=SpreadsheetList)
async def get_my_spreadsheets(
    current_user: User = Depends(get_current_active_user)
):
    """Get all spreadsheets accessible by current user"""
    spreadsheets = await SpreadsheetService.get_user_spreadsheets(current_user)
    return SpreadsheetList(
        spreadsheets=spreadsheets,
        total=len(spreadsheets)
    )


@router.get("/{spreadsheet_id}", response_model=SpreadsheetDetail)
async def get_spreadsheet(
    spreadsheet_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get spreadsheet details"""
    return await SpreadsheetService.get_spreadsheet(spreadsheet_id, current_user)


@router.patch("/{spreadsheet_id}", response_model=SpreadsheetInfo)
async def update_spreadsheet(
    spreadsheet_id: str,
    update_data: SpreadsheetUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update spreadsheet metadata"""
    spreadsheet = await SpreadsheetService.update_spreadsheet(
        spreadsheet_id, update_data, current_user
    )
    permission = SpreadsheetService._get_user_permission(spreadsheet, current_user)
    return SpreadsheetInfo(
        id=str(spreadsheet.id),
        title=spreadsheet.title,
        owner_id=spreadsheet.owner_id,
        owner_email=spreadsheet.owner_email,
        rows=spreadsheet.rows,
        cols=spreadsheet.cols,
        created_at=spreadsheet.created_at,
        updated_at=spreadsheet.updated_at,
        version=spreadsheet.version,
        my_permission=permission
    )


@router.delete("/{spreadsheet_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_spreadsheet(
    spreadsheet_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Delete spreadsheet (owner only)"""
    await SpreadsheetService.delete_spreadsheet(spreadsheet_id, current_user)


@router.patch("/{spreadsheet_id}/cells")
async def update_cell(
    spreadsheet_id: str,
    cell_update: CellUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update a single cell"""
    return await SpreadsheetService.update_cell(spreadsheet_id, cell_update, current_user)


@router.post("/{spreadsheet_id}/share", status_code=status.HTTP_200_OK)
async def share_spreadsheet(
    spreadsheet_id: str,
    share_data: ShareSpreadsheet,
    current_user: User = Depends(get_current_active_user)
):
    """Share spreadsheet with another user"""
    await SpreadsheetService.share_spreadsheet(spreadsheet_id, share_data, current_user)
    return {"message": f"Spreadsheet shared with {share_data.user_email}"}


@router.delete("/{spreadsheet_id}/permissions/{user_email}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_permission(
    spreadsheet_id: str,
    user_email: str,
    current_user: User = Depends(get_current_active_user)
):
    """Remove user's access to spreadsheet"""
    await SpreadsheetService.remove_permission(spreadsheet_id, user_email, current_user)
