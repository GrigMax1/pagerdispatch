import aiosqlite
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

class Database:
    """Asynchronous SQLite database manager."""
    
    DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dispatch.db')
    SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.sql')
    
    def __init__(self):
        self.connection: Optional[aiosqlite.Connection] = None
    
    async def initialize(self) -> None:
        """Initialize the database connection and schema."""
        self.connection = await aiosqlite.connect(self.DB_PATH)
        self.connection.row_factory = aiosqlite.Row
        
        with open(self.SCHEMA_PATH, 'r') as f:
            schema = f.read()
        
        await self.connection.executescript(schema)
        await self.connection.commit()
    
    async def close(self) -> None:
        """Close the database connection."""
        if self.connection:
            await self.connection.close()
    
    async def execute(self, query: str, params: tuple = ()) -> aiosqlite.Cursor:
        """Execute a query and return cursor."""
        return await self.connection.execute(query, params)
    
    async def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """Fetch a single row."""
        cursor = await self.execute(query, params)
        row = await cursor.fetchone()
        await cursor.close()
        return dict(row) if row else None
    
    async def fetch_all(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Fetch all rows."""
        cursor = await self.execute(query, params)
        rows = await cursor.fetchall()
        await cursor.close()
        return [dict(row) for row in rows]
    
    async def commit(self) -> None:
        """Commit changes to database."""
        await self.connection.commit()
    
    # Dispatch Management
    
    async def get_next_dispatch_number(self) -> str:
        """Get the next dispatch number."""
        result = await self.fetch_one(
            'SELECT COUNT(*) as count FROM dispatches WHERE status = "Active" OR status = "Closed"'
        )
        next_num = (result['count'] if result else 0) + 1
        return f"#{next_num:04d}"
    
    async def create_dispatch(
        self,
        dispatch_number: str,
        category: str,
        title: str,
        location: str,
        situation: str,
        created_by: str,
        swat_required: bool,
        detectives_required: bool,
        traffic_required: bool,
        message_id: int
    ) -> int:
        """Create a new dispatch."""
        cursor = await self.execute(
            '''INSERT INTO dispatches (
                dispatch_number, category, title, location, situation,
                created_by, swat_required, detectives_required, traffic_required, message_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                dispatch_number, category, title, location, situation,
                created_by, swat_required, detectives_required, traffic_required, message_id
            )
        )
        await self.commit()
        return cursor.lastrowid
    
    async def get_dispatch(self, dispatch_id: int) -> Optional[Dict[str, Any]]:
        """Get dispatch by ID."""
        return await self.fetch_one(
            'SELECT * FROM dispatches WHERE dispatch_id = ?',
            (dispatch_id,)
        )
    
    async def get_dispatch_by_number(self, dispatch_number: str) -> Optional[Dict[str, Any]]:
        """Get dispatch by dispatch number."""
        return await self.fetch_one(
            'SELECT * FROM dispatches WHERE dispatch_number = ?',
            (dispatch_number,)
        )
    
    async def get_dispatch_by_message_id(self, message_id: int) -> Optional[Dict[str, Any]]:
        """Get dispatch by Discord message ID."""
        return await self.fetch_one(
            'SELECT * FROM dispatches WHERE message_id = ?',
            (message_id,)
        )
    
    async def get_active_dispatches(self) -> List[Dict[str, Any]]:
        """Get all active dispatches."""
        return await self.fetch_all(
            'SELECT * FROM dispatches WHERE status = "Active" ORDER BY created_at DESC'
        )
    
    async def update_dispatch_status(self, dispatch_id: int, status: str, closed_by: Optional[str] = None) -> None:
        """Update dispatch status."""
        if status == 'Closed':
            await self.execute(
                'UPDATE dispatches SET status = ?, closed_at = ?, closed_by = ? WHERE dispatch_id = ?',
                (status, datetime.now(), closed_by, dispatch_id)
            )
        else:
            await self.execute(
                'UPDATE dispatches SET status = ? WHERE dispatch_id = ?',
                (status, dispatch_id)
            )
        await self.commit()
    
    # Officer Response Tracking
    
    async def add_officer_response(
        self,
        dispatch_id: int,
        user_id: int,
        user_name: str,
        status: str
    ) -> None:
        """Add or update officer response."""
        existing = await self.fetch_one(
            'SELECT response_id FROM officer_responses WHERE dispatch_id = ? AND user_id = ?',
            (dispatch_id, user_id)
        )
        
        if existing:
            await self.execute(
                'UPDATE officer_responses SET status = ?, timestamp = ? WHERE dispatch_id = ? AND user_id = ?',
                (status, datetime.now(), dispatch_id, user_id)
            )
        else:
            await self.execute(
                '''INSERT INTO officer_responses (dispatch_id, user_id, user_name, status)
                   VALUES (?, ?, ?, ?)''',
                (dispatch_id, user_id, user_name, status)
            )
        await self.commit()
    
    async def remove_officer_response(self, dispatch_id: int, user_id: int) -> None:
        """Remove officer response (when clicking same status again)."""
        await self.execute(
            'DELETE FROM officer_responses WHERE dispatch_id = ? AND user_id = ?',
            (dispatch_id, user_id)
        )
        await self.commit()
    
    async def get_officer_responses(self, dispatch_id: int) -> List[Dict[str, Any]]:
        """Get all officer responses for a dispatch."""
        return await self.fetch_all(
            'SELECT * FROM officer_responses WHERE dispatch_id = ? ORDER BY timestamp ASC',
            (dispatch_id,)
        )
    
    async def get_officers_by_status(self, dispatch_id: int, status: str) -> List[Dict[str, Any]]:
        """Get officers with a specific status on a dispatch."""
        return await self.fetch_all(
            'SELECT * FROM officer_responses WHERE dispatch_id = ? AND status = ? ORDER BY user_name ASC',
            (dispatch_id, status)
        )
    
    # Dispatch Logging
    
    async def log_action(
        self,
        dispatch_id: int,
        action: str,
        user_name: str,
        user_id: Optional[int] = None,
        details: Optional[str] = None
    ) -> None:
        """Log an action to dispatch_logs."""
        await self.execute(
            '''INSERT INTO dispatch_logs (dispatch_id, action, user_name, user_id, details)
               VALUES (?, ?, ?, ?, ?)''',
            (dispatch_id, action, user_name, user_id, details)
        )
        await self.commit()
    
    async def get_dispatch_logs(self, dispatch_id: int) -> List[Dict[str, Any]]:
        """Get all logs for a dispatch."""
        return await self.fetch_all(
            'SELECT * FROM dispatch_logs WHERE dispatch_id = ? ORDER BY timestamp ASC',
            (dispatch_id,)
        )
    
    # Bot Settings
    
    async def set_setting(self, key: str, value: str) -> None:
        """Set a bot setting."""
        existing = await self.fetch_one(
            'SELECT setting_key FROM bot_settings WHERE setting_key = ?',
            (key,)
        )
        
        if existing:
            await self.execute(
                'UPDATE bot_settings SET setting_value = ?, updated_at = ? WHERE setting_key = ?',
                (value, datetime.now(), key)
            )
        else:
            await self.execute(
                'INSERT INTO bot_settings (setting_key, setting_value) VALUES (?, ?)',
                (key, value)
            )
        await self.commit()
    
    async def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a bot setting."""
        result = await self.fetch_one(
            'SELECT setting_value FROM bot_settings WHERE setting_key = ?',
            (key,)
        )
        return result['setting_value'] if result else default
    
    async def get_all_settings(self) -> Dict[str, str]:
        """Get all bot settings."""
        results = await self.fetch_all('SELECT setting_key, setting_value FROM bot_settings')
        return {row['setting_key']: row['setting_value'] for row in results}
