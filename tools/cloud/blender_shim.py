# Blender command-line shim over the bpy module for cloud sessions (tools/cloud/setup_cloud.sh). Takes the
# arguments the factory passes to blender.exe: -b [file.blend] -P script.py [-- script args].
import sys, runpy
argv = sys.argv[1:]
blend = None; script = None; py_expr = None
i = 0
while i < len(argv):
    a = argv[i]
    if a == "--": break
    if a in ("-b", "--background", "--factory-startup", "-noaudio"): i += 1; continue
    if a in ("-P", "--python"): script = argv[i+1]; i += 2; continue
    if a == "--python-expr": py_expr = argv[i+1]; i += 2; continue
    if a in ("-t", "--threads", "-E", "--engine"): i += 2; continue
    if a.endswith(".blend"): blend = a; i += 1; continue
    i += 1
import bpy
if blend: bpy.ops.wm.open_mainfile(filepath=blend)
sys.argv = ["blender"] + argv
if py_expr: exec(py_expr, {"__name__": "__main__"})
if script:
    runpy.run_path(script, run_name="__main__")
