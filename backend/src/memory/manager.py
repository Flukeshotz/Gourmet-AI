import sqlite3
import logging
from typing import Optional
from pathlib import Path
from src.config import Config

class MemoryManager:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            self.db_path = Config.DATA_DIR / "app.db"
        else:
            self.db_path = Path(db_path)
            
        self._init_db()
        
    def _init_db(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_feedback (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        trace_id TEXT NOT NULL,
                        restaurant_name TEXT NOT NULL,
                        cuisine TEXT,
                        budget_tier TEXT,
                        is_positive BOOLEAN NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()
        except Exception as e:
            logging.error(f"Failed to initialize Memory DB: {e}")

    def record_feedback(self, session_id: str, trace_id: str, restaurant_name: str, cuisine: str, budget_tier: str, is_positive: bool):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO user_feedback (session_id, trace_id, restaurant_name, cuisine, budget_tier, is_positive)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (session_id, trace_id, restaurant_name, cuisine, budget_tier, is_positive))
                conn.commit()
                logging.info(f"Feedback recorded for {session_id}: {restaurant_name} ({'👍' if is_positive else '👎'})")
        except Exception as e:
            logging.error(f"Failed to record feedback: {e}")

    def get_user_profile(self, session_id: str) -> str:
        if not session_id:
            return ""
            
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get the last 10 positive feedbacks for this session
                cursor.execute('''
                    SELECT cuisine, budget_tier 
                    FROM user_feedback 
                    WHERE session_id = ? AND is_positive = 1
                    ORDER BY timestamp DESC
                    LIMIT 10
                ''', (session_id,))
                
                rows = cursor.fetchall()
                if not rows:
                    return ""
                
                cuisines = [r[0] for r in rows if r[0]]
                budgets = [r[1] for r in rows if r[1]]
                
                cuisine_counts = {c: cuisines.count(c) for c in set(cuisines)}
                budget_counts = {b: budgets.count(b) for b in set(budgets)}
                
                top_cuisines = sorted(cuisine_counts, key=cuisine_counts.get, reverse=True)[:2]
                top_budgets = sorted(budget_counts, key=budget_counts.get, reverse=True)[:1]
                
                profile_parts = []
                if top_cuisines:
                    profile_parts.append(f"shows a strong affinity for {', '.join(top_cuisines)} cuisine")
                if top_budgets:
                    profile_parts.append(f"frequently upvotes {top_budgets[0]} budget options")
                    
                if profile_parts:
                    return f"[User Profile Memory] The user {', and '.join(profile_parts)}."
                return ""
        except Exception as e:
            logging.error(f"Failed to get user profile: {e}")
            return ""
