"""Hippo cleanup, adapted from kangaroo take A: whole-sheet nearest-solid-colour cleanup.
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
    # Approved purple is armour, including its rim. Only off-palette magenta on the rim is contamination.
    edge = solid & ~ndimage.binary_erosion(solid)
    purple = np.zeros(solid.shape, bool)
    for c in ['a990e0','7258b4','4a347e','26183f','a8183c','ff5c78','ffe0e6']:
        purple |= np.all(px[..., :3] == tuple(bytes.fromhex(c)), axis=2)
    bad = edge & ~purple & (r > b*.90) & (b > g*1.8) & (r > g*1.8)
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
