import sqlite3
import json
from datetime import datetime
from config import CLASSES, EQUIPMENT_SLOTS

DB_PATH = "maplestory.db"

def init_db():
    """Initialize database schema"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            class TEXT NOT NULL,
            level INTEGER DEFAULT 1,
            exp INTEGER DEFAULT 0,
            total_exp INTEGER DEFAULT 0,
            hp INTEGER,
            mp INTEGER,
            meso INTEGER DEFAULT 0,
            nx INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_daily_reset TIMESTAMP
        )
    """)
    
    # Equipment table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS equipment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            slot TEXT NOT NULL,
            name TEXT NOT NULL,
            rarity TEXT DEFAULT 'common',
            stars INTEGER DEFAULT 0,
            atk INTEGER DEFAULT 0,
            def INTEGER DEFAULT 0,
            hp_bonus INTEGER DEFAULT 0,
            mp_bonus INTEGER DEFAULT 0,
            str_bonus INTEGER DEFAULT 0,
            dex_bonus INTEGER DEFAULT 0,
            int_bonus INTEGER DEFAULT 0,
            luk_bonus INTEGER DEFAULT 0,
            locked BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, slot),
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    """)
    
    # Inventory table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            quantity INTEGER DEFAULT 1,
            item_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    """)
    
    # Auto Hunt table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS auto_hunt (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            duration INTEGER,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            status TEXT DEFAULT 'active',
            exp_pending INTEGER DEFAULT 0,
            meso_pending INTEGER DEFAULT 0,
            notified BOOLEAN DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    """)
    
    # Dungeon Runs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dungeon_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            dungeon_id TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            completed BOOLEAN DEFAULT 0,
            exp_gained INTEGER DEFAULT 0,
            meso_gained INTEGER DEFAULT 0,
            item_dropped TEXT,
            run_date DATE DEFAULT CURRENT_DATE,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    """)
    
    # Daily Quests Progress
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quest_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            quest_id TEXT NOT NULL,
            progress INTEGER DEFAULT 0,
            completed BOOLEAN DEFAULT 0,
            claimed BOOLEAN DEFAULT 0,
            reset_date DATE DEFAULT CURRENT_DATE,
            UNIQUE(user_id, quest_id, reset_date),
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    """)
    
    # Achievements
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            achievement_id TEXT NOT NULL,
            progress INTEGER DEFAULT 0,
            completed BOOLEAN DEFAULT 0,
            completed_at TIMESTAMP,
            UNIQUE(user_id, achievement_id),
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    """)
    
    # Admin Logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            target_user_id INTEGER,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

# User Functions
def create_user(user_id: int, username: str, class_name: str):
    """Create new user"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    class_data = CLASSES[class_name]
    base_stats = class_data["base_stats"]
    
    cursor.execute("""
        INSERT INTO users (user_id, username, class, hp, mp, meso, nx)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, username, class_name, base_stats["hp"], base_stats["mp"], 0, 0))
    
    # Create beginner equipment
    beginner_items = {
        "weapon": ("Beginner Sword", "common", 1, 5, 0, 0, 0),
        "armor": ("Beginner Armor", "common", 1, 2, 5, 0, 0),
        "helmet": ("Beginner Hat", "common", 1, 1, 2, 0, 0),
    }
    
    for slot, (name, rarity, stars, atk, def_val, hp_b, mp_b) in beginner_items.items():
        cursor.execute("""
            INSERT INTO equipment (user_id, slot, name, rarity, stars, atk, def)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, slot, name, rarity, stars, atk, def_val))
    
    conn.commit()
    conn.close()

def get_user(user_id: int):
    """Get user data"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    return dict(user) if user else None

def user_exists(user_id: int):
    """Check if user exists"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
    exists = cursor.fetchone() is not None
    conn.close()
    
    return exists

def add_exp(user_id: int, exp: int):
    """Add experience to user"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE users 
        SET exp = exp + ?, total_exp = total_exp + ?
        WHERE user_id = ?
    """, (exp, exp, user_id))
    
    # Check for level up
    cursor.execute("SELECT level, exp FROM users WHERE user_id = ?", (user_id,))
    level, total_exp = cursor.fetchone()
    
    # Simple leveling: 1000 EXP per level
    new_level = min(250, 1 + (total_exp // 1000))
    
    if new_level > level:
        cursor.execute("""
            UPDATE users 
            SET level = ?, exp = 0
            WHERE user_id = ?
        """, (new_level, user_id))
    
    conn.commit()
    conn.close()

def add_meso(user_id: int, amount: int):
    """Add meso to user"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE users 
        SET meso = meso + ?
        WHERE user_id = ?
    """, (amount, user_id))
    
    conn.commit()
    conn.close()

def add_nx(user_id: int, amount: int):
    """Add NX to user"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE users 
        SET nx = nx + ?
        WHERE user_id = ?
    """, (amount, user_id))
    
    conn.commit()
    conn.close()

def subtract_meso(user_id: int, amount: int) -> bool:
    """Subtract meso, return True if successful"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT meso FROM users WHERE user_id = ?", (user_id,))
    current_meso = cursor.fetchone()[0]
    
    if current_meso < amount:
        conn.close()
        return False
    
    cursor.execute("""
        UPDATE users 
        SET meso = meso - ?
        WHERE user_id = ?
    """, (amount, user_id))
    
    conn.commit()
    conn.close()
    return True

