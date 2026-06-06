"""Daily Quests and Achievement system"""
import database as db
from config import DAILY_QUESTS
from datetime import datetime, time
import pytz

ACHIEVEMENTS = {
    "first_hunt": {
        "name": "First Hunt",
        "description": "Complete your first auto hunt",
        "target": 1,
        "reward_exp": 1000,
        "reward_meso": 5000,
    },
    "level_100": {
        "name": "Century",
        "description": "Reach level 100",
        "target": 100,
        "reward_exp": 50000,
        "reward_meso": 100000,
    },
    "level_250": {
        "name": "True Legend",
        "description": "Reach level 250 (max level)",
        "target": 250,
        "reward_exp": 500000,
        "reward_meso": 1000000,
    },
    "star_100": {
        "name": "Star Collector",
        "description": "Get 100 total stars across all equipment",
        "target": 100,
        "reward_exp": 100000,
        "reward_meso": 500000,
    },
    "perfect_quests": {
        "name": "Perfect Day",
        "description": "Complete all 10 daily quests",
        "target": 10,
        "reward_exp": 50000,
        "reward_meso": 100000,
    },
    "boss_slayer": {
        "name": "Boss Slayer",
        "description": "Defeat 50 bosses",
        "target": 50,
        "reward_exp": 100000,
        "reward_meso": 500000,
    },
    "rich": {
        "name": "Wealthy",
        "description": "Accumulate 10 million Meso",
        "target": 10000000,
        "reward_exp": 50000,
        "reward_meso": 100000,
    }
}

def get_quest_by_id(quest_id: str) -> dict:
    """Get quest data by ID"""
    for quest in DAILY_QUESTS:
        if quest["id"] == quest_id:
            return quest
    return None

def get_user_quest_progress(user_id: int, quest_id: str) -> dict:
    """Get user's progress on a specific quest"""
    quest = get_quest_by_id(quest_id)
    if not quest:
        return None
    
    progress = db.get_quest_progress(user_id, quest_id)
    
    if not progress:
        return {
            "quest_id": quest_id,
            "progress": 0,
            "target": quest["target"],
            "completed": False,
            "claimed": False
        }
    
    return {
        "quest_id": quest_id,
        "progress": progress["progress"],
        "target": quest["target"],
        "completed": progress["progress"] >= quest["target"],
        "claimed": progress["claimed"],
        "quest_data": quest
    }

def get_all_user_quests(user_id: int) -> list:
    """Get all quests with user's progress"""
    quests = []
    for quest in DAILY_QUESTS:
        quests.append(get_user_quest_progress(user_id, quest["id"]))
    return quests

def claim_quest(user_id: int, quest_id: str) -> dict:
    """Claim quest reward"""
    quest = get_quest_by_id(quest_id)
    if not quest:
        return {"success": False, "message": "Quest not found"}
    
    progress = db.get_quest_progress(user_id, quest_id)
    
    if not progress:
        return {"success": False, "message": "No progress on this quest"}
    
    if progress["progress"] < quest["target"]:
        return {"success": False, "message": f"Quest not complete. Progress: {progress['progress']}/{quest['target']}"}
    
    if progress["claimed"]:
        return {"success": False, "message": "Quest reward already claimed"}
    
    # Claim reward
    exp_reward = quest.get("reward_exp", 0)
    meso_reward = quest.get("reward_meso", 0)
    
    db.claim_quest_reward(user_id, quest_id, exp_reward, meso_reward)
    
    message = f"✅ Quest Complete!\n+{exp_reward:,} EXP\n+{meso_reward:,} Meso"
    
    # Special item rewards
    if "special_item" in quest:
        message += f"\n+1 {quest['special_item']}"
    
    return {
        "success": True,
        "exp_gained": exp_reward,
        "meso_gained": meso_reward,
        "message": message
    }

def update_quest_progress(user_id: int, quest_id: str, amount: int = 1):
    """Update progress on a quest"""
    db.update_quest_progress(user_id, quest_id, amount)

def format_quest_display(user_id: int) -> str:
    """Format quest list for display"""
    quests = get_all_user_quests(user_id)
    
    completed_count = sum(1 for q in quests if q["completed"] and not q["claimed"])
    all_completed = sum(1 for q in quests if q["completed"])
    
    text = f"""
╔════════════════════════════════╗
║ 📋 DAILY QUESTS
║ Completed: {all_completed}/10 | Ready: {completed_count}
║
"""
    
    for quest in quests:
        quest_data = quest.get("quest_data", get_quest_by_id(quest["quest_id"]))
        if not quest_data:
            continue
        
        status = ""
        if quest["claimed"]:
            status = "✅ CLAIMED"
        elif quest["completed"]:
            status = "✔️ READY"
        else:
            status = "❌ IN PROGRESS"
        
        progress_bar_fill = min(10, int((quest["progress"] / quest["target"]) * 10))
        progress_bar = "█" * progress_bar_fill + "░" * (10 - progress_bar_fill)
        
        text += f"║ {status} {quest_data['name']}\n"
        text += f"║ [{progress_bar}] {quest['progress']}/{quest['target']}\n"
        text += f"║ Reward: {quest_data['reward_exp']} EXP\n"
    
    text += "╚════════════════════════════════╝"
    
    return text

def get_achievement(user_id: int, achievement_id: str) -> dict:
    """Get achievement progress"""
    achievement = ACHIEVEMENTS.get(achievement_id)
    if not achievement:
        return None
    
    progress = db.get_achievement(user_id, achievement_id)
    
    if not progress:
        return {
            "achievement_id": achievement_id,
            "progress": 0,
            "target": achievement["target"],
            "completed": False,
            "achievement_data": achievement
        }
    
    return {
        "achievement_id": achievement_id,
        "progress": progress["progress"],
        "target": achievement["target"],
        "completed": progress["completed"],
        "achievement_data": achievement
    }

def update_achievement(user_id: int, achievement_id: str, amount: int = 1):
    """Update achievement progress"""
    achievement = ACHIEVEMENTS.get(achievement_id)
    if not achievement:
        return
    
    current = db.get_achievement(user_id, achievement_id)
    new_progress = (current["progress"] if current else 0) + amount
    
    db.update_achievement_progress(user_id, achievement_id, amount)
    
    # Check if completed
    if new_progress >= achievement["target"]:
        conn = db.sqlite3.connect(db.DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE achievements 
            SET completed = 1, completed_at = datetime('now')
            WHERE user_id = ? AND achievement_id = ?
        """, (user_id, achievement_id))
        conn.commit()
        conn.close()
