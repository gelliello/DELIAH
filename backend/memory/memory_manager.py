import aiosqlite
import json
from pathlib import Path
from typing import Optional
from datetime import datetime


DB_PATH = Path(__file__).parent / "deliah_memory.db"


class MemoryManager:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self._initialized = False

    async def initialize(self):
        if self._initialized:
            return
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    category TEXT DEFAULT 'general',
                    importance INTEGER DEFAULT 5,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TIMESTAMP
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    session_id TEXT
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()
        self._initialized = True

    async def store(
        self, key: str, value: str, category: str = "general", importance: int = 5
    ):
        await self.initialize()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT OR REPLACE INTO memory (key, value, category, importance, updated_at)
                   VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)""",
                (key, value, category, importance),
            )
            await db.commit()

    async def retrieve(self, key: str) -> Optional[str]:
        await self.initialize()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """UPDATE memory SET access_count = access_count + 1,
                   last_accessed = CURRENT_TIMESTAMP WHERE key = ?""",
                (key,),
            )
            await db.commit()
            cursor = await db.execute(
                "SELECT value FROM memory WHERE key = ?", (key,)
            )
            row = await cursor.fetchone()
            return row[0] if row else None

    async def search(
        self, query: str, category: Optional[str] = None, limit: int = 10
    ) -> list[dict]:
        await self.initialize()
        async with aiosqlite.connect(self.db_path) as db:
            if category:
                cursor = await db.execute(
                    """SELECT key, value, category, importance FROM memory
                       WHERE category = ? AND (value LIKE ? OR key LIKE ?)
                       ORDER BY importance DESC, access_count DESC LIMIT ?""",
                    (category, f"%{query}%", f"%{query}%", limit),
                )
            else:
                cursor = await db.execute(
                    """SELECT key, value, category, importance FROM memory
                       WHERE value LIKE ? OR key LIKE ?
                       ORDER BY importance DESC, access_count DESC LIMIT ?""",
                    (f"%{query}%", f"%{query}%", limit),
                )
            rows = await cursor.fetchall()
            return [
                {"key": r[0], "value": r[1], "category": r[2], "importance": r[3]}
                for r in rows
            ]

    async def get_by_category(self, category: str) -> list[dict]:
        await self.initialize()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """SELECT key, value, category, importance, created_at
                   FROM memory WHERE category = ?
                   ORDER BY importance DESC""",
                (category,),
            )
            rows = await cursor.fetchall()
            return [
                {
                    "key": r[0], "value": r[1], "category": r[2],
                    "importance": r[3], "created_at": r[4],
                }
                for r in rows
            ]

    async def get_all(self) -> list[dict]:
        await self.initialize()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """SELECT key, value, category, importance, created_at
                   FROM memory ORDER BY importance DESC"""
            )
            rows = await cursor.fetchall()
            return [
                {
                    "key": r[0], "value": r[1], "category": r[2],
                    "importance": r[3], "created_at": r[4],
                }
                for r in rows
            ]

    async def delete(self, key: str) -> bool:
        await self.initialize()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("DELETE FROM memory WHERE key = ?", (key,))
            await db.commit()
            return cursor.rowcount > 0

    async def store_conversation(
        self, role: str, content: str, session_id: str = "default"
    ):
        await self.initialize()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT INTO conversations (role, content, session_id)
                   VALUES (?, ?, ?)""",
                (role, content, session_id),
            )
            await db.commit()

    async def get_conversation_history(
        self, session_id: str = "default", limit: int = 50
    ) -> list[dict]:
        await self.initialize()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """SELECT role, content, timestamp FROM conversations
                   WHERE session_id = ?
                   ORDER BY timestamp DESC LIMIT ?""",
                (session_id, limit),
            )
            rows = await cursor.fetchall()
            return [
                {"role": r[0], "content": r[1], "timestamp": r[2]}
                for r in reversed(rows)
            ]

    async def set_preference(self, key: str, value: str):
        await self.initialize()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT OR REPLACE INTO preferences (key, value, updated_at)
                   VALUES (?, ?, CURRENT_TIMESTAMP)""",
                (key, value),
            )
            await db.commit()

    async def get_preference(self, key: str) -> Optional[str]:
        await self.initialize()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT value FROM preferences WHERE key = ?", (key,)
            )
            row = await cursor.fetchone()
            return row[0] if row else None
