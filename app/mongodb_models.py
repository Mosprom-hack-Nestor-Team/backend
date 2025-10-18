"""
MongoDB models for spreadsheets
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from beanie import Document
from pydantic import Field, EmailStr, BaseModel


class PermissionLevel(str, Enum):
    """Permission levels for spreadsheet access"""
    OWNER = "owner"
    EDIT = "edit"
    VIEW = "view"


class CellValue(str, Enum):
    """Cell value types"""
    TEXT = "text"
    NUMBER = "number"
    FORMULA = "formula"
    DATE = "date"
    BOOLEAN = "boolean"


class Cell(BaseModel):
    """Cell data structure"""
    row: int
    col: int
    value: Any = None
    value_type: CellValue = CellValue.TEXT
    formula: Optional[str] = None
    style: Optional[Dict[str, Any]] = None


class SpreadsheetPermission(BaseModel):
    """Permission for a user on a spreadsheet"""
    user_email: EmailStr
    permission_level: PermissionLevel
    granted_at: datetime = Field(default_factory=datetime.utcnow)
    granted_by: int  # user_id from PostgreSQL


class Spreadsheet(Document):
    """
    Spreadsheet document stored in MongoDB
    Links to PostgreSQL User via owner_id
    """
    title: str
    owner_id: int  # References User.id in PostgreSQL
    owner_email: EmailStr  # For easier queries
    
    # Spreadsheet data
    rows: int = 100
    cols: int = 26
    cells: Dict[str, Dict[str, Any]] = Field(default_factory=dict)  # {"row_col": cell_data}
    
    # Permissions - list of users who have access
    permissions: List[SpreadsheetPermission] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_modified_by: Optional[int] = None  # user_id
    
    # Version control for concurrent editing
    version: int = 1
    
    class Settings:
        name = "spreadsheets"
        indexes = [
            "owner_id",
            "owner_email",
            "permissions.user_email",
        ]

    class Config:
        json_schema_extra = {
            "example": {
                "title": "My Spreadsheet",
                "owner_id": 1,
                "owner_email": "user@example.com",
                "rows": 100,
                "cols": 26,
                "cells": {
                    "0_0": {
                        "value": "Hello",
                        "value_type": "text",
                        "style": {"bold": True}
                    }
                },
                "permissions": []
            }
        }


class SpreadsheetChange(Document):
    """
    Track changes for real-time synchronization and conflict resolution
    """
    spreadsheet_id: str  # Spreadsheet._id
    user_id: int
    user_email: EmailStr
    
    # Change details
    change_type: str  # "cell_update", "cell_delete", "row_add", "col_add", etc.
    cell_ref: Optional[str] = None  # "row_col"
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    
    # Versioning
    version: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "spreadsheet_changes"
        indexes = [
            "spreadsheet_id",
            "timestamp",
        ]
