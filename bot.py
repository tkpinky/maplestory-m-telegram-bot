"""Main Telegram Bot Handler"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode
import database as db
from config import BOT_TOKEN, ADMIN_IDS, CLASSES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
db.init_db()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command - show main menu"""
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name
    
    if not db.user_exists(user_id):
        # New player - show class selection
        await show_class_selection(update, context)
    else:
        # Existing player - show main menu
        await show_main_menu(update, context)

async def show_class_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show class selection for new players"""
    keyboard = []
    for class_id, class_data in CLASSES.items():
        btn = InlineKeyboardButton(class_data["name"], callback_data=f"class_{class_id}")
        keyboard.append([btn])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """
🎮 **Welcome to MapleStory M!**

Choose your class to begin your adventure:

⚔️ **Warrior** - High DEF, tanky
🔥 **Mage** - High INT, magical damage
🏹 **Archer** - High DEX, ranged attacks
🗡️ **Thief** - High DEX & LUK, fast attacks
🎯 **Bowmaster** - Balanced damage dealer
"""
    
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)

async def handle_class_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle class selection callback"""
    query = update.callback_query
    user_id = query.from_user.id
    username = query.from_user.username or query.from_user.first_name
    
    class_id = query.data.replace("class_", "")
    
    if class_id not in CLASSES:
        await query.answer("Invalid class!", show_alert=True)
        return
    
    # Create user
    db.create_user(user_id, username, class_id)
    
    class_name = CLASSES[class_id]["name"]
    
    await query.edit_message_text(f"✅ Welcome {class_name}!\n\nYour adventure begins now!")
    
    # Show main menu after 1 second
    await context.application.run_async(show_main_menu, update, context)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show main menu"""
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    
    if not user:
        await update.message.reply_text("❌ User not found. Use /start to create account.")
        return
    
    from utils.formatters import format_user_profile, format_inventory_simple
    
    profile = format_user_profile(user_id)
    inventory = format_inventory_simple(user_id)
    
    keyboard = [
        [InlineKeyboardButton("🤖 Auto Hunt", callback_data="menu_autohunt"),
         InlineKeyboardButton("⚔️ Dungeons", callback_data="menu_dungeons")],
        [InlineKeyboardButton("🛡️ Equipment", callback_data="menu_equipment"),
         InlineKeyboardButton("📋 Quests", callback_data="menu_quests")],
        [InlineKeyboardButton("🏆 Achievements", callback_data="menu_achievements"),
         InlineKeyboardButton("💳 Shop", callback_data="menu_shop")],
    ]
    
    if user_id in ADMIN_IDS:
        keyboard.append([InlineKeyboardButton("⚙️ Admin Panel", callback_data="menu_admin")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = f"{profile}\n{inventory}"
    
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)

async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle menu callbacks"""
    query = update.callback_query
    menu = query.data.replace("menu_", "")
    
    if menu == "autohunt":
        await show_autohunt_menu(query, context)
    elif menu == "dungeons":
        await show_dungeon_menu(query, context)
    elif menu == "equipment":
        await show_equipment_menu(query, context)
    elif menu == "quests":
        await show_quest_menu(query, context)
    elif menu == "achievements":
        await show_achievement_menu(query, context)
    elif menu == "shop":
        await show_shop_menu(query, context)
    elif menu == "admin":
        await show_admin_menu(query, context)

async def show_autohunt_menu(query, context):
    """Show auto hunt menu"""
    from game_logic.autohunt import auto_hunt_manager
    
    hunt_status = auto_hunt_manager.get_hunt_status(query.from_user.id)
    
    if hunt_status and hunt_status["remaining_seconds"] > 0:
        # Hunt in progress
        display = auto_hunt_manager.format_hunt_display(query.from_user.id)
        keyboard = [
            [InlineKeyboardButton("🔄 Refresh", callback_data="autohunt_refresh")],
            [InlineKeyboardButton("⬅️ Back", callback_data="menu_main")]
        ]
    else:
        # No hunt - show duration options
        from config import AUTO_HUNT_DURATIONS
        
        display = """
╔════════════════════════════════╗
║ 🤖 AUTO HUNT
║
║ Select hunting duration:
╚════════════════════════════════╝
"""
        keyboard = []
        for duration in AUTO_HUNT_DURATIONS:
            btn = InlineKeyboardButton(f"{duration}min", callback_data=f"autohunt_start_{duration}")
            keyboard.append([btn])
        
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="menu_main")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(display, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)

