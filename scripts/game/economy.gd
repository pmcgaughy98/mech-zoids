extends RefCounted
## Buying, selling and using things (Claude, 2026-10-13). Structure from Zoids Legacy's item and equipment shops
## (read for structure only): buy at price, sell back for half, quantities capped. DRAFT prices in items.gd.

const Items := preload("res://scripts/data/items.gd")
const Roster := preload("res://scripts/game/roster.gd")


static func _bag(run, kind: String) -> Dictionary:
	return run.items if kind == "items" else run.parts


## Buys one; returns "" or why not.
static func buy(run, kind: String, id: String) -> String:
	var price := Items.price_of(kind, id)
	if price <= 0:
		return "not sold here"
	if run.money < price:
		return "not enough credits"
	var bag := _bag(run, kind)
	if int(bag.get(id, 0)) >= Items.QUANTITY_LIMIT:
		return "carrying the most you can"
	run.money -= price
	bag[id] = int(bag.get(id, 0)) + 1
	if kind == "parts" and not run.catalog.parts.has(id):
		run.catalog.parts.append(id)
	return ""


## Sells one for half its price; returns "" or why not.
static func sell(run, kind: String, id: String) -> String:
	var bag := _bag(run, kind)
	if int(bag.get(id, 0)) <= 0:
		return "none to sell"
	bag[id] = int(bag[id]) - 1
	run.money = min(Items.MONEY_LIMIT, run.money + Items.price_of(kind, id) / 2)
	return ""


## Uses a recovery item on a battle unit (in battle) and returns the amount restored; -1 if it cannot.
static func use_on_unit(run, id: String, u: Dictionary) -> int:
	if int(run.items.get(id, 0)) <= 0 or not Items.RECOVERY.has(id):
		return -1
	var d: Dictionary = Items.RECOVERY[id]
	run.items[id] = int(run.items[id]) - 1
	if d.has("heal_pct"):
		var before: int = u.hp
		u.hp = min(u.max_hp, u.hp + int(u.max_hp * d.heal_pct / 100.0))
		return u.hp - before
	var e0: int = u.ep
	u.ep = min(u.max_ep, u.ep + int(u.max_ep * d.ep_pct / 100.0))
	return u.ep - e0
