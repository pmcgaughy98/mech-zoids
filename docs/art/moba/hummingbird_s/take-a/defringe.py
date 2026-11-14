"""Hummingbird cleanup, adapted from falcon take B: whole-sheet nearest-solid-colour cleanup.
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
    px = px.copy()
    solid = px[..., 3] > 0
    # Restrict the lens palette to actual lens clusters. Quantization can assign
    # steel glints or green rim antialiasing to cyan; those are not eyes.
    cyan = solid & np.all(px[..., :3] == (74,240,255), axis=2)
    glint = solid & np.all(px[..., :3] == (232,255,255), axis=2)
    lab, total = ndimage.label(cyan)
    sizes = np.bincount(lab.ravel())
    core = cyan & (sizes[lab] >= 8)
    core[:px.shape[0]//3] = False  # rear views cannot show lenses
    eye_ok = ndimage.binary_dilation(core, iterations=3) & (cyan | glint)
    stray = (cyan | glint) & ~eye_ok
    ruby = solid & (px[...,0] > px[...,1]*1.3) & (px[...,0] > 100)
    rl, _ = ndimage.label(ruby)
    rs = np.bincount(rl.ravel())
    stray |= ruby & (rs[rl] < 8)
    donor = solid & ~stray & ~(cyan | glint)
    idx = ndimage.distance_transform_edt(~donor, return_distances=False, return_indices=True)
    px[stray] = px[idx[0][stray],idx[1][stray]]
    rgb = px[..., :3].astype(float)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    bad = solid & (r - g > 25) & (b - g > 25) & (b > r * .65)
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
    eye = np.all(out[..., :3] == (74,240,255), axis=2) | np.all(out[..., :3] == (232,255,255), axis=2)
    pale = solid & ~eye & (np.dot(out[..., :3], [0.2126, 0.7152, 0.0722]) >= 145)
    lone = np.zeros(solid.shape, bool)
    for colour in np.unique(out[pale, :3], axis=0):
        same = solid & np.all(out[..., :3] == colour, axis=2)
        neighbours = ndimage.convolve(same.astype(int), np.ones((3,3),int), mode='constant') - same
        lone |= same & edge & (neighbours == 0)
    donor = solid & ~pale & ~np.all(out[..., :3] == (20, 18, 24), axis=2)
    if lone.any():
        idx = ndimage.distance_transform_edt(~donor, return_distances=False, return_indices=True)
        out[lone] = out[idx[0][lone], idx[1][lone]]
    return out, int(bad.sum()), int(lone.sum()), int(rim_ink.sum())

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
