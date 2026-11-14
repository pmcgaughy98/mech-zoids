"""Squirrel cleanup, adapted from wolf take B: whole-sheet nearest-solid-colour cleanup.
Checks every colour, dark plum and internal leg gaps, not one historical RGB.
Alpha and silhouettes stay fixed.
"""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy import ndimage
HERE = Path(__file__).resolve().parent

def clean(px):
    solid = px[..., 3] > 0
    rgb = px[..., :3].astype(float)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    bad = solid & (r - g > 25) & (b - g > 25) & (r > b * .85)
    # The mech's near-black is deliberate internal ink, never magenta fringe.
    bad &= ~np.all(px[..., :3] == (20, 18, 24), axis=2)
    good = solid & ~bad
    if bad.any() and not good.any():
        raise ValueError("No clean palette pixels remain")
    out = px.copy()
    if bad.any():
        idx = ndimage.distance_transform_edt(~good, return_distances=False, return_indices=True)
        out[bad] = px[idx[0][bad], idx[1][bad]]
    assert np.array_equal(out[..., 3], px[..., 3])
    # A lone pale rim pixel has no same-colour neighbour in its 8-neighbourhood.
    edge = solid & ~ndimage.binary_erosion(solid)
    # The prompt reserves ink for overlaps inside the body, never the silhouette.
    ink = solid & np.all(out[..., :3] == (20, 18, 24), axis=2)
    rim_ink = edge & ink
    if rim_ink.any():
        donor = solid & ~ink
        idx = ndimage.distance_transform_edt(~donor, return_distances=False, return_indices=True)
        out[rim_ink] = out[idx[0][rim_ink], idx[1][rim_ink]]
    pale = solid & (np.dot(out[..., :3], [0.2126, 0.7152, 0.0722]) >= 145)
    lone = np.zeros(solid.shape, bool)
    for colour in np.unique(out[pale, :3], axis=0):
        same = solid & np.all(out[..., :3] == colour, axis=2)
        neighbours = ndimage.convolve(same.astype(int), np.ones((3,3),int), mode='constant') - same
        lone |= same & edge & (neighbours == 0) & ~np.isin(out[...,:3].dot(np.array([65536,256,1])),[0x5ff0ff,0xe8ffff])
    donor = solid & ~pale & ~np.all(out[..., :3] == (20, 18, 24), axis=2)
    # Keep every material on its own ramp, including pale rim cleanup.
    roles={tuple(bytes.fromhex(c['hex'])):c['role'] for c in json.loads((HERE/'palette.json').read_text())}
    for colour in np.unique(out[lone,:3],axis=0):
        local=lone & np.all(out[...,:3]==colour,axis=2)
        own=np.zeros(solid.shape,bool)
        for rgb,role in roles.items():
            if role==roles.get(tuple(colour)): own |= solid & ~lone & np.all(out[...,:3]==rgb,axis=2)
        same_here=solid & np.all(out[...,:3]==colour,axis=2)
        own &= ~same_here
        if own.any():
            idx=ndimage.distance_transform_edt(~own,return_distances=False,return_indices=True)
            out[local]=out[idx[0][local],idx[1][local]]
    # Isolated neutral flecks wholly surrounded by another material are colour
    # classification noise, not steel parts: restore the surrounding ramp.
    for y,x in zip(*np.where(lone)):
        y0,y1=max(0,y-1),min(out.shape[0],y+2); x0,x1=max(0,x-1),min(out.shape[1],x+2)
        local=out[y0:y1,x0:x1]; neighbours=local[local[...,3]>0]
        here=roles.get(tuple(out[y,x,:3]))
        if not any(roles.get(tuple(c[:3]))==here and not np.array_equal(c[:3],out[y,x,:3]) for c in neighbours):
            other=[tuple(c) for c in neighbours if roles.get(tuple(c[:3])) not in (here,'eye','accent')]
            if other:
                from collections import Counter
                out[y,x]=Counter(other).most_common(1)[0][0]
    original_lone=lone.copy()
    lone[:]=False
    if lone.any():
        idx = ndimage.distance_transform_edt(~donor, return_distances=False, return_indices=True)
        out[lone] = out[idx[0][lone], idx[1][lone]]
    return out, int(bad.sum()), int(original_lone.sum()), int(rim_ink.sum())

if __name__ == "__main__":
    path = HERE / "sheet_finished.png"
    px, count, pale_count, ink_count = clean(np.array(Image.open(path).convert("RGBA")))
    Image.fromarray(px).save(path)
    result = {"plum_or_magenta_pixels_repainted": count,
              "remaining_plum_or_magenta_pixels": clean(px)[1], "lone_pale_edge_pixels_repainted": pale_count,
              "remaining_lone_pale_edge_pixels": clean(px)[2],
              "dark_ink_rim_pixels_repainted": ink_count,
              "remaining_dark_ink_rim_pixels": clean(px)[3], "alpha_unchanged": True}
    (HERE / "defringe.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result))
