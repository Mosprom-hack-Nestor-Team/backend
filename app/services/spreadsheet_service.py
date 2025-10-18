"""
Spreadsheet service for managing spreadsheets and permissions
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from beanie import PydanticObjectId
from fastapi import HTTPException, status

from app.mongodb_models import Spreadsheet, SpreadsheetPermission, PermissionLevel, SpreadsheetChange
from app.spreadsheet_schemas import (
    SpreadsheetCreate, SpreadsheetUpdate, SpreadsheetInfo,
    SpreadsheetDetail, ShareSpreadsheet, CellUpdate, PermissionInfo
)
from app.models import User


class SpreadsheetService:
    """Service for spreadsheet operations"""
    
    @staticmethod
    async def create_spreadsheet(
        spreadsheet_data: SpreadsheetCreate,
        user: User
    ) -> Spreadsheet:
        """Create a new spreadsheet"""
        spreadsheet = Spreadsheet(
            title=spreadsheet_data.title,
            owner_id=user.id,
            owner_email=user.email,
            rows=spreadsheet_data.rows,
            cols=spreadsheet_data.cols,
            cells={},
            permissions=[],
        )
        await spreadsheet.insert()
        return spreadsheet
    
    @staticmethod
    async def get_user_spreadsheets(user: User) -> List[SpreadsheetInfo]:
        """Get all spreadsheets accessible by user (owned + shared)"""
        # Find spreadsheets owned by user
        owned = await Spreadsheet.find(
            Spreadsheet.owner_id == user.id
        ).to_list()
        
        # Find spreadsheets shared with user
        shared = await Spreadsheet.find(
            Spreadsheet.permissions.user_email == user.email
        ).to_list()
        
        # Combine and remove duplicates
        all_spreadsheets = {str(s.id): s for s in owned + shared}.values()
        
        # Convert to SpreadsheetInfo
        result = []
        for s in all_spreadsheets:
            my_permission = SpreadsheetService._get_user_permission(s, user)
            result.append(SpreadsheetInfo(
                id=str(s.id),
                title=s.title,
                owner_id=s.owner_id,
                owner_email=s.owner_email,
                rows=s.rows,
                cols=s.cols,
                created_at=s.created_at,
                updated_at=s.updated_at,
                version=s.version,
                my_permission=my_permission
            ))
        
        return sorted(result, key=lambda x: x.updated_at, reverse=True)
    
    @staticmethod
    async def get_spreadsheet(
        spreadsheet_id: str,
        user: User
    ) -> SpreadsheetDetail:
        """Get spreadsheet details with permission check"""
        spreadsheet = await Spreadsheet.get(PydanticObjectId(spreadsheet_id))
        
        if not spreadsheet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Spreadsheet not found"
            )
        
        # Check permissions
        permission = SpreadsheetService._get_user_permission(spreadsheet, user)
        if permission is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this spreadsheet"
            )
        
        # Convert permissions to PermissionInfo
        permissions_info = [
            PermissionInfo(
                user_email=p.user_email,
                permission_level=p.permission_level,
                granted_at=p.granted_at,
                granted_by=p.granted_by
            )
            for p in spreadsheet.permissions
        ]
        
        return SpreadsheetDetail(
            id=str(spreadsheet.id),
            title=spreadsheet.title,
            owner_id=spreadsheet.owner_id,
            owner_email=spreadsheet.owner_email,
            rows=spreadsheet.rows,
            cols=spreadsheet.cols,
            cells=spreadsheet.cells,
            permissions=permissions_info,
            created_at=spreadsheet.created_at,
            updated_at=spreadsheet.updated_at,
            version=spreadsheet.version,
            my_permission=permission
        )
    
    @staticmethod
    async def update_spreadsheet(
        spreadsheet_id: str,
        update_data: SpreadsheetUpdate,
        user: User
    ) -> Spreadsheet:
        """Update spreadsheet metadata"""
        spreadsheet = await Spreadsheet.get(PydanticObjectId(spreadsheet_id))
        
        if not spreadsheet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Spreadsheet not found"
            )
        
        # Only owner or users with EDIT permission can update
        permission = SpreadsheetService._get_user_permission(spreadsheet, user)
        if permission not in [PermissionLevel.OWNER, PermissionLevel.EDIT]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to edit this spreadsheet"
            )
        
        if update_data.title:
            spreadsheet.title = update_data.title
        
        spreadsheet.updated_at = datetime.utcnow()
        spreadsheet.last_modified_by = user.id
        
        await spreadsheet.save()
        return spreadsheet
    
    @staticmethod
    async def delete_spreadsheet(spreadsheet_id: str, user: User) -> bool:
        """Delete spreadsheet (only owner)"""
        spreadsheet = await Spreadsheet.get(PydanticObjectId(spreadsheet_id))
        
        if not spreadsheet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Spreadsheet not found"
            )
        
        # Only owner can delete
        if spreadsheet.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the owner can delete this spreadsheet"
            )
        
        await spreadsheet.delete()
        return True
    
    @staticmethod
    async def update_cell(
        spreadsheet_id: str,
        cell_update: CellUpdate,
        user: User
    ) -> Dict[str, Any]:
        """Update a single cell"""
        spreadsheet = await Spreadsheet.get(PydanticObjectId(spreadsheet_id))
        
        if not spreadsheet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Spreadsheet not found"
            )
        
        # Check edit permission
        permission = SpreadsheetService._get_user_permission(spreadsheet, user)
        if permission not in [PermissionLevel.OWNER, PermissionLevel.EDIT]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to edit this spreadsheet"
            )
        
        # Create cell reference
        cell_ref = f"{cell_update.row}_{cell_update.col}"
        
        # Save old value for change tracking
        old_value = spreadsheet.cells.get(cell_ref)
        
        # Update cell
        spreadsheet.cells[cell_ref] = {
            "value": cell_update.value,
            "value_type": cell_update.value_type,
            "formula": cell_update.formula,
            "style": cell_update.style or {}
        }
        
        # Update metadata
        spreadsheet.updated_at = datetime.utcnow()
        spreadsheet.last_modified_by = user.id
        spreadsheet.version += 1
        
        await spreadsheet.save()
        
        # Track change
        change = SpreadsheetChange(
            spreadsheet_id=str(spreadsheet.id),
            user_id=user.id,
            user_email=user.email,
            change_type="cell_update",
            cell_ref=cell_ref,
            old_value=old_value,
            new_value=spreadsheet.cells[cell_ref],
            version=spreadsheet.version
        )
        await change.insert()
        
        return {
            "cell_ref": cell_ref,
            "value": spreadsheet.cells[cell_ref],
            "version": spreadsheet.version
        }
    
    @staticmethod
    async def share_spreadsheet(
        spreadsheet_id: str,
        share_data: ShareSpreadsheet,
        user: User
    ) -> Spreadsheet:
        """Share spreadsheet with another user"""
        spreadsheet = await Spreadsheet.get(PydanticObjectId(spreadsheet_id))
        
        if not spreadsheet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Spreadsheet not found"
            )
        
        # Only owner can share
        if spreadsheet.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the owner can share this spreadsheet"
            )
        
        # Check if already shared with this user
        for perm in spreadsheet.permissions:
            if perm.user_email == share_data.user_email:
                # Update permission level
                perm.permission_level = share_data.permission_level
                perm.granted_at = datetime.utcnow()
                perm.granted_by = user.id
                await spreadsheet.save()
                return spreadsheet
        
        # Add new permission
        new_permission = SpreadsheetPermission(
            user_email=share_data.user_email,
            permission_level=share_data.permission_level,
            granted_at=datetime.utcnow(),
            granted_by=user.id
        )
        spreadsheet.permissions.append(new_permission)
        await spreadsheet.save()
        
        return spreadsheet
    
    @staticmethod
    async def remove_permission(
        spreadsheet_id: str,
        user_email: str,
        user: User
    ) -> Spreadsheet:
        """Remove user's access to spreadsheet"""
        spreadsheet = await Spreadsheet.get(PydanticObjectId(spreadsheet_id))
        
        if not spreadsheet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Spreadsheet not found"
            )
        
        # Only owner can remove permissions
        if spreadsheet.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the owner can manage permissions"
            )
        
        # Remove permission
        spreadsheet.permissions = [
            p for p in spreadsheet.permissions
            if p.user_email != user_email
        ]
        await spreadsheet.save()
        
        return spreadsheet
    
    @staticmethod
    def _get_user_permission(spreadsheet: Spreadsheet, user: User) -> Optional[PermissionLevel]:
        """Get user's permission level for a spreadsheet"""
        # Owner has full access
        if spreadsheet.owner_id == user.id:
            return PermissionLevel.OWNER
        
        # Check shared permissions
        for perm in spreadsheet.permissions:
            if perm.user_email == user.email:
                return perm.permission_level
        
        return None
