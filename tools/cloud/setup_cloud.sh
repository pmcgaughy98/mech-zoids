#!/bin/bash
# Set up a Claude Code cloud session (Linux container) to run the creature factory and the Godot checks
# (Claude, 2026-10-16). The PC keeps its own Blender and Godot; nothing here changes how the factory runs there.
#   bash tools/cloud/setup_cloud.sh        (about 3 minutes, idempotent)
# Installs:
#   - Godot 4.7.2 (the same build as the PC, Linux binary) at /opt/tools/godot
#   - Blender 5.2 as the bpy 5.2.2 Python module in /opt/tools/bpyenv, behind a `blender` command that takes the
#     factory's usual arguments (-b [file.blend] -P script.py -- args). download.blender.org is blocked by the
#     cloud proxy; PyPI is not.
#   - Mesa's software EGL so Blender's Workbench engine renders without a GPU (about 8 s a view).
#   - numpy, pillow, scipy for the pixelizers, and a `python` command.
# Then it writes LF copies of the CRLF shell scripts (tools/art/<name>.lf.sh, ignored by git) since bash on Linux
# chokes on CRLF. Export BLENDER=blender before running a factory script: the scripts default to the PC's path.
set -e
cd "$(dirname "$0")/../.."
mkdir -p /opt/tools
if [ ! -x /opt/tools/godot ]; then
  curl -sSL -o /opt/tools/godot.zip https://github.com/godotengine/godot-builds/releases/download/4.7.2-stable/Godot_v4.7.2-stable_linux.x86_64.zip
  unzip -q -o /opt/tools/godot.zip -d /opt/tools && mv /opt/tools/Godot_v4.7.2-stable_linux.x86_64 /opt/tools/godot && rm /opt/tools/godot.zip
fi
ln -sf /opt/tools/godot /usr/local/bin/godot
if ! dpkg -s libegl-mesa0 >/dev/null 2>&1; then
  (apt-get install -y -q libegl1 libegl-mesa0 libgl1-mesa-dri libgles2 libglx-mesa0 libxkbcommon0 libsm6 libxi6 libxxf86vm1 libxfixes3 libxrender1 >/dev/null 2>&1) || \
  (apt-get update -q >/dev/null 2>&1 && apt-get install -y -q libegl1 libegl-mesa0 libgl1-mesa-dri libgles2 libglx-mesa0 libxkbcommon0 libsm6 libxi6 libxxf86vm1 libxfixes3 libxrender1 >/dev/null)
fi
if [ ! -x /opt/tools/bpyenv/bin/python ]; then python3 -m venv /opt/tools/bpyenv; fi
/opt/tools/bpyenv/bin/pip install -q bpy==5.2.2 numpy pillow scipy
pip install -q numpy pillow scipy 2>/dev/null || pip install -q --break-system-packages numpy pillow scipy
command -v python >/dev/null || ln -sf "$(command -v python3)" /usr/local/bin/python
cp tools/cloud/blender_shim.py /opt/tools/blender_shim.py
printf '#!/bin/bash\nexec /opt/tools/bpyenv/bin/python /opt/tools/blender_shim.py "$@"\n' > /usr/local/bin/blender
chmod +x /usr/local/bin/blender
for f in tools/art/*.sh; do case "$f" in *.lf.sh) continue;; esac; tr -d '\r' < "$f" > "${f%.sh}.lf.sh"; done
grep -qx 'tools/art/\*.lf.sh' .git/info/exclude 2>/dev/null || echo 'tools/art/*.lf.sh' >> .git/info/exclude
godot --version; blender --python-expr "import bpy; print('blender', bpy.app.version_string)" 2>/dev/null | tail -1
echo "CLOUD_SETUP_DONE  (export BLENDER=blender GODOT=godot)"
