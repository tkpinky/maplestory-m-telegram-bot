"""Auto hunt handlers"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import database as db
from game_logic.autohunt import auto_hunt_manager
from config import AUTO_HUNT_DURATIONS

async def show_autohunt_menu(query, context: ContextTypes.DEFAULT_TYPE):
    """Show auto hunt menu"""
    user_id = query.from_user.id
    
    hunt_status = auto_hunt_manager.get_hunt_status(user_id)
    
    if hunt_status and hunt_status["remaining_seconds"] > 0:
        # Hunt in progress
        display = auto_hunt_manager.format_hunt_display(user_id)
        keyboard = [
            [InlineKeyboardButton("🔄 Refresh", callback_data="autohunt_refresh")],
            [InlineKeyboardButton("⬅️ Back", callback_data="menu_main")]
        ]
    else:
        # No hunt - show duration options
        display = """
╔════════════════════════════════╗
║ 🤖 AUTO HUNT
║
║ Select hunting duration:
║
║ Longer duration = More rewards
╚════════════════════════════════╝
"""
        keyboard = []
        for duration in AUTO_HUNT_DURATIONS:
            rate = (1.0 + (duration / 480) * 0.4)
            btn = InlineKeyboardButton(f"{duration}min (x{rate:.1f})", callback_data=f"autohunt_start_{duration}")
            keyboard.append([btn])
        
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="menu_main")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(display, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)

async def handle_autohunt_start(query, context: ContextTypes.DEFAULT_TYPE):
    """Handle auto hunt start"""
    user_id = query.from_user.id
    duration = int(query.data.replace("autohunt_start_", ""))
    
    # Check if already hunting
    current_hunt = auto_hunt_manager.get_hunt_status(user_id)
    if current_hunt and current_hunt["remaining_seconds"] > 0:
        await query.answer("❌ You already have an active hunt!", show_alert=True)
        return
    
    # Start hunt
    success = auto_hunt_manager.start_hunt(user_id, duration)
    
    if not success:
        await query.answer("❌ Failed to start hunt!", show_alert=True)
        return
    
    status = auto_hunt_manager.get_hunt_status(user_id)
    
    display = f"""
✅ Auto Hunt Started!

⏱️ Duration: {duration} minutes
📊 Rate: x{status['exp_rate']:.1f}
💰 Rewards:
  • {status['total_exp']:,} EXP
  • {status['total_meso']:,} Meso

You will be notified when complete!
"""
    
    await query.edit_message_text(display)
    
    # Schedule notification
    from datetime import datetime, timedelta
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    
    end_time = datetime.fromisoformat(status['end_time'])
    
    # Add job to check hunt completion (every 30 seconds)
    context.job_queue.run_repeating(
        check_hunt_complete,
        interval=30,
        first=30,
        context={"user_id": user_id, "chat_id": query.message.chat_id},
        name=f"hunt_{user_id}"
    )

async def handle_autohunt_refresh(query, context: ContextTypes.DEFAULT_TYPE):
    """Refresh auto hunt status"""
    user_id = query.from_user.id
    
    hunt_status = auto_hunt_manager.get_hunt_status(user_id)
    
    if not hunt_status:
        await query.answer("No active hunt!", show_alert=True)
        await show_autohunt_menu(query, context)
        return
    
    if hunt_status["remaining_seconds"] <= 0:
        # Hunt complete - claim rewards
        result = auto_hunt_manager.complete_hunt(user_id)
        
        display = f"""
🎉 AUTO HUNT COMPLETE!

{result['message']}

Total Playtime: {hunt_status['duration']} minutes
"""
        
        await query.edit_message_text(display)
        
        # Cancel job
        if context.job_queue:
            context.job_queue.get_jobs_by_name(f"hunt_{user_id}")[0].schedule_removal()
    else:
        # Still hunting
        display = auto_hunt_manager.format_hunt_display(user_id)
        
        keyboard = [
            [InlineKeyboardButton("🔄 Refresh", callback_data="autohunt_refresh")],
            [InlineKeyboardButton("⬅️ Back", callback_data="menu_main")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(display, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)

async def check_hunt_complete(context: ContextTypes.DEFAULT_TYPE):
    """Check if hunt is complete and notify user"""
    data = context.job.context
    user_id = data["user_id"]
    chat_id = data["chat_id"]
    
    hunt_status = auto_hunt_manager.get_hunt_status(user_id)
    
    if not hunt_status or hunt_status["remaining_seconds"] > 0:
        return
    
    # Hunt complete
    result = auto_hunt_manager.complete_hunt(user_id)
    
    from telegram import Bot
    bot = Bot(token=context.bot.token)
    
    message = f"""
🎉 **AUTO HUNT COMPLETE!**

{result['message']}

Total Playtime: {hunt_status['duration']} minutes

Use /menu to collect rewards!
"""
    
    await bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.MARKDOWN)
    
    # Cancel job
    context.job.schedule_removal()
