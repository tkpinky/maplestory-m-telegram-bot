# Game Configuration
import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x]

# Game Constants
MAX_LEVEL = 250
TIMEZONE = "Asia/Shanghai"  # GMT+8

# Class Configuration
CLASSES = {
    "warrior": {
        "name": "⚔️ Warrior",
        "base_stats": {"str": 35, "dex": 20, "int": 20, "luk": 20, "hp": 500, "mp": 100},
        "equipment_allowed": ["weapon_sword", "armor_heavy", "helmet_heavy", "gloves_heavy", "shoes_heavy", "belt", "cape", "pendant", "ring", "earring"]
    },
    "mage": {
        "name": "🔥 Mage",
        "base_stats": {"str": 20, "dex": 20, "int": 35, "luk": 20, "hp": 250, "mp": 500},
        "equipment_allowed": ["weapon_staff", "armor_light", "helmet_light", "gloves_light", "shoes_light", "belt", "cape", "pendant", "ring", "earring"]
    },
    "archer": {
        "name": "🏹 Archer",
        "base_stats": {"str": 25, "dex": 35, "int": 20, "luk": 20, "hp": 350, "mp": 200},
        "equipment_allowed": ["weapon_bow", "armor_medium", "helmet_medium", "gloves_medium", "shoes_medium", "belt", "cape", "pendant", "ring", "earring"]
    },
    "thief": {
        "name": "🗡️ Thief",
        "base_stats": {"str": 20, "dex": 35, "int": 20, "luk": 25, "hp": 300, "mp": 150},
        "equipment_allowed": ["weapon_dagger", "armor_light", "helmet_light", "gloves_light", "shoes_light", "belt", "cape", "pendant", "ring", "earring"]
    },
    "bowmaster": {
        "name": "🎯 Bowmaster",
        "base_stats": {"str": 30, "dex": 35, "int": 20, "luk": 15, "hp": 400, "mp": 250},
        "equipment_allowed": ["weapon_crossbow", "armor_medium", "helmet_medium", "gloves_medium", "shoes_medium", "belt", "cape", "pendant", "ring", "earring"]
    }
}

# Equipment Configuration
EQUIPMENT_SLOTS = {
    "weapon": "🗡️ Weapon",
    "armor": "🛡️ Armor",
    "helmet": "👑 Helmet",
    "gloves": "🧤 Gloves",
    "shoes": "👟 Shoes",
    "belt": "⏸️ Belt",
    "cape": "🧥 Cape",
    "pendant": "📿 Pendant",
    "ring_1": "💍 Ring 1",
    "ring_2": "💍 Ring 2",
    "earring": "👂 Earring"
}

# Star Force Configuration
STAR_FORCE_RATES = {
    0: 0.95, 1: 0.95, 2: 0.95, 3: 0.95, 4: 0.95,
    5: 0.90, 6: 0.90, 7: 0.90, 8: 0.90, 9: 0.90,
    10: 0.85, 11: 0.85, 12: 0.85, 13: 0.85, 14: 0.85,
    15: 0.80, 16: 0.70, 17: 0.60, 18: 0.50, 19: 0.40,
    20: 0.30, 21: 0.20, 22: 0.15, 23: 0.10, 24: 0.05
}

STAR_FORCE_COSTS = {
    0: (100, 0), 1: (100, 0), 2: (100, 0), 3: (100, 0), 4: (100, 0),
    5: (500, 0), 6: (500, 0), 7: (500, 0), 8: (500, 0), 9: (500, 0),
    10: (2000, 0), 11: (2000, 100), 12: (2000, 200), 13: (3000, 300), 14: (3000, 400),
    15: (5000, 500), 16: (10000, 1000), 17: (15000, 1500), 18: (20000, 2000), 19: (30000, 3000),
    20: (50000, 5000), 21: (100000, 10000), 22: (150000, 15000), 23: (200000, 20000), 24: (300000, 30000)
}

# Auto Hunt Configuration
AUTO_HUNT_DURATIONS = [30, 60, 120, 240, 480]  # minutes: 30min, 1hr, 2hr, 4hr, 8hr
AUTO_HUNT_RATES = {
    30: 1.0, 60: 1.1, 120: 1.2, 240: 1.3, 480: 1.4  # EXP multiplier
}
AUTO_HUNT_ENERGY_PER_MINUTE = 0.5
MAX_ENERGY = 240  # 4 hours worth

