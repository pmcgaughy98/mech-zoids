"""Walk redo job for Codex (Claude, 2026-11-04). Preston: "walking needs redone".

The first walk (codex-set-a/walk) trotted in place but the front row barely moved, the diagonal pairs did not
match across rows and the rear legs shortened. This job reuses set A's prompt head, brief and refs and asks
for a walk whose lifted legs show in the front and back rows too. Output: codex-walk-b.
"""
import shutil
from pathlib import Path

ANIM = Path(__file__).parent
ROOT = "D:/dev/new-mech-rpg/docs/art/moba/rhino_l/take-a/anim"
OUT = ANIM / "codex-walk-b"

old = (ANIM / "codex-set-a/prompts/walk.txt").read_text(encoding="utf8")
head = old.split("2. Contact A")[0]
head = head.replace("trotting in place, a steady heavy trot where diagonal legs move together",
                    "walking in place with a heavy, deliberate stride where diagonal legs move together")
assert "walking in place" in head and head.rstrip().endswith("standing still with all four feet flat on the ground.")
cols = [
    "Step A, lift: one front leg and the opposite back leg lift together. Their feet are clearly off the ground, "
    "raised about a quarter of the leg's height, bent at the disc joints. The other two feet stay flat on the ground. "
    "Body slightly raised.",
    "Step A, reach: the lifted pair swings forward, feet still off the ground, the front foot reaching ahead. "
    "Body at its highest.",
    "Step A, plant: the swinging pair sets down ahead, all four feet on the ground, legs spread front to back. "
    "Body at its lowest.",
    "Step B, lift: the OTHER front leg and the OTHER back leg lift together, feet clearly off the ground and bent at "
    "the disc joints. The pair that just planted stays flat. Body slightly raised.",
    "Step B, reach: this pair swings forward, feet still off the ground. Body at its highest.",
    "Step B, plant: this pair sets down ahead, all four feet on the ground. Body at its lowest.",
]
rule = ("In the side view the swinging legs move forward and back. In the front view and the back view the same legs "
        "lift: the lifted feet sit clearly higher than the planted feet and the body bobs up and down, so the front "
        "and back rows change visibly from column to column and are never one pose repeated. Column for column, the "
        "same legs are lifted in all three rows. Every leg keeps its length in every column and every view: a lifted "
        "leg bends at its disc joint, it never gets shorter. Columns 2 to 7 loop. It walks in place and does not move "
        "across the cell. At least two feet touch the ground in every column.\n")
tail = "\nNo motion lines, no dust, no impact effect, no shadow, no other creature.\n"
prompt = head + "".join(f"{i + 2}. {c}\n" for i, c in enumerate(cols)) + rule + tail

brief = (ANIM / "codex-set-a/brief.txt").read_text(encoding="utf8")
swaps = [
    ("set A of two: rhino animation sheets", "walk redo: one rhino animation sheet"),
    ("this set makes: idle, walk, horn-jab, horn-toss. A second Codex job is making the other sheets in a sibling "
     "folder at the same time; do not touch it.",
     "this job makes only: walk. It replaces an earlier walk that Preston rejected because the front row barely "
     "moved, the diagonal leg pairs did not match across rows and the rear legs got shorter. No other job is running."),
    (f"{ROOT}/codex-set-a", f"{ROOT}/codex-walk-b"),
    ("idle: f0-f4, 220 ms each, loop; walk: f1-f6, 110 ms each, loop; horn-jab: f0-f5, 90 ms each with f0 held 400 ms; "
     "horn-toss: f0-f6, 100 ms each with f0 held 400 ms", "walk: f1-f6, 130 ms each, loop"),
    ("In the back row, do the legs keep their length?",
     "In every row, do the legs keep their length? In the front and back rows, do the lifted feet visibly rise and "
     "fall from column to column with the same timing as the side row?"),
]
for a, b in swaps:
    assert a in brief, a[:60]
    brief = brief.replace(a, b)
assert "codex-set-a" not in brief

(OUT / "prompts").mkdir(parents=True, exist_ok=True)
shutil.copytree(ANIM / "codex-ground-pound/refs", OUT / "refs", dirs_exist_ok=True)
(OUT / "prompts/walk.txt").write_text(prompt, encoding="utf8")
(OUT / "brief.txt").write_text(brief, encoding="utf8")
print(prompt)
print(len(brief), "chars of brief")
