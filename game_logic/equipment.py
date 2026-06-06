"""Equipment and Star Force enhancement system"""
import random
import database as db
from config import STAR_FORCE_RATES, STAR_FORCE_COSTS

def can_enhance(equipment_id: int, user_id: int) -> bool:
    """Check if equipment can be enhanced"""
    conn = db.sqlite3.connect(db.DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT stars FROM equipment WHERE id = ? AND user_id = ?
    """, (equipment_id, user_id))
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return False
    
    stars = result[0]
    return stars < 24  # Max 24 stars (can go to 25)

def get_enhancement_cost(stars: int) -> tuple:
    """Get cost for enhancing to next star"""
    if stars >= 24:
        return None
    
    return STAR_FORCE_COSTS.get(stars, (1000, 0))

def get_success_rate(stars: int) -> float:
    """Get success rate for enhancing to next star"""
    if stars >= 24:
        return 0.0
    
    return STAR_FORCE_RATES.get(stars, 0.5)

def enhance_equipment(equipment_id: int, user_id: int, use_protect_scroll: bool = False) -> dict:
    """
    Attempt to enhance equipment
    
    Returns:
        {
            "success": bool,
            "new_stars": int,
            "result": "success" | "fail_downgrade" | "fail_break",
            "message": str
        }
    """
    conn = db.sqlite3.connect(db.DB_PATH)
    conn.row_factory = db.sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT stars, name FROM equipment WHERE id = ? AND user_id = ?
    """, (equipment_id, user_id))
    
    equipment = cursor.fetchone()
    conn.close()
    
    if not equipment:
        return {"success": False, "result": "error", "message": "Equipment not found"}
    
    current_stars = equipment["stars"]
    
    if current_stars >= 24:
        return {"success": False, "result": "error", "message": "Equipment is already max stars"}
    
    # Get costs
    meso_cost, nx_cost = get_enhancement_cost(current_stars)
    
    # Check player resources
    user = db.get_user(user_id)
    if user["meso"] < meso_cost:
        return {"success": False, "result": "error", "message": f"Not enough Meso. Need {meso_cost:,}, have {user['meso']:,}"}
    
    if user["nx"] < nx_cost:
        return {"success": False, "result": "error", "message": f"Not enough NX. Need {nx_cost}, have {user['nx']}"}
    
    # Check protect scroll cost
    if use_protect_scroll:
        protect_meso, protect_nx = (0, 300)  # From config
        if user["nx"] < protect_nx + nx_cost:
            return {"success": False, "result": "error", "message": "Not enough NX for protect scroll and enhancement"}
    
    # Deduct costs
    db.subtract_meso(user_id, meso_cost)
    db.subtract_nx(user_id, nx_cost)
    
    if use_protect_scroll:
        db.subtract_nx(user_id, 300)
    
    # Attempt enhancement
    success_rate = get_success_rate(current_stars)
    is_success = random.random() < success_rate
    
    if is_success:
        # Success
        new_stars = current_stars + 1
        db.update_equipment_stars(equipment_id, new_stars)
        
        return {
            "success": True,
            "result": "success",
            "new_stars": new_stars,
            "message": f"✅ Success! {equipment['name']} enhanced to ⭐{new_stars}!"
        }
    else:
        # Failure
        if use_protect_scroll:
            # Protect scroll prevents downgrade
            return {
                "success": False,
                "result": "fail_protected",
                "new_stars": current_stars,
                "message": f"❌ Enhancement failed, but protect scroll saved your item!"
            }
        else:
            # Random: downgrade or break
            if random.random() < 0.7:  # 70% downgrade
                if current_stars > 0:
                    new_stars = current_stars - 1
                    db.update_equipment_stars(equipment_id, new_stars)
                    return {
                        "success": False,
                        "result": "fail_downgrade",
                        "new_stars": new_stars,
                        "message": f"❌ Enhancement failed! {equipment['name']} downgraded to ⭐{new_stars}"
                    }
                else:
                    # Can't downgrade from 0, so just fail
                    return {
                        "success": False,
                        "result": "fail_noop",
                        "new_stars": 0,
                        "message": f"❌ Enhancement failed! {equipment['name']} is destroyed!"
                    }
            else:  # 30% break
                db.update_equipment_stars(equipment_id, -1)  # This deletes the item
                return {
                    "success": False,
                    "result": "fail_break",
                    "new_stars": -1,
                    "message": f"💔 Critical failure! {equipment['name']} is destroyed!"
                }

def get_total_stats(equipment_list: list) -> dict:
    """Calculate total stats from all equipment"""
    stats = {
        "atk": 0,
        "def": 0,
        "hp_bonus": 0,
        "mp_bonus": 0,
        "str_bonus": 0,
        "dex_bonus": 0,
        "int_bonus": 0,
        "luk_bonus": 0
    }
    
    for item in equipment_list:
        for key in stats:
            stats[key] += item.get(key, 0)
    
    return stats

def match_equipment_to_class(user_class: str, equipment_slot: str) -> bool:
    """Check if equipment matches character class"""
    from config import CLASSES
    
    class_data = CLASSES.get(user_class, {})
    allowed_items = class_data.get("equipment_allowed", [])
    
    return equipment_slot in allowed_items
