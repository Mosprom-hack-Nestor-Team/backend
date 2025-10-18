"""
Pydantic schemas for spreadsheet API
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field
from app.mongodb_models import PermissionLevel, CellValue


# Cell schemas
class CellData(BaseModel):
    """Cell data"""
    value: Any = None
    value_type: CellValue = CellValue.TEXT
    formula: Optional[str] = None
    style: Optional[Dict[str, Any]] = None


class CellUpdate(BaseModel):
    """Update a single cell"""
    row: int = Field(..., ge=0)
    col: int = Field(..., ge=0)
    value: Any = None
    value_type: CellValue = CellValue.TEXT
    formula: Optional[str] = None
    style: Optional[Dict[str, Any]] = None


class BatchCellUpdate(BaseModel):
    """Update multiple cells at once"""
    cells: List[CellUpdate]


# Permission schemas
class PermissionInfo(BaseModel):
    """Permission information"""
    user_email: EmailStr
    permission_level: PermissionLevel
    granted_at: datetime
    granted_by: int


class ShareSpreadsheet(BaseModel):
    """Share spreadsheet with another user"""
    user_email: EmailStr
    permission_level: PermissionLevel = PermissionLevel.VIEW


class UpdatePermission(BaseModel):
    """Update user permission"""
    permission_level: PermissionLevel


# Spreadsheet schemas
class SpreadsheetCreate(BaseModel):
    """Create new spreadsheet"""
    title: str = Field(..., min_length=1, max_length=200)
    rows: int = Field(default=100, ge=10, le=1000)
    cols: int = Field(default=26, ge=10, le=100)


class SpreadsheetUpdate(BaseModel):
    """Update spreadsheet metadata"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)


class SpreadsheetInfo(BaseModel):
    """Spreadsheet information without cell data"""
    id: str
    title: str
    owner_id: int
    owner_email: EmailStr
    rows: int
    cols: int
    created_at: datetime
    updated_at: datetime
    version: int
    my_permission: PermissionLevel  # Current user's permission level


class SpreadsheetDetail(BaseModel):
    """Full spreadsheet data including cells"""
    id: str
    title: str
    owner_id: int
    owner_email: EmailStr
    rows: int
    cols: int
    cells: Dict[str, Dict[str, Any]]
    permissions: List[PermissionInfo]
    created_at: datetime
    updated_at: datetime
    version: int
    my_permission: PermissionLevel


class SpreadsheetList(BaseModel):
    """List of spreadsheets"""
    spreadsheets: List[SpreadsheetInfo]
    total: int


# WebSocket messages
class WSMessage(BaseModel):
    """WebSocket message base"""
    type: str
    spreadsheet_id: str


class WSCellUpdate(WSMessage):
    """Cell update via WebSocket"""
    type: str = "cell_update"
    cell: CellUpdate
    user_email: EmailStr
    version: int


class WSUserJoined(WSMessage):
    """User joined spreadsheet"""
    type: str = "user_joined"
    user_email: EmailStr


class WSUserLeft(WSMessage):
    """User left spreadsheet"""
    type: str = "user_left"
    user_email: EmailStr


class WSError(WSMessage):
    """Error message"""
    type: str = "error"
    message: str


class WSVersionConflict(WSMessage):
    """Version conflict detected"""
    type: str = "version_conflict"
    current_version: int
    your_version: int
