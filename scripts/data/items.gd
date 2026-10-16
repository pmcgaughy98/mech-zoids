extends RefCounted
## Items, parts and cores (Claude, 2026-10-13). DRAFT names, prices and numbers, Preston's to set.
##
## Structure from Zoids Legacy's player state and shops (read for structure only): recovery items used in or out of
## battle; equipment (parts) bought at weapon and armor shops and fitted into a machine's slots, each with a weight
## that counts against the machine's load capacity; machine cores, found or won, which with a machine's unlocked data
## let the lab build that machine. Quantities cap at QUANTITY_LIMIT, money at MONEY_LIMIT.

const QUANTITY_LIMIT := 99
const MONEY_LIMIT := 9999999
const STARTING_MONEY := 1500

const RECOVERY := {
	"repair_kit": {"name": "Repair Kit", "price": 60, "heal_pct": 30, "text": "Restore 30% of a machine's health."},
	"repair_crate": {"name": "Repair Crate", "price": 180, "heal_pct": 70, "text": "Restore 70% of a machine's health."},
	"energy_cell": {"name": "Energy Cell", "price": 80, "ep_pct": 50, "text": "Restore half a machine's energy."},
}

# slot: armor, booster, sensor, weapon. mods add to the machine's stats (power_pct scales weapon power).
const PARTS := {
	"plate_armor_1": {"name": "Plate Armor I", "slot": "armor", "weight": 12, "price": 300, "mods": {"defense": 6}},
	"plate_armor_2": {"name": "Plate Armor II", "slot": "armor", "weight": 20, "price": 700, "mods": {"defense": 12, "speed": -2}},
	"thruster_pack": {"name": "Thruster Pack", "slot": "booster", "weight": 10, "price": 450, "mods": {"speed": 5}},
	"target_sensor": {"name": "Targeting Sensor", "slot": "sensor", "weight": 6, "price": 400, "mods": {"accuracy": 6}},
	"coil_capacitor": {"name": "Coil Capacitor", "slot": "booster", "weight": 8, "price": 520, "mods": {"max_ep": 15, "ep_regen": 2}},
	"impact_rams": {"name": "Impact Rams", "slot": "weapon", "weight": 14, "price": 650, "mods": {"power_pct": 8}},
}

# A machine's slots, and its load capacity by size (machines.gd sizes). XL for later machines.
const SLOTS := ["armor", "booster", "sensor", "weapon"]
const LOAD_CAPACITY := {"S": 30, "M": 45, "L": 70, "XL": 100}

# Cores: with a machine's data unlocked, a core lets the lab build that machine. Keyed by machine id.
const CORES := {
	"ape_l": {"name": "Ape-line Core", "build_cost": 2000},
	"shoebill_m": {"name": "Wader-line Core", "build_cost": 1600},
	"pangolin_m": {"name": "Scale-line Core", "build_cost": 1600},
	"hippo_m": {"name": "River-line Core", "build_cost": 1600},
	"kangaroo_m": {"name": "Hopper-line Core", "build_cost": 1600},
	"wolf_m": {"name": "Pack-line Core", "build_cost": 1800},
}

const SHOP_ITEMS := ["repair_kit", "repair_crate", "energy_cell"]
const SHOP_PARTS := ["plate_armor_1", "plate_armor_2", "thruster_pack", "target_sensor", "coil_capacitor", "impact_rams"]


static func price_of(kind: String, id: String) -> int:
	return int((RECOVERY if kind == "items" else PARTS).get(id, {}).get("price", 0))
