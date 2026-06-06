"""Admin panel handlers for testing and adjustments"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from telegram.constants import ParseMode
import database as db
from config import ADMIN_IDS

# Conversation states
ADMIN_CHOOSE_PLAYER, ADMIN_ADJUST_LEVEL, ADMIN_ADJUST_MESO, ADMIN_ADJUST_NX, ADMIN_ADJUST_STARS = range(5)

async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin panel entry"""
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ Unauthorized")
        return
    
    keyboard = [
        [InlineKeyboardButton("👤 Adjust Player Stats", callback_data="admin_stats")],
        [InlineKeyboardButton("🛡️ Adjust Equipment", callback_data="admin_equipment")],
        [InlineKeyboardButton("💰 Add Currency", callback_data="admin_currency")],
        [InlineKeyboardButton("⬅️ Back", callback_data="menu_main")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("⚙️ **ADMIN PANEL**\n\nSelect action:", reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)

async def admin_adjust_player(query, context: ContextTypes.DEFAULT_TYPE):
    """Admin adjust player stats"""
    admin_id = query.from_user.id
    if admin_id not in ADMIN_IDS:
        await query.answer("❌ Unauthorized", show_alert=True)
        return
    
    await query.message.reply_text(
        "📝 Enter player User ID to adjust:\n\n(Copy from: /id or their profile)"
    )
    
    return ADMIN_CHOOSE_PLAYER

async def admin_receive_player_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive player ID from admin"""
    try:
        player_id = int(update.message.text)
    except ValueError:
        await update.message.reply_text("❌ Invalid User ID!")
        return ADMIN_CHOOSE_PLAYER
    
    if not db.user_exists(player_id):
        await update.message.reply_text("❌ Player not found!")
        return ADMIN_CHOOSE_PLAYER
    
    context.user_data["target_player"] = player_id
    user = db.get_user(player_id)
    
    display = f"""
👤 **Player Found**

Level: {user['level']}
Meso: {user['meso']:,}
NX: {user['nx']}

What to adjust?
"""
    
    keyboard = [
        [InlineKeyboardButton("📈 Level", callback_data="admin_adjust_level")],
        [InlineKeyboardButton("💰 Meso", callback_data="admin_adjust_meso")],
        [InlineKeyboardButton("⭐ NX", callback_data="admin_adjust_nx")],
        [InlineKeyboardButton("🛡️ Equipment Stars", callback_data="admin_adjust_stars")],
        [InlineKeyboardButton("❌ Cancel", callback_data="menu_admin")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(display, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    return ConversationHandler.END

async def admin_adjust_level(query, context: ContextTypes.DEFAULT_TYPE):
    """Admin adjust player level"""
    await query.message.reply_text(
        "📝 Enter new level (1-250):"
    )
    
    return ADMIN_ADJUST_LEVEL

async def admin_receive_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive level adjustment"""
    try:
        new_level = int(update.message.text)
    except ValueError:
        await update.message.reply_text("❌ Invalid number!")
        return ADMIN_ADJUST_LEVEL
    
    if not (1 <= new_level <= 250):
        await update.message.reply_text("❌ Level must be 1-250!")
        return ADMIN_ADJUST_LEVEL
    
    player_id = context.user_data.get("target_player")
    
    conn = db.sqlite3.connect(db.DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE users SET level = ? WHERE user_id = ?
    """, (new_level, player_id))
    
    conn.commit()
    conn.close()
    
    # Log action
    conn = db.sqlite3.connect(db.DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO admin_logs (admin_id, action, target_user_id, details)
        VALUES (?, ?, ?, ?)
    """, (update.effective_user.id, "adjust_level", player_id, f"Set level to {new_level}"))
    
    conn.commit()
    conn.close()
    
    await update.message.reply_text(f"✅ Level adjusted to {new_level}")
    
    return ConversationHandler.END

async def admin_adjust_meso(query, context: ContextTypes.DEFAULT_TYPE):
    """Admin adjust meso"""
    await query.message.reply_text(
        "💰 Enter amount of Meso to ADD (+) or SET (=):\n\n+10000 = add 10k\n=50000 = set to 50k"
    )
    
    return ADMIN_ADJUST_MESO

async def admin_receive_meso(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive meso adjustment"""
    text = update.message.text
    player_id = context.user_data.get("target_player")
    
    if text.startswith("+"):
        try:
            amount = int(text[1:])
            db.add_meso(player_id, amount)
            await update.message.reply_text(f"✅ Added {amount:,} Meso")
        except ValueError:
            await update.message.reply_text("❌ Invalid amount!")
            return ADMIN_ADJUST_MESO
    
    elif text.startswith("="):
        try:
            amount = int(text[1:])
            conn = db.sqlite3.connect(db.DB_PATH)
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET meso = ? WHERE user_id = ?", (amount, player_id))
            conn.commit()
            conn.close()
            await update.message.reply_text(f"✅ Set Meso to {amount:,}")
        except ValueError:
            await update.message.reply_text("❌ Invalid amount!")
            return ADMIN_ADJUST_MESO
    else:
        await update.message.reply_text("❌ Use + to add or = to set!")
        return ADMIN_ADJUST_MESO
    
    return ConversationHandler.END

async def admin_adjust_nx(query, context: ContextTypes.DEFAULT_TYPE):
    """Admin adjust NX"""
    await query.message.reply_text(
        "⭐ Enter amount of NX to ADD (+) or SET (=):\n\n+1000 = add 1k\n=5000 = set to 5k"
    )
    
    return ADMIN_ADJUST_NX

async def admin_receive_nx(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive NX adjustment"""
    text = update.message.text
    player_id = context.user_data.get("target_player")
    
    if text.startswith("+"):
        try:
            amount = int(text[1:])
            db.add_nx(player_id, amount)
            await update.message.reply_text(f"✅ Added {amount} NX")
        except ValueError:
            await update.message.reply_text("❌ Invalid amount!")
            return ADMIN_ADJUST_NX
    
    elif text.startswith("="):
        try:
            amount = int(text[1:])
            conn = db.sqlite3.connect(db.DB_PATH)
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET nx = ? WHERE user_id = ?", (amount, player_id))
            conn.commit()
            conn.close()
            await update.message.reply_text(f"✅ Set NX to {amount}")
        except ValueError:
            await update.message.reply_text("❌ Invalid amount!")
            return ADMIN_ADJUST_NX
    else:
        await update.message.reply_text("❌ Use + to add or = to set!")
        return ADMIN_ADJUST_NX
    
    return ConversationHandler.END

async def admin_adjust_stars(query, context: ContextTypes.DEFAULT_TYPE):
    """Admin adjust equipment stars"""
    player_id = context.user_data.get("target_player")
    equipment = db.get_equipment(player_id)
    
    from config import EQUIPMENT_SLOTS
    
    display = "Select equipment to adjust stars:\n\n"
    
    keyboard = []
    for item in equipment:
        slot_name = EQUIPMENT_SLOTS.get(item["slot"], item["slot"])
        btn = InlineKeyboardButton(
            f"{slot_name}: {item['name']} ⭐{item['stars']}",
            callback_data=f"admin_star_select_{item['id']}"
        )
        keyboard.append([btn])
    
    keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="menu_admin")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(display, reply_markup=reply_markup)
    
    return ConversationHandler.END
