"""Notification utilities for sending alerts to players"""
from telegram import Bot
from telegram.error import TelegramError
import logging

logger = logging.getLogger(__name__)

async def send_hunt_completion_notification(bot: Bot, chat_id: int, hunt_data: dict):
    """Send notification when auto hunt completes"""
    message = f"""
🎉 **AUTO HUNT COMPLETE!**

⏱️ Duration: {hunt_data['duration']} minutes
✨ EXP Gained: +{hunt_data['exp_gained']:,}
💰 Meso Gained: +{hunt_data['meso_gained']:,}

Total Playtime: {hunt_data['duration']} minutes

Use /menu to collect your rewards!
"""
    
    try:
        await bot.send_message(chat_id=chat_id, text=message, parse_mode="MARKDOWN")
    except TelegramError as e:
        logger.error(f"Failed to send notification to {chat_id}: {e}")

async def send_dungeon_result_notification(bot: Bot, chat_id: int, result: dict):
    """Send dungeon clear/defeat notification"""
    if result['won']:
        message = f"""
🎉 **DUNGEON CLEAR!**

Boss Defeated in {result['turns']} turns

Rewards:
✨ +{result['exp_reward']:,} EXP
💰 +{result['meso_reward']:,} Meso
"""
    else:
        message = f"""
💀 **DUNGEON DEFEAT**

You were defeated in {result['turns']} turns

Try again after leveling up!
"""
    
    try:
        await bot.send_message(chat_id=chat_id, text=message, parse_mode="MARKDOWN")
    except TelegramError as e:
        logger.error(f"Failed to send dungeon notification to {chat_id}: {e}")

async def send_quest_complete_notification(bot: Bot, chat_id: int, quest_name: str):
    """Send quest completion notification"""
    message = f"""
✅ **QUEST COMPLETE!**

{quest_name}

Use /menu → Quests to claim your reward!
"""
    
    try:
        await bot.send_message(chat_id=chat_id, text=message, parse_mode="MARKDOWN")
    except TelegramError as e:
        logger.error(f"Failed to send quest notification to {chat_id}: {e}")
