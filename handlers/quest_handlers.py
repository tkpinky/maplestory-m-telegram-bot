"""Quest handlers"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import database as db
from game_logic.quests import format_quest_display, get_all_user_quests, claim_quest

async def show_quest_menu(query, context: ContextTypes.DEFAULT_TYPE):
    """Show quest menu"""
    user_id = query.from_user.id
    
    display = format_quest_display(user_id)
    
    keyboard = [
        [InlineKeyboardButton("📥 Claim Rewards", callback_data="quest_claim")],
        [InlineKeyboardButton("🔄 Refresh", callback_data="quest_refresh")],
        [InlineKeyboardButton("⬅️ Back", callback_data="menu_main")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(display, reply_markup=reply_markup)

async def handle_quest_claim(query, context: ContextTypes.DEFAULT_TYPE):
    """Handle quest reward claiming"""
    user_id = query.from_user.id
    quests = get_all_user_quests(user_id)
    
    total_exp = 0
    total_meso = 0
    claimed_count = 0
    
    for quest_progress in quests:
        quest_id = quest_progress["quest_id"]
        
        if quest_progress["completed"] and not quest_progress["claimed"]:
            result = claim_quest(user_id, quest_id)
            
            if result["success"]:
                total_exp += result["exp_gained"]
                total_meso += result["meso_gained"]
                claimed_count += 1
    
    if claimed_count == 0:
        await query.answer("❌ No claimable rewards!", show_alert=True)
        return
    
    display = f"""
✅ **REWARDS CLAIMED!**

Quests Completed: {claimed_count}

Total Rewards:
✨ +{total_exp:,} EXP
💰 +{total_meso:,} Meso
"""
    
    await query.edit_message_text(display, parse_mode=ParseMode.MARKDOWN)
    
    keyboard = [
        [InlineKeyboardButton("📋 Quests", callback_data="menu_quests")],
        [InlineKeyboardButton("⬅️ Back", callback_data="menu_main")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("What next?", reply_markup=reply_markup)

async def handle_quest_refresh(query, context: ContextTypes.DEFAULT_TYPE):
    """Refresh quest display"""
    await show_quest_menu(query, context)
