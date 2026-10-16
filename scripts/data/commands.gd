extends RefCounted
## Deck commands. Rule from Zoids Legacy's structure: equip up to DECK_LIMIT before a battle, each one works
## once per battle, and a side can play one per round. Names and effects are Claude placeholders.

const DECK_LIMIT := 10

const COMMANDS := {
	"shield_wall": {"name": "Shield Wall", "text": "Halve damage to your machine this round and next."},
	"field_repair": {"name": "Field Repair", "text": "Restore 35% of your machine's health."},
	"mine_field": {"name": "Mine Field", "text": "Enemies take damage at the start of their next 3 turns."},
	"power_surge": {"name": "Power Surge", "text": "Fill your machine's energy to full."},
	"air_lock": {"name": "Air Lock", "text": "Your weapons count as anti-air for the rest of the battle."},
}

# Given for winning a story battle (see Run.start_battle).
const REWARD_FIRST_BATTLE := "air_lock"

const STARTER_DECK := ["shield_wall", "field_repair", "mine_field", "power_surge"]
