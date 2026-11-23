class_name MatchRules
extends RefCounted
## Every number the match runs on (Claude, 2026-11-04, game feel lane; Mech-Zoids' brief for Preston's "sel-out moba map").
## EVERY NUMBER HERE IS A PLACEHOLDER. Preston sets the real ones. Each says where it came from:
##   2D: the approved 2D skeleton (scripts/moba/*.gd)       brief: Mech-Zoids' brief, 2026-11-04
##   map: the map lane (scenes/moba3d/arena_blockout.gd)    doc: docs/plan/moba-kits.md
##   pick: chosen here only so the match can be played
## They are static vars, not consts, so the checks can shorten a timer.

# ---- waves (2D: lane_spawner.gd) --------------------------------------------------------------------------------------
static var first_wave_at := 5.0 ## pick: seconds into the match
static var wave_interval := 30.0 ## brief and 2D
static var wave_size := 3 ## 2D
static var wave_stagger := 0.8 ## pick: seconds between the minions of one wave leaving the gate

# ---- minions (2D: moba_unit.gd) ---------------------------------------------------------------------------------------
static var minion_hp := 300.0 ## 2D
static var minion_damage := 20.0 ## 2D
static var pit_wave_bonus := 0.25 ## map lane's start: each side pit a team holds adds this share to its new minions' hp and damage (Preston picked the pit capture, 2026-11-05)
static var beacon_tower_off := 30.0 ## pick (map lane's start): seconds the plaza beacon switches the other team's tower off
static var minion_cooldown := 1.0 ## 2D
static var minion_range := 4.0 ## pick: the drone's blaster reach, middle to the target's edge (2D had 24 px)
static var minion_speed := 3.5 ## map: the pace that brings both waves to the plaza about 20 s out
static var minion_sight := 7.0 ## pick (2D had 110 px)

# ---- towers and cores ---------------------------------------------------------------------------------------------------
static var tower_range := 12.0 ## brief and map (read from the marker's "range" meta when the map lane sets it)
static var tower_hp := 2000.0 ## pick
static var tower_damage := 60.0 ## pick
static var tower_cooldown := 1.2 ## pick
static var tower_bolt_speed := 24.0 ## pick: metres per second
static var tower_switch_time := 4.0 ## pick: how long a tower stays on a machine that hit an allied machine
static var core_hp := 3000.0 ## pick

# ---- machines ------------------------------------------------------------------------------------------------------------
static var machine_hp := 600.0 ## pick: the same for every machine until Preston sets them
static var kit_hit_damage := 60.0 ## pick: one kit hit; the kits carry no damage numbers yet
static var blocked_share := 0.5 ## pick: what a hit the front plating, brace or a hex shield takes still does
static var basic_damage := 30.0 ## pick: the stand-in basic attack (a test shot); no machine has a real one yet
static var basic_range := 6.0 ## pick
static var basic_cooldown := 0.9 ## pick
static var slow_mult := 0.6 ## pick: speed while slowed
static var respawn_time := 8.0 ## pick
static var base_heal_radius := 9.0 ## pick: from the team's spawn
static var base_heal_share := 0.2 ## pick: share of full health healed per second at base
static var recall_time := 4.0 ## pick
static var vision_machine := 12.0 ## pick: the map lane's fog reads it
static var vision_minion := 8.0 ## pick

## The doc gives each ability a tier, not seconds (doc: "short, medium, long"). The seconds are picks.
static var tier_seconds := {"short": 5.0, "short-medium": 7.0, "medium": 9.0, "medium-long": 12.0, "long": 40.0}
const TIERS := { ## doc, per slot
	"rhino": {"1": "medium", "2": "short", "3": "medium-long", "4": "long"},
	"gorilla": {"1": "short-medium", "2": "medium", "3": "medium", "4": "long"},
	"fennec": {"1": "short", "2": "short-medium", "3": "long", "4": "long"},
	"kangaroo": {"1": "medium", "2": "medium", "3": "medium", "4": "long"}, ## the kit doc's words; slot 1 medium (9 s) once it became a 10 m leap (Preston, 2026-11-11: "Yes, 9 s")
	"wolf": {"1": "short", "2": "medium", "3": "medium-long", "4": "long"}, ## Wolf Session, from the doc, 2026-11-05
	"hummingbird": {"1": "short", "2": "medium", "3": "short-medium", "4": "long"}, ## Hummingbird session, doc tier words, 2026-11-05
	"shoebill": {"1": "short", "2": "medium", "3": "medium", "4": "long"}, ## Shoebill session, doc tier words, 2026-11-05
	"squirrel": {"1": "short", "2": "short-medium", "3": "medium-long", "4": "long"}, ## Squirrel session, the tiers Preston took ("Take it"), 2026-11-05
	"falcon": {"1": "short", "2": "medium", "3": "medium", "4": "long"}, ## Falcon session, doc tier words, 2026-11-05
	"hippo": {"1": "short", "2": "medium", "3": "medium-long", "4": "long"}, ## Hippo session, doc tier words (kit rework undecided), 2026-11-05
	"bison": {"1": "medium", "2": "medium", "3": "short", "4": "long"}, ## moba-kits.md (the Whistle Stop refine, 2026-11-14); all four built
	"pangolin": {"1": "short", "2": "medium", "3": "medium", "4": "long"}, ## kit redo (Preston approved 2026-11-12): the spec gives the iron ball "about 9 s", the medium tier here
}
## rhino 3 is Aftershock since 2026-11-20: kit design's "about 11 s" sits in medium-long (12 s); there is no 11 s tier.

## The slots that move the caster itself, which grounded (the rhino's Aftershock) blocks: dashes, leaps, rolls, blinks
## and long carries (kit design, 2026-11-20; docs/plan/rhino-brace-replacement-2026-11-20.md, "Grounded rules"). The
## bison's Chain (1) is not one: its haul is about the hook. Its Plow and every basic attack are not either.
const MOBILITY := {
	"rhino": ["1", "4"], ## Horn Toss's dash; Stampede and its Tremor charge
	"gorilla": ["3"], ## Drive Slam (its grab only chains off the drive)
	"kangaroo": ["1", "4"], ## Hop and Jab; Boxing Ring
	"hippo": ["2", "3"], ## Piston Drop; Lockjaw's carry
	"pangolin": ["2", "4"], ## Iron Ball; Scrap Comet (a mid-roll Scale Flare ends with the roll)
	"fennec": ["2", "3"], ## Blink Gate and its Gate Back recast; Tunnel
	"wolf": ["1"], ## Lunge
	"bison": ["4"], ## Freight
}


static func is_mobility(machine: String, slot: String) -> bool:
	return slot in MOBILITY.get(machine, [])

# ---- jungle --------------------------------------------------------------------------------------------------------------
static var monster_hp := 500.0 ## pick
static var monster_damage := 30.0 ## pick
static var monster_cooldown := 1.3 ## pick
static var monster_range := 1.2 ## pick
static var monster_speed := 3.0 ## pick
static var monster_leash := 10.0 ## pick: metres from its camp before it walks home and heals
static var monster_respawn := 60.0 ## pick


static func cooldown(machine: String, slot: String) -> float:
	var tier: String = TIERS.get(machine, {}).get(slot, "medium")
	return float(tier_seconds.get(tier, 9.0))
