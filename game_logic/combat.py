"""Combat and boss raid mechanics"""
import random
from config import DUNGEONS

class BossFight:
    """Handles boss combat with phases and patterns"""
    
    def __init__(self, dungeon_id: str, difficulty: str, player_atk: int, player_def: int):
        self.dungeon_id = dungeon_id
        self.difficulty = difficulty
        
        dungeon = DUNGEONS.get(dungeon_id, {})
        diff_config = dungeon.get("difficulties", {}).get(difficulty, {})
        
        self.boss_hp = diff_config.get("boss_hp", 1000)
        self.boss_atk = diff_config.get("boss_atk", 20)
        self.boss_def = diff_config.get("boss_def", 10)
        self.max_boss_hp = self.boss_hp
        
        self.player_atk = player_atk
        self.player_def = player_def
        self.player_hp = 1000  # Temp, will be updated
        self.max_player_hp = 1000
        
        self.turn = 0
        self.phase = 1
        self.log = []
        
    def calculate_damage(self, attacker_atk: int, defender_def: int) -> int:
        """Calculate damage based on ATK and DEF"""
        base_damage = max(attacker_atk - (defender_def // 2), 1)
        variance = random.randint(-10, 20)  # 0-20% variance
        damage = int(base_damage * (1 + variance / 100))
        return max(damage, 1)
    
    def player_attack(self) -> str:
        """Player attacks boss"""
        self.turn += 1
        
        damage = self.calculate_damage(self.player_atk, self.boss_def)
        self.boss_hp -= damage
        
        msg = f"💥 You dealt {damage} damage!"
        self.log.append(msg)
        
        # Boss counter attack
        boss_damage = self.calculate_damage(self.boss_atk, self.player_def)
        self.player_hp -= boss_damage
        
        msg += f"\n😤 Boss dealt {boss_damage} damage!"
        self.log.append(msg)
        
        # Check phase change
        self._check_phase()
        
        return msg
    
    def _check_phase(self):
        """Check if boss should change phase"""
        hp_percent = (self.boss_hp / self.max_boss_hp) * 100
        
        if hp_percent <= 66 and self.phase == 1:
            self.phase = 2
            self.boss_atk = int(self.boss_atk * 1.2)  # Boss gets stronger
            self.log.append("⚠️ Boss enters Phase 2! More aggressive!")
        elif hp_percent <= 33 and self.phase == 2:
            self.phase = 3
            self.boss_atk = int(self.boss_atk * 1.2)  # Boss gets even stronger
            self.log.append("🔴 Boss enters Phase 3! Extreme danger!")
    
    def is_player_alive(self) -> bool:
        """Check if player is still alive"""
        return self.player_hp > 0
    
    def is_boss_alive(self) -> bool:
        """Check if boss is still alive"""
        return self.boss_hp > 0
    
    def get_status(self) -> str:
        """Get current combat status"""
        player_hp_percent = (self.player_hp / self.max_player_hp) * 100
        boss_hp_percent = max(0, (self.boss_hp / self.max_boss_hp) * 100)
        
        player_bar = "█" * int(player_hp_percent / 10) + "░" * (10 - int(player_hp_percent / 10))
        boss_bar = "█" * int(boss_hp_percent / 10) + "░" * (10 - int(boss_hp_percent / 10))
        
        status = f"""
╔════════════════════════════════╗
║ BOSS RAID - Phase {self.phase}
║
║ YOUR HP: [{player_bar}]
║ {self.player_hp}/{self.max_player_hp}
║
║ BOSS HP: [{boss_bar}]
║ {max(0, self.boss_hp)}/{self.max_boss_hp}
║
║ Turn: {self.turn}
╚════════════════════════════════╝
"""
        return status

def simulate_boss_fight(dungeon_id: str, difficulty: str, player_atk: int, player_def: int, player_hp: int) -> dict:
    """Simulate a complete boss fight"""
    fight = BossFight(dungeon_id, difficulty, player_atk, player_def)
    fight.player_hp = player_hp
    fight.max_player_hp = player_hp
    
    turns = 0
    max_turns = 100  # Prevent infinite loops
    
    while fight.is_boss_alive() and fight.is_player_alive() and turns < max_turns:
        fight.player_attack()
        turns += 1
    
    result = {
        "won": fight.is_boss_alive() == False and fight.is_player_alive() == True,
        "turns": turns,
        "player_hp_remaining": max(0, fight.player_hp),
        "boss_hp_remaining": max(0, fight.boss_hp),
        "phase": fight.phase,
        "log": fight.log
    }
    
    return result

def calculate_player_stats(user: dict, equipment: list) -> dict:
    """Calculate total player stats with equipment bonuses"""
    from config import CLASSES
    
    class_data = CLASSES.get(user["class"], {})
    base_stats = class_data.get("base_stats", {})
    
    stats = {
        "str": base_stats.get("str", 20),
        "dex": base_stats.get("dex", 20),
        "int": base_stats.get("int", 20),
        "luk": base_stats.get("luk", 20),
        "atk": 0,
        "def": 0,
        "hp": base_stats.get("hp", 300),
        "mp": base_stats.get("mp", 100)
    }
    
    # Add equipment bonuses
    for item in equipment:
        stats["atk"] += item.get("atk", 0)
        stats["def"] += item.get("def", 0)
        stats["hp"] += item.get("hp_bonus", 0)
        stats["mp"] += item.get("mp_bonus", 0)
        stats["str"] += item.get("str_bonus", 0)
        stats["dex"] += item.get("dex_bonus", 0)
        stats["int"] += item.get("int_bonus", 0)
        stats["luk"] += item.get("luk_bonus", 0)
    
    # ATK calculation: base + (STR * 0.5) + equipment
    stats["atk"] += int(stats["str"] * 0.5)
    
    # DEF calculation: base + (DEX * 0.25) + equipment
    stats["def"] += int(stats["dex"] * 0.25)
    
    return stats
