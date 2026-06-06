"""Utility functions for formatting game messages"""
import database as db
from config import CLASSES, EQUIPMENT_SLOTS

def format_user_profile(user_id: int) -> str:
    """Format user profile display"""
    user = db.get_user(user_id)
    equipment = db.get_equipment(user_id)
    
    if not user:
        return "User not found"
    
    class_info = CLASSES.get(user["class"], {})
    
    # Calculate total ATK and DEF from equipment
    total_atk = sum(e.get("atk", 0) for e in equipment)
    total_def = sum(e.get("def", 0) for e in equipment)
    
    profile = f"""
╔════════════════════════════════╗
║   {class_info.get('name', 'Unknown')}
║
║ Lv.{user['level']} | EXP: {user['exp']}/1000
║ HP: {user['hp']} | MP: {user['mp']}
║
║ ATK: {total_atk} | DEF: {total_def}
║
║ Meso: {user['meso']:,} 💰
║ NX: {user['nx']} ⭐
║
║ Total EXP: {user['total_exp']:,}
╚════════════════════════════════╝
"""
    return profile

def format_equipment_inventory(user_id: int) -> str:
    """Format equipment inventory display"""
    equipment = db.get_equipment(user_id)
    
    if not equipment:
        return "No equipment found"
    
    inv_text = "╔════ 📦 Equipment ════╗\n"
    
    for item in equipment:
        slot_name = EQUIPMENT_SLOTS.get(item["slot"], item["slot"])
        stars = "⭐" * item["stars"]
        
        inv_text += f"║ {slot_name}\n"
        inv_text += f"║ {item['name']} {stars}\n"
        inv_text += f"║ ATK: +{item['atk']} | DEF: +{item['def']}\n"
        inv_text += f"║ ─────────────────\n"
    
    inv_text += "╚═══════════════════╝"
    return inv_text

def format_stat_bonus(equipment: list) -> dict:
    """Calculate total stat bonuses from equipment"""
    bonuses = {
        "atk": 0, "def": 0, "hp": 0, "mp": 0,
        "str": 0, "dex": 0, "int": 0, "luk": 0
    }
    
    for item in equipment:
        for key in bonuses:
            bonuses[key] += item.get(f"{key}_bonus", 0)
    
    return bonuses

def format_dungeon_info(dungeon_id: str, difficulty: str) -> str:
    """Format dungeon information"""
    from config import DUNGEONS
    
    dungeon = DUNGEONS.get(dungeon_id, {})
    diff_info = dungeon.get("difficulties", {}).get(difficulty, {})
    
    text = f"""
╔════════════════════════════════╗
║ {dungeon.get('name', 'Unknown')}
║ Difficulty: {difficulty.upper()}
║
║ Min Level: {diff_info.get('min_level', '?')}
║ Boss HP: {diff_info.get('boss_hp', '?')}
║ Boss ATK: {diff_info.get('boss_atk', '?')}
║ Boss DEF: {diff_info.get('boss_def', '?')}
║
║ Rewards:
║ EXP: +{diff_info.get('exp_reward', 0):,}
║ Meso: +{diff_info.get('meso_reward', 0):,}
║ Drop Rate: {diff_info.get('item_drop_rate', 0)*100:.0f}%
╚════════════════════════════════╝
"""
    return text

def format_auto_hunt_status(user_id: int) -> str:
    """Format auto hunt status"""
    from datetime import datetime, timedelta
    
    hunt = db.get_auto_hunt(user_id)
    
    if not hunt:
        return "❌ No active auto hunt"
    
    start_time = datetime.fromisoformat(hunt["start_time"])
    end_time = start_time + timedelta(minutes=hunt["duration"])
    now = datetime.now()
    
    remaining = (end_time - now).total_seconds()
    hours = int(remaining // 3600)
    minutes = int((remaining % 3600) // 60)
    
    status_text = f"""
╔════════════════════════════════╗
║ 🤖 AUTO HUNT IN PROGRESS
║
║ Duration: {hunt['duration']} min
║ Time Remaining: {hours}h {minutes}m
║
║ EXP Pending: +{hunt['exp_pending']:,}
║ Meso Pending: +{hunt['meso_pending']:,}
╚════════════════════════════════╝
"""
    return status_text

def format_quest_list(user_id: int) -> str:
    """Format daily quests list"""
    from config import DAILY_QUESTS
    
    quests_progress = db.get_all_quests_today(user_id)
    quest_dict = {q["quest_id"]: q for q in quests_progress}
    
    text = "╔════ 📋 DAILY QUESTS ════╗\n"
    
    for quest in DAILY_QUESTS:
        progress = quest_dict.get(quest["id"], {})
        current = progress.get("progress", 0)
        target = quest["target"]
        claimed = progress.get("claimed", False)
        completed = progress.get("completed", False)
        
        status = "✅" if claimed else ("✔️" if completed else "❌")
        bar_fill = min(10, int((current / target) * 10))
        bar = "█" * bar_fill + "░" * (10 - bar_fill)
        
        text += f"║ {status} {quest['name']}\n"
        text += f"║ {bar} {current}/{target}\n"
        text += f"║ Reward: {quest['reward_exp']} EXP, {quest['reward_meso']} Meso\n"
        text += f"║ ─────────────────────\n"
    
    text += "╚════════════════════════╝"
    return text

def format_inventory_simple(user_id: int) -> str:
    """Format simple inventory view"""
    user = db.get_user(user_id)
    equipment = db.get_equipment(user_id)
    
    text = f"💰 Meso: {user['meso']:,}\n"
    text += f"⭐ NX: {user['nx']}\n"
    text += f"📦 Equipment: {len(equipment)}/11 slots\n"
    
    return text
