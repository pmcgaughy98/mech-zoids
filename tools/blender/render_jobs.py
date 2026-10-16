# Many sprite renders in one Blender session (Claude, 2026-10-13): one launch per frame cost more than the frames.
#   blender -b -P tools/blender/render_jobs.py -- <file.blend> <jobs.txt> <out_dir>
# jobs.txt lines: "<anim name> <k> <blender clip> <frame>". Each job reopens the blend (render_sprite_views.py changes
# the scene) and runs the renderer with SPRITE_CLIP / SPRITE_FRAME / SPRITE_VIEWS=e / SPRITE_OUT=<out>/<anim>/<k>.
import bpy, os, runpy, sys
args = sys.argv[sys.argv.index("--") + 1:]
blend, jobs, out = (os.path.abspath(a) for a in args[:3])   # absolute: once a blend is open, Blender resolves relative paths against the drive root
renderer = os.path.join(os.path.dirname(os.path.abspath(__file__)), "render_sprite_views.py")
n = 0
for line in open(jobs, encoding="utf-8"):
    if not line.strip():
        continue
    name, k, clip, frame = line.split()
    bpy.ops.wm.open_mainfile(filepath=blend)
    d = os.path.join(out, name, k)
    os.makedirs(d, exist_ok=True)
    os.environ.update({"SPRITE_CLIP": clip, "SPRITE_FRAME": frame, "SPRITE_VIEWS": "e", "SPRITE_OUT": d})
    os.environ.pop("SPRITE_STANCE", None)
    runpy.run_path(renderer, run_name="__main__")
    n += 1
print("RENDER_JOBS_DONE", n)
