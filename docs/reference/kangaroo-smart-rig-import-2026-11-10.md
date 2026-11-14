# Kangaroo Meshy Smart Rig import check

Preston reports liking Meshy's Smart Rig skeleton but losing it when importing into MeshForge to touch up joints.

## Actual file and test

Inspected `D:/user/Downloads/kangaroo_front - Hunyuan 3D v3.1 Pro.glb`, downloaded 2026-11-10. SHA-256: `7e4de6f249d90753b5380e8fae775ef86020bbc2bea989035333b825aee931c4`.

It contains one glTF skin, **29 joints**, inverse bind matrices and JOINTS_0/WEIGHTS_0 on the mesh. No animation clips. Names are generic Bone_000 through Bone_028. This is different from the older static kangaroo source archived in the model catalog; do not overwrite that archive.

Imported a separate copy through the MeshForge MCP, named `Kangaroo Smart Rig compatibility test (copy)` (library id `edd3b524de0b`, connector profile). MeshForge reports rigged=true, bones=29, 24,973 triangles. getSkeleton returns all 29 bones and their parent relationships. Its inferred roles are hips for Bone_000 and null for the remaining 28; feet=[] and rigDraft=null.

Thus **the rig was not stripped in this test**. Automatic anatomical role recognition is incomplete. The connector profile is separate from Preston's usual browser library, so this does not certify that every import path behaves identically.

MeshForge's current docs say an already-bound imported rig opens at the weights step. Its draft joint tools place/move a template before binding. Starting a new template/bind workflow is not evidence that the existing Meshy skeleton can be edited in place. No re-rig, remesh, binding, weight changes, animation generation or paid job was performed.

## Editable preserved master

`D:/dev/_scratch/kangaroo-smart-rig-2026-11-10/kangaroo-smart-rig-touchup.blend`

Blender 5.2 workspace imports the actual Smart Rig GLB. Original armature is selected, with bones visible through the mesh. Four catalog generation sheets are packed and arranged alongside it; textures are packed. Original bone names, hierarchy, rest heads/tails, mesh coordinates and vertex weights were checked unchanged during workspace preparation. See `preservation.json` and `prepare_workspace.py` beside it.

This is a touch-up workspace, not a completed rig correction. Move rest joints in Armature Edit Mode, inspect and adjust weights separately where needed, and flex-test limbs/tail before exporting. Changes to a rest skeleton can affect deformation and existing animation compatibility; do not promise edits preserve every clip unchanged.

For the shared manufacture route, Meshy Smart Rig can provide the initial skeleton, Blender is the editable rig/weight master, and a validated GLB is registered into the game. Anatomical role mapping for MeshForge can be tested on a separate copy after reviewing which generic bones correspond to each limb. Do not rename them by numeric order or replace them with a humanoid template automatically.

Official references checked 2026-11-10:

- [Meshy rigging](https://docs.meshy.ai/en/webapp/guides/3d-model/rigging): Smart Rig Beta exports GLB only and cannot use Meshy's animation library; custom rig work belongs in a DCC.
- [MeshForge rigging/import docs](https://www.keyframe.it.com/docs/meshforge): GLB import, existing rigs at the weight step, draft-joint/bind workflow.
