"""Dungeon and boss raid handlers"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import database as db
from game_logic.combat import simulate_boss_fight, calculate_player_stats
from config import DUNGEONS

async def show_dungeon_selection(query, context: ContextTypes.DEFAULT_TYPE):
    """Show dungeon list"""
    display = """
╔════════════════════════════════╗
║ 🏰 DUNGEONS
║
║ Select a dungeon:
╚════════════════════════════════╝
"""
    
    keyboard = []
    for dungeon_id in DUNGEONS:
        dungeon = DUNGEONS[dungeon_id]
        btn = InlineKeyboardButton(dungeon["name"], callback_data=f"dungeon_select_{dungeon_id}")
        keyboard.append([btn])
    
    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="menu_main")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(display, reply_markup=reply_markup)

async def handle_dungeon_select(query, context: ContextTypes.DEFAULT_TYPE):
    """Show dungeon difficulties"""
    user_id = query.from_user.id
    dungeon_id = query.data.replace("dungeon_select_", "")
    
    dungeon = DUNGEONS.get(dungeon_id)
    if not dungeon:
        await query.answer("Dungeon not found!", show_alert=True)
        return
    
    user = db.get_user(user_id)
    
    display = f"""
╔════════════════════════════════╗
║ {dungeon['name']}
║
║ Recommended: Lv.{dungeon['levels']}
║ Your Level: Lv.{user['level']}
║
║ Select difficulty:
╚════════════════════════════════╝
"""
    
    keyboard = []
    for difficulty in ["normal", "hard"]:
        diff_config = dungeon["difficulties"][difficulty]
        min_level = diff_config["min_level"]
        
        if user["level"] >= min_level:
            status = "✅"
        else:
            status = "🔒"
        
        btn = InlineKeyboardButton(
            f"{status} {difficulty.upper()} (Lv.{min_level}+)",
            callback_data=f"dungeon_difficulty_{dungeon_id}_{difficulty}"
        )
        keyboard.append([btn])
    
    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="menu_dungeons")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(display, reply_markup=reply_markup)

async def handle_dungeon_difficulty(query, context: ContextTypes.DEFAULT_TYPE):
    """Show dungeon run confirmation"""
    user_id = query.from_user.id
    data = query.data.replace("dungeon_difficulty_", "").split("_")
    dungeon_id = data[0]
    difficulty = data[1]
    
    dungeon = DUNGEONS.get(dungeon_id)
    if not dungeon:
        await query.answer("Dungeon not found!", show_alert=True)
        return
    
    user = db.get_user(user_id)
    diff_config = dungeon["difficulties"][difficulty]
    
    # Check level requirement
    if user["level"] < diff_config["min_level"]:
        await query.answer(f"❌ You need Lv.{diff_config['min_level']}+", show_alert=True)
        return
    
    # Check daily runs limit
    runs_today = db.get_dungeon_runs_today(user_id, dungeon_id, difficulty)
    if runs_today >= 3:
        await query.answer("❌ You've completed this dungeon 3 times today!", show_alert=True)
        return
    
    display = f"""
╔════════════════════════════════╗
║ {dungeon['name']} - {difficulty.upper()}
║
║ Runs Completed: {runs_today}/3
║
║ Boss Stats:
║ HP: {diff_config['boss_hp']}
║ ATK: {diff_config['boss_atk']}
║ DEF: {diff_config['boss_def']}
║
║ Rewards:
║ EXP: +{diff_config['exp_reward']:,}
║ Meso: +{diff_config['meso_reward']:,}
║ Drop Rate: {diff_config['item_drop_rate']*100:.0f}%
╚════════════════════════════════╝
"""
    
    keyboard = [
        [InlineKeyboardButton("⚔️ Enter Dungeon", callback_data=f"dungeon_start_{dungeon_id}_{difficulty}")],
        [InlineKeyboardButton("⬅️ Back", callback_data=f"dungeon_select_{dungeon_id}")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(display, reply_markup=reply_markup)

async def handle_dungeon_start(query, context: ContextTypes.DEFAULT_TYPE):
    """Start dungeon raid"""
    user_id = query.from_user.id
    data = query.data.replace("dungeon_start_", "").split("_")
    dungeon_id = data[0]
    difficulty = data[1]
    
    user = db.get_user(user_id)
    equipment = db.get_equipment(user_id)
    
    # Calculate player stats
    player_stats = calculate_player_stats(user, equipment)
    
    # Simulate boss fight
    result = simulate_boss_fight(dungeon_id, difficulty, player_stats["atk"], player_stats["def"], player_stats["hp"])
    
    dungeon = DUNGEONS[dungeon_id]
    diff_config = dungeon["difficulties"][difficulty]
    
    if result["won"]:
        # Grant rewards
        exp_reward = diff_config["exp_reward"]
        meso_reward = diff_config["meso_reward"]
        
        db.record_dungeon_run(user_id, dungeon_id, difficulty, exp_reward, meso_reward)
        
        # Update quests
        db.update_quest_progress(user_id, "dungeon_clear", 1)
        db.update_quest_progress(user_id, "boss_defeat", 1)
        if difficulty == "hard":
            db.update_quest_progress(user_id, "hard_dungeon", 1)
        
        display = f"""
🎉 **VICTORY!**

Boss Defeated in {result['turns']} turns

Rewards:
✨ +{exp_reward:,} EXP
💰 +{meso_reward:,} Meso

Battle Summary:
• Player HP: {result['player_hp_remaining']}/{player_stats['hp']}
• Boss Phase: {result['phase']}
"""
    else:
        display = f"""
💀 **DEFEAT!**

You were defeated in {result['turns']} turns

Battle Summary:
• Boss HP Remaining: {result['boss_hp_remaining']}/{diff_config['boss_hp']}
• Your Final HP: 0

Try again after leveling up!
"""
    
    keyboard = [
        [InlineKeyboardButton("🏰 Dungeons", callback_data="menu_dungeons")],
        [InlineKeyboardButton("⬅️ Back", callback_data="menu_main")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(display, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