def subtract_nx(user_id: int, amount: int) -> bool:
    """Subtract NX, return True if successful"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT nx FROM users WHERE user_id = ?", (user_id,))
    current_nx = cursor.fetchone()[0]
    
    if current_nx < amount:
        conn.close()
        return False
    
    cursor.execute("""
        UPDATE users 
        SET nx = nx - ?
        WHERE user_id = ?
    """, (amount, user_id))
    
    conn.commit()
    conn.close()
    return True

# Equipment Functions
def get_equipment(user_id: int):
    """Get all user equipment"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM equipment 
        WHERE user_id = ?
        ORDER BY slot
    """, (user_id,))
    
    equipment = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return equipment

def get_equipment_slot(user_id: int, slot: str):
    """Get equipment in specific slot"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM equipment 
        WHERE user_id = ? AND slot = ?
    """, (user_id, slot))
    
    equipment = cursor.fetchone()
    conn.close()
    
    return dict(equipment) if equipment else None

def update_equipment_stars(equipment_id: int, new_stars: int, protect_used: bool = False):
    """Update equipment stars"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if new_stars < 0:
        # Equipment breaks
        cursor.execute("DELETE FROM equipment WHERE id = ?", (equipment_id,))
    else:
        cursor.execute("""
            UPDATE equipment 
            SET stars = ?
            WHERE id = ?
        """, (new_stars, equipment_id))
    
    conn.commit()
    conn.close()

# Auto Hunt Functions
def start_auto_hunt(user_id: int, duration: int):
    """Start auto hunt session"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO auto_hunt 
        (user_id, duration, start_time, status, notified)
        VALUES (?, ?, datetime('now'), 'active', 0)
    """, (user_id, duration))
    
    conn.commit()
    conn.close()

def get_auto_hunt(user_id: int):
    """Get current auto hunt status"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM auto_hunt WHERE user_id = ?", (user_id,))
    hunt = cursor.fetchone()
    conn.close()
    
    return dict(hunt) if hunt else None

def complete_auto_hunt(user_id: int, exp: int, meso: int):
    """Complete auto hunt and grant rewards"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        DELETE FROM auto_hunt WHERE user_id = ?
    """, (user_id,))
    
    conn.commit()
    conn.close()
    
    add_exp(user_id, exp)
    add_meso(user_id, meso)

# Dungeon Functions
def get_dungeon_runs_today(user_id: int, dungeon_id: str, difficulty: str):
    """Get number of dungeon runs today"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COUNT(*) FROM dungeon_runs 
        WHERE user_id = ? AND dungeon_id = ? AND difficulty = ? AND run_date = CURRENT_DATE
    """, (user_id, dungeon_id, difficulty))
    
    count = cursor.fetchone()[0]
    conn.close()
    
    return count

def record_dungeon_run(user_id: int, dungeon_id: str, difficulty: str, exp: int, meso: int, item: str = None):
    """Record dungeon run"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO dungeon_runs 
        (user_id, dungeon_id, difficulty, completed, exp_gained, meso_gained, item_dropped)
        VALUES (?, ?, ?, 1, ?, ?, ?)
    """, (user_id, dungeon_id, difficulty, exp, meso, item))
    
    conn.commit()
    conn.close()
    
    add_exp(user_id, exp)
    add_meso(user_id, meso)

# Quest Functions
def get_quest_progress(user_id: int, quest_id: str):
    """Get quest progress"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM quest_progress 
        WHERE user_id = ? AND quest_id = ? AND reset_date = CURRENT_DATE
    """, (user_id, quest_id))
    
    progress = cursor.fetchone()
    conn.close()
    
    return dict(progress) if progress else None

def update_quest_progress(user_id: int, quest_id: str, increment: int = 1):
    """Update quest progress"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    progress = get_quest_progress(user_id, quest_id)
    
    if progress:
        cursor.execute("""
            UPDATE quest_progress 
            SET progress = progress + ?
            WHERE user_id = ? AND quest_id = ? AND reset_date = CURRENT_DATE
        """, (increment, user_id, quest_id))
    else:
        cursor.execute("""
            INSERT INTO quest_progress 
            (user_id, quest_id, progress)
            VALUES (?, ?, ?)
        """, (user_id, quest_id, increment))
    
    conn.commit()
    conn.close()

def claim_quest_reward(user_id: int, quest_id: str, exp: int, meso: int):
    """Claim quest reward"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE quest_progress 
        SET claimed = 1
        WHERE user_id = ? AND quest_id = ? AND reset_date = CURRENT_DATE
    """, (user_id, quest_id))
    
    conn.commit()
    conn.close()
    
    add_exp(user_id, exp)
    add_meso(user_id, meso)

def get_all_quests_today(user_id: int):
    """Get all quest progress for today"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM quest_progress 
        WHERE user_id = ? AND reset_date = CURRENT_DATE
        ORDER BY quest_id
    """, (user_id,))
    
    quests = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return quests

def get_achievement(user_id: int, achievement_id: str):
    """Get achievement progress"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM achievements 
        WHERE user_id = ? AND achievement_id = ?
    """, (user_id, achievement_id))
    
    achievement = cursor.fetchone()
    conn.close()
    
    return dict(achievement) if achievement else None

def update_achievement_progress(user_id: int, achievement_id: str, increment: int = 1):
    """Update achievement progress"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    achievement = get_achievement(user_id, achievement_id)
    
    if achievement:
        cursor.execute("""
            UPDATE achievements 
            SET progress = progress + ?
            WHERE user_id = ? AND achievement_id = ?
        """, (increment, user_id, achievement_id))
    else:
        cursor.execute("""
            INSERT INTO achievements 
            (user_id, achievement_id, progress)
            VALUES (?, ?, ?)
        """, (user_id, achievement_id, increment))
    
    conn.commit()
    conn.close()
