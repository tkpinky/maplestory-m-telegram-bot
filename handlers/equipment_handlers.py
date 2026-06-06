"""Equipment handlers"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import database as db
from game_logic.equipment import enhance_equipment, can_enhance, get_enhancement_cost, get_success_rate

async def show_equipment_menu(query, context: ContextTypes.DEFAULT_TYPE):
    """Show equipment selection for enhancement"""
    user_id = query.from_user.id
    equipment = db.get_equipment(user_id)
    
    if not equipment:
        await query.answer("No equipment found!", show_alert=True)
        return
    
    display = "╔════ 🛡️ EQUIPMENT ════╗\n"
    display += "║ Select item to enhance:\n"
    display += "║ ───────────────────\n"
    
    keyboard = []
    for item in equipment:
        from config import EQUIPMENT_SLOTS
        slot_name = EQUIPMENT_SLOTS.get(item["slot"], item["slot"])
        stars = "⭐" * item["stars"]
        
        btn_text = f"{slot_name} {item['name']} {stars}"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"equip_{item['id']}")])
    
    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="menu_main")])
    
    display += "╚═══════════════════╝"
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(display, reply_markup=reply_markup)

async def show_enhance_options(query, context: ContextTypes.DEFAULT_TYPE):
    """Show enhancement options for selected equipment"""
    user_id = query.from_user.id
    equipment_id = int(query.data.replace("equip_", ""))
    
    conn = db.sqlite3.connect(db.DB_PATH)
    conn.row_factory = db.sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM equipment WHERE id = ? AND user_id = ?
    """, (equipment_id, user_id))
    
    item = cursor.fetchone()
    conn.close()
    
    if not item:
        await query.answer("Item not found!", show_alert=True)
        return
    
    item = dict(item)
    
    if not can_enhance(equipment_id, user_id):
        await query.answer("This item is already maxed!", show_alert=True)
        return
    
    meso_cost, nx_cost = get_enhancement_cost(item["stars"])
    success_rate = get_success_rate(item["stars"])
    
    from config import EQUIPMENT_SLOTS
    slot_name = EQUIPMENT_SLOTS.get(item["slot"], item["slot"])
    
    display = f"""
╔════════════════════════════════╗
║ ⭐ ENHANCE EQUIPMENT
║
║ {slot_name}
║ {item['name']} ⭐{item['stars']}
║
║ ─────────────────────────────
║ Next Level: ⭐{item['stars'] + 1}
║
║ Cost: {meso_cost:,} 💰 + {nx_cost} NX
║ Success Rate: {success_rate * 100:.0f}%
║
║ On Failure:
║ • 70% Downgrade (-1⭐)
║ • 30% Break (Lost Item)
╚════════════════════════════════╝
"""
    
    keyboard = [
        [InlineKeyboardButton("⭐ Enhance", callback_data=f"enhance_confirm_{equipment_id}")],
        [InlineKeyboardButton("🛡️ Protect Scroll (+300 NX)", callback_data=f"enhance_protect_{equipment_id}")],
        [InlineKeyboardButton("⬅️ Back", callback_data="menu_equipment")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(display, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)

async def handle_enhance(query, context: ContextTypes.DEFAULT_TYPE):
    """Handle equipment enhancement"""
    user_id = query.from_user.id
    
    use_protect = "protect" in query.data
    equipment_id = int(query.data.split("_")[-1])
    
    result = enhance_equipment(equipment_id, user_id, use_protect_scroll=use_protect)
    
    if not result["success"]:
        await query.answer(result["message"], show_alert=True)
        return
    
    message = result["message"]
    
    if result["result"] == "success":
        # Update quest progress
        db.update_quest_progress(user_id, "star_force", 1)
    
    await query.edit_message_text(message)
    
    # Show back to equipment menu
    keyboard = [
        [InlineKeyboardButton("🛡️ Equipment", callback_data="menu_equipment")],
        [InlineKeyboardButton("⬅️ Back", callback_data="menu_main")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("What next?", reply_markup=reply_markup)