async def show_dungeon_menu(query, context):
    """Show dungeon menu"""
    from config import DUNGEONS
    
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
    await query.edit_message_text(display, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)

async def show_equipment_menu(query, context):
    """Show equipment menu"""
    from utils.formatters import format_equipment_inventory
    
    display = format_equipment_inventory(query.from_user.id)
    
    keyboard = [
        [InlineKeyboardButton("⭐ Enhance", callback_data="equip_enhance")],
        [InlineKeyboardButton("⬅️ Back", callback_data="menu_main")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(display, reply_markup=reply_markup)

async def show_quest_menu(query, context):
    """Show quest menu"""
    from game_logic.quests import format_quest_display
    
    display = format_quest_display(query.from_user.id)
    
    keyboard = [
        [InlineKeyboardButton("📥 Claim Rewards", callback_data="quest_claim")],
        [InlineKeyboardButton("🔄 Refresh", callback_data="quest_refresh")],
        [InlineKeyboardButton("⬅️ Back", callback_data="menu_main")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(display, reply_markup=reply_markup)

async def show_achievement_menu(query, context):
    """Show achievement menu"""
    from game_logic.quests import ACHIEVEMENTS
    
    user = db.get_user(query.from_user.id)
    achievements = user  # Placeholder
    
    display = """
╔════════════════════════════════╗
║ 🏆 ACHIEVEMENTS
║
║ Unlocking achievements grants
║ EXP and Meso bonuses!
╚════════════════════════════════╝
"""
    
    keyboard = [
        [InlineKeyboardButton("⬅️ Back", callback_data="menu_main")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(display, reply_markup=reply_markup)

async def show_shop_menu(query, context):
    """Show shop menu"""
    display = """
╔════════════════════════════════╗
║ 💳 SHOP
║
║ Buy NX with Telegram Stars
╚════════════════════════════════╝
"""
    
    keyboard = [
        [InlineKeyboardButton("⭐ 100 Stars → 10,000 NX", callback_data="shop_100stars")],
        [InlineKeyboardButton("⭐ 500 Stars → 50,000 NX", callback_data="shop_500stars")],
        [InlineKeyboardButton("⬅️ Back", callback_data="menu_main")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(display, reply_markup=reply_markup)

async def show_admin_menu(query, context):
    """Show admin menu"""
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Admin only!", show_alert=True)
        return
    
    display = """
╔════════════════════════════════╗
║ ⚙️ ADMIN PANEL
║
║ Select action:
╚════════════════════════════════╝
"""
    
    keyboard = [
        [InlineKeyboardButton("👤 Adjust Player Stats", callback_data="admin_stats")],
        [InlineKeyboardButton("🛡️ Adjust Equipment", callback_data="admin_equipment")],
        [InlineKeyboardButton("💰 Add Currency", callback_data="admin_currency")],
        [InlineKeyboardButton("⬅️ Back", callback_data="menu_main")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(display, reply_markup=reply_markup)

async def handle_back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle back to main menu"""
    await show_main_menu(update, context)

def main():
    """Start the bot"""
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", show_main_menu))
    
    app.add_handler(CallbackQueryHandler(handle_class_selection, pattern="^class_"))
    app.add_handler(CallbackQueryHandler(handle_menu, pattern="^menu_"))
    app.add_handler(CallbackQueryHandler(handle_back_to_main, pattern="^back_main$"))
    
    logger.info("Starting bot...")
    app.run_polling()

if __name__ == "__main__":
    main()