# Dungeon Configuration
DUNGEONS = {
    "mushroom": {
        "name": "🍄 Mushroom Forest",
        "levels": "10-30",
        "difficulties": {
            "normal": {
                "min_level": 10,
                "boss_hp": 500,
                "boss_atk": 20,
                "boss_def": 10,
                "exp_reward": 1000,
                "meso_reward": 5000,
                "item_drop_rate": 0.3
            },
            "hard": {
                "min_level": 20,
                "boss_hp": 1000,
                "boss_atk": 35,
                "boss_def": 20,
                "exp_reward": 3000,
                "meso_reward": 15000,
                "item_drop_rate": 0.5
            }
        }
    },
    "kerning": {
        "name": "🏙️ Kerning City",
        "levels": "30-60",
        "difficulties": {
            "normal": {
                "min_level": 30,
                "boss_hp": 2000,
                "boss_atk": 40,
                "boss_def": 25,
                "exp_reward": 5000,
                "meso_reward": 20000,
                "item_drop_rate": 0.4
            },
            "hard": {
                "min_level": 45,
                "boss_hp": 4000,
                "boss_atk": 60,
                "boss_def": 40,
                "exp_reward": 15000,
                "meso_reward": 50000,
                "item_drop_rate": 0.6
            }
        }
    },
    "henesys": {
        "name": "🌳 Henesys",
        "levels": "60-100",
        "difficulties": {
            "normal": {
                "min_level": 60,
                "boss_hp": 5000,
                "boss_atk": 70,
                "boss_def": 40,
                "exp_reward": 15000,
                "meso_reward": 50000,
                "item_drop_rate": 0.45
            },
            "hard": {
                "min_level": 80,
                "boss_hp": 10000,
                "boss_atk": 100,
                "boss_def": 60,
                "exp_reward": 40000,
                "meso_reward": 120000,
                "item_drop_rate": 0.65
            }
        }
    }
}

# Daily Quests
DAILY_QUESTS = [
    {
        "id": "hunt_exp",
        "name": "Hunt for Experience",
        "description": "Gain 50,000 EXP",
        "target": 50000,
        "reward_exp": 5000,
        "reward_meso": 10000,
        "difficulty": "easy"
    },
    {
        "id": "dungeon_clear",
        "name": "Clear Dungeons",
        "description": "Clear 2 dungeons",
        "target": 2,
        "reward_exp": 8000,
        "reward_meso": 15000,
        "difficulty": "medium"
    },
    {
        "id": "boss_defeat",
        "name": "Defeat Bosses",
        "description": "Defeat 1 boss",
        "target": 1,
        "reward_exp": 10000,
        "reward_meso": 20000,
        "difficulty": "medium"
    },
    {
        "id": "star_force",
        "name": "Enhance Equipment",
        "description": "Upgrade equipment 3 times",
        "target": 3,
        "reward_exp": 5000,
        "reward_meso": 10000,
        "difficulty": "medium"
    },
    {
        "id": "auto_hunt",
        "name": "Use Auto Hunt",
        "description": "Complete 1 auto hunt session",
        "target": 1,
        "reward_exp": 3000,
        "reward_meso": 5000,
        "difficulty": "easy"
    },
    {
        "id": "equipment_change",
        "name": "Equip New Gear",
        "description": "Equip 2 new items",
        "target": 2,
        "reward_exp": 4000,
        "reward_meso": 8000,
        "difficulty": "easy"
    },
    {
        "id": "level_up",
        "name": "Gain Levels",
        "description": "Reach 2 level ups",
        "target": 2,
        "reward_exp": 7000,
        "reward_meso": 12000,
        "difficulty": "medium"
    },
    {
        "id": "hard_dungeon",
        "name": "Hard Dungeon Challenge",
        "description": "Clear 1 hard difficulty dungeon",
        "target": 1,
        "reward_exp": 12000,
        "reward_meso": 25000,
        "special_item": "rare_scroll",
        "difficulty": "hard"
    },
    {
        "id": "perfect_hunt",
        "name": "Perfect Hunt",
        "description": "Complete an 8-hour auto hunt",
        "target": 1,
        "reward_exp": 15000,
        "reward_meso": 30000,
        "special_item": "enhancement_scroll",
        "difficulty": "hard"
    },
    {
        "id": "full_clear",
        "name": "Full Clearance",
        "description": "Clear all dungeon runs (6 total)",
        "target": 6,
        "reward_exp": 20000,
        "reward_meso": 40000,
        "special_item": "star_protect_scroll",
        "difficulty": "hard"
    }
]

# NX & Premium Currency
TELEGRAM_STAR_TO_NX = 100  # 1 Telegram Star = 100 NX

# Protect Scroll costs
PROTECT_SCROLL_COST = (0, 300)  # (meso, nx)
