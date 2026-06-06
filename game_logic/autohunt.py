"""Auto Hunt system - real-time hunting with notifications"""
import asyncio
from datetime import datetime, timedelta
import database as db
from config import AUTO_HUNT_DURATIONS, AUTO_HUNT_RATES

class AutoHuntManager:
    """Manages auto hunt sessions"""
    
    def __init__(self):
        self.active_hunts = {}  # user_id -> hunt_data
    
    def start_hunt(self, user_id: int, duration: int):
        """Start a new auto hunt session"""
        if duration not in AUTO_HUNT_DURATIONS:
            return False
        
        db.start_auto_hunt(user_id, duration)
        self.active_hunts[user_id] = {
            "duration": duration,
            "start_time": datetime.now(),
            "exp_rate": AUTO_HUNT_RATES.get(duration, 1.0)
        }
        
        return True
    
    def get_hunt_status(self, user_id: int) -> dict:
        """Get current hunt status"""
        hunt_data = db.get_auto_hunt(user_id)
        
        if not hunt_data:
            return None
        
        start_time = datetime.fromisoformat(hunt_data["start_time"])
        duration = hunt_data["duration"]
        end_time = start_time + timedelta(minutes=duration)
        now = datetime.now()
        
        elapsed = (now - start_time).total_seconds()
        total_seconds = duration * 60
        remaining = max(0, (end_time - now).total_seconds())
        
        # Calculate base rewards: 100 EXP per minute, multiplied by duration rate
        base_exp = duration * 100
        exp_rate = AUTO_HUNT_RATES.get(duration, 1.0)
        total_exp = int(base_exp * exp_rate)
        
        # Meso: 500 per minute
        total_meso = duration * 500
        
        # Progress calculation
        progress_percent = min(100, (elapsed / total_seconds) * 100)
        
        return {
            "duration": duration,
            "elapsed_seconds": elapsed,
            "remaining_seconds": remaining,
            "progress_percent": progress_percent,
            "total_exp": total_exp,
            "total_meso": total_meso,
            "exp_rate": exp_rate,
            "end_time": end_time.isoformat()
        }
    
    def is_hunt_complete(self, user_id: int) -> bool:
        """Check if hunt session is complete"""
        status = self.get_hunt_status(user_id)
        
        if not status:
            return False
        
        return status["remaining_seconds"] <= 0
    
    def complete_hunt(self, user_id: int) -> dict:
        """Complete hunt and grant rewards"""
        status = self.get_hunt_status(user_id)
        
        if not status:
            return {"success": False, "message": "No active hunt"}
        
        # Grant rewards
        db.add_exp(user_id, status["total_exp"])
        db.add_meso(user_id, status["total_meso"])
        
        # Update quest progress
        db.update_quest_progress(user_id, "auto_hunt", 1)
        
        # Remove hunt
        db.complete_auto_hunt(user_id, 0, 0)  # Already added exp/meso
        
        if user_id in self.active_hunts:
            del self.active_hunts[user_id]
        
        return {
            "success": True,
            "exp_gained": status["total_exp"],
            "meso_gained": status["total_meso"],
            "message": f"✅ Auto Hunt Complete!\n+{status['total_exp']:,} EXP\n+{status['total_meso']:,} Meso"
        }
    
    def format_hunt_display(self, user_id: int) -> str:
        """Format hunt status for display"""
        status = self.get_hunt_status(user_id)
        
        if not status:
            return "No active auto hunt"
        
        remaining = status["remaining_seconds"]
        hours = int(remaining // 3600)
        minutes = int((remaining % 3600) // 60)
        seconds = int(remaining % 60)
        
        exp_bar_fill = int(status["progress_percent"] / 5)
        exp_bar = "█" * exp_bar_fill + "░" * (20 - exp_bar_fill)
        
        display = f"""
╔════════════════════════════════╗
║ 🤖 AUTO HUNT IN PROGRESS
║
║ Progress: [{exp_bar}]
║ {status['progress_percent']:.0f}% - {hours}h {minutes}m {seconds}s remaining
║
║ ⏱️  Duration: {status['duration']} minutes
║ 📊 Rate: x{status['exp_rate']:.1f}
║
║ 💰 Rewards:
║ EXP: +{status['total_exp']:,}
║ Meso: +{status['total_meso']:,}
╚════════════════════════════════╝
"""
        return display

# Global auto hunt manager
auto_hunt_manager = AutoHuntManager()
