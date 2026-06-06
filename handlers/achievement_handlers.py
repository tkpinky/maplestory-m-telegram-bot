"""Achievement handlers and system"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import database as db
from game_logic.quests import ACHIEVEMENTS, get_achievement

async def show_achievement_menu(query, context: ContextTypes.DEFAULT_TYPE):
    """Show achievements UI"""
    user_id = query.from_user.id
    
    display = "╔════════════════════════════════╗\n"
    display += "║ 🏆 ACHIEVEMENTS\n"
    display += "║\n"
    display += "║ Achievements unlock permanent\n"
    display += "║ bonuses and prestige!\n"
    display += "║\n"
    
    keyboard = []
    
    for achievement_id, achievement in ACHIEVEMENTS.items():
        progress = get_achievement(user_id, achievement_id)
        
        if progress and progress["completed"]:
            status = "✅"
        elif progress:
            current = progress["progress"]
            target = achievement["target"]
            status = f"{int((current/target)*100)}%"
        else:
            status = "🔒"
        
        btn = InlineKeyboardButton(
            f"{status} {achievement['name']}",
            callback_data=f"achievement_detail_{achievement_id}"
        )
        keyboard.append([btn])
    
    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="menu_main")])
    
    display += "╚════════════════════════════════╝"
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(display, reply_markup=reply_markup)

async def show_achievement_detail(query, context: ContextTypes.DEFAULT_TYPE):
    """Show achievement detail"""
    user_id = query.from_user.id
    achievement_id = query.data.replace("achievement_detail_", "")
    
    achievement = ACHIEVEMENTS.get(achievement_id)
    if not achievement:
        await query.answer("Achievement not found!", show_alert=True)
        return
    
    progress = get_achievement(user_id, achievement_id)
    
    if progress:
        current = progress["progress"]
        completed = progress["completed"]
    else:
        current = 0
        completed = False
    
    target = achievement["target"]
    percent = min(100, int((current / target) * 100))
    
    status = "✅ UNLOCKED" if completed else f"IN PROGRESS - {percent}%"
    
    progress_bar = "█" * int(percent / 5) + "░" * (20 - int(percent / 5))
    
    display = f"""
╔════════════════════════════════╗
║ 🏆 {achievement['name']}
║
║ [{progress_bar}]
║ {current}/{target}
║
║ Status: {status}
║
║ {achievement['description']}
║
║ Reward:
║ ✨ +{achievement['reward_exp']:,} EXP
║ 💰 +{achievement['reward_meso']:,} Meso
╚════════════════════════════════╝
"""
    
    keyboard = [
        [InlineKeyboardButton("🏆 Achievements", callback_data="menu_achievements")],
        [InlineKeyboardButton("⬅️ Back", callback_data="menu_main")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(display, reply_markup=reply_markup)
