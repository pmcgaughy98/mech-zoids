"""Author readable paint/steel PBR maps on the gorilla's existing UV layout.

No remesh or export: geometry, UVs, skin weights, bones and every animation byte
are retained. Only embedded images and the body's normal strength are replaced.
The model's own old maps identify its material families and occlusion.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
import math
from pathlib import Path
import struct

import numpy as np
from PIL import Image, ImageFilter


def read_glb(path):
    raw = Path(path).read_bytes()
    assert struct.unpack_from('<III', raw)[:2] == (0x46546C67, 2)
    length, kind = struct.unpack_from('<II', raw, 12)
    assert kind == 0x4E4F534A
    doc = json.loads(raw[20:20 + length])
    offset = 20 + length
    n, kind = struct.unpack_from('<II', raw, offset)
    assert kind == 0x004E4942
    return raw, doc, raw[offset + 8:offset + 8 + n]


def accessor(doc, binary, index):
    a = doc['accessors'][index]
    v = doc['bufferViews'][a['bufferView']]
    dtype = {5121: 'u1', 5123: '<u2', 5125: '<u4', 5126: '<f4'}[a['componentType']]
    count = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}[a['type']]
    item = np.dtype(dtype).itemsize
    offset = v.get('byteOffset', 0) + a.get('byteOffset', 0)
    return np.ndarray((a['count'], count), dtype=dtype, buffer=binary,
                      offset=offset, strides=(v.get('byteStride', count * item), item)).copy()


def image_bytes(doc, binary, index):
    v = doc['bufferViews'][doc['images'][index]['bufferView']]
    return binary[v.get('byteOffset', 0):v.get('byteOffset', 0) + v['byteLength']]


def encode_image(array):
    im = Image.fromarray(np.clip(np.round(array), 0, 255).astype(np.uint8))
    stream = io.BytesIO()
    im.save(stream, format='PNG', optimize=True)
    return stream.getvalue()


def weld_components(position, joints, weights, triangles):
    parent = list(range(len(position)))

    def root(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        a, b = root(a), root(b)
        if a != b:
            parent[b] = a

    # Restore connectivity across exported UV/normal splits, but never across bones.
    buckets = {}
    for i, p in enumerate(position):
        bone = int(joints[i, np.argmax(weights[i])])
        key = (*np.round(p * 100000).astype(int), bone)
        if key in buckets:
            union(i, buckets[key])
        else:
            buckets[key] = i
    for a, b, c in triangles:
        union(int(a), int(b))
        union(int(b), int(c))
    roots = np.array([root(i) for i in range(len(position))])
    return np.unique(roots, return_inverse=True)[1]


def family(rgb):
    r, g, b = np.asarray(rgb).T
    out = np.full(r.shape, 2, dtype=np.int32)  # steel/frame
    out[(g > r * 1.12) & (g > b * 1.12)] = 0
    out[(r > g * 1.16) & (g > b * 1.2)] = 1
    out[(g > r * 1.4) & (b > r * 1.4)] = 3
    return out


def write_glb(path, doc, binary, replacements):
    updated = copy.deepcopy(doc)
    payload = bytearray()
    for i, view in enumerate(doc['bufferViews']):
        original = binary[view.get('byteOffset', 0):view.get('byteOffset', 0) + view['byteLength']]
        chunk = replacements.get(i, original)
        payload.extend(b'\0' * ((-len(payload)) % 4))
        updated['bufferViews'][i]['byteOffset'] = len(payload)
        updated['bufferViews'][i]['byteLength'] = len(chunk)
        payload.extend(chunk)
    updated['buffers'][0]['byteLength'] = len(payload)
    payload.extend(b'\0' * ((-len(payload)) % 4))
    # Keep the modeled bevels; the old fine tiled bump should not drive the silhouette's shading.
    updated['materials'][0]['normalTexture']['scale'] = 0.45
    encoded = json.dumps(updated, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    result = struct.pack('<III', 0x46546C67, 2, 28 + len(encoded) + len(payload))
    result += struct.pack('<II', len(encoded), 0x4E4F534A) + encoded
    result += struct.pack('<II', len(payload), 0x004E4942) + payload
    Path(path).write_bytes(result)
    # Verify the actual file, not the in-memory arrays: all non-image buffers survive exactly.
    _, check, data = read_glb(path)
    preserved = 0
    for i, v in enumerate(doc['bufferViews']):
        if i in replacements:
            continue
        v2 = check['bufferViews'][i]
        old = binary[v.get('byteOffset', 0):v.get('byteOffset', 0) + v['byteLength']]
        new = data[v2['byteOffset']:v2['byteOffset'] + v2['byteLength']]
        assert old == new, f'Non-image buffer {i} changed'
        preserved += 1
    for key in ('meshes', 'nodes', 'skins', 'animations', 'accessors', 'scenes'):
        assert doc.get(key) == check.get(key), key
    return updated, preserved


def finish(source, out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    raw, doc, binary = read_glb(source)
    body = next(p for m in doc['meshes'] for p in m['primitives'] if p['material'] == 0)
    attrs = body['attributes']
    pos = accessor(doc, binary, attrs['POSITION'])
    normals = accessor(doc, binary, attrs['NORMAL'])
    uv = accessor(doc, binary, attrs['TEXCOORD_0'])
    indices = accessor(doc, binary, body['indices']).reshape(-1, 3)
    groups = weld_components(pos, accessor(doc, binary, attrs['JOINTS_0']),
                             accessor(doc, binary, attrs['WEIGHTS_0']), indices)
    maps = [np.array(Image.open(io.BytesIO(image_bytes(doc, binary, i))).convert('RGB')) for i in range(3)]
    old_normal, old_color, old_orm = maps
    height, width = old_color.shape[:2]
    assert old_color.shape == old_normal.shape == old_orm.shape
    # Identify a material from the whole connected part, so a painted vent cannot
    # arbitrarily change a plate into steel. Area weighting avoids tiny bevel votes.
    votes = np.zeros((groups.max() + 1, 4), dtype=np.float64)
    tri_group = groups[indices[:, 0]]
    tri_pos = pos[indices]
    areas = np.linalg.norm(np.cross(tri_pos[:, 1] - tri_pos[:, 0], tri_pos[:, 2] - tri_pos[:, 0]), axis=1)
    weights = np.array([[1/3, 1/3, 1/3], [.6, .2, .2], [.2, .6, .2], [.2, .2, .6]])
    samples = np.einsum('sc,tcd->tsd', weights, uv[indices])
    # glTF UVs use top-left image convention (Blender's exporter already flips V).
    sx = np.clip((samples[:, :, 0] * width).astype(int), 0, width - 1)
    sy = np.clip((samples[:, :, 1] * height).astype(int), 0, height - 1)
    kinds = family(old_color[sy, sx].reshape(-1, 3)).reshape(-1, 4)
    for sample in range(4):
        np.add.at(votes, (tri_group, kinds[:, sample]), areas)
    part_family = np.argmax(votes, axis=1)
    # Steel components keep light steel and dark machinery distinct.
    value_sum = np.zeros(len(votes))
    value_weight = np.zeros(len(votes))
    value = np.max(old_color[sy, sx], axis=2).mean(axis=1)
    np.add.at(value_sum, tri_group, value * areas)
    np.add.at(value_weight, tri_group, areas)
    part_brightness = value_sum / np.maximum(value_weight, 1e-8)
    # Large, quiet color fields. Paint is non-metallic coating; grey hubs are bare steel.
    palette = np.array([[63, 94, 43], [145, 87, 30], [99, 110, 122], [39, 184, 195]], dtype=np.float32)
    dark_steel = np.array([50, 58, 68], dtype=np.float32)
    part_min = np.full((len(votes), 3), np.inf)
    part_max = np.full((len(votes), 3), -np.inf)
    np.minimum.at(part_min, groups, pos)
    np.maximum.at(part_max, groups, pos)
    color = np.zeros((height, width, 3), dtype=np.float32)
    orm = np.zeros_like(color)
    normal = np.zeros_like(color) + [128, 128, 255]
    cover = np.zeros((height, width), dtype=bool)
    # Smooth occlusion, never bake the old panel-grid albedo into the new paint.
    ao_image = Image.fromarray(old_orm[:, :, 0]).filter(ImageFilter.GaussianBlur(1.2))
    ao = np.array(ao_image).astype(np.float32) / 255
    lit_axis = np.array([-.35, .88, .3], dtype=np.float32)
    lit_axis /= np.linalg.norm(lit_axis)
    for t, ids in enumerate(indices):
        coords = uv[ids] * [width, height]
        lo = np.maximum(np.floor(coords.min(axis=0)).astype(int), 0)
        hi = np.minimum(np.ceil(coords.max(axis=0)).astype(int), [width - 1, height - 1])
        if np.any(hi < lo):
            continue
        a, b, c = coords
        denominator = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
        if abs(denominator) < 1e-8:
            continue
        yy, xx = np.mgrid[lo[1]:hi[1]+1, lo[0]:hi[0]+1]
        x, y = xx + .5, yy + .5
        w0 = ((b[1] - c[1]) * (x - c[0]) + (c[0] - b[0]) * (y - c[1])) / denominator
        w1 = ((c[1] - a[1]) * (x - c[0]) + (a[0] - c[0]) * (y - c[1])) / denominator
        w2 = 1 - w0 - w1
        inside = (w0 >= -1e-5) & (w1 >= -1e-5) & (w2 >= -1e-5)
        if not inside.any():
            continue
        iy, ix = yy[inside], xx[inside]
        bary = np.stack([w0[inside], w1[inside], w2[inside]], axis=1)
        n = bary @ normals[ids]
        n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-6)
        group = tri_group[t]
        kind = int(part_family[group])
        dark = kind == 2 and part_brightness[group] < 49
        base = dark_steel.copy() if dark else palette[kind].copy()
        # Small part-level color variation, never per-pixel noise or repeated grids.
        variation = 1 + (((int(group) * 73) % 11) - 5) * .005
        contact = .73 + .27 * np.sqrt(ao[iy, ix])
        # A broad directional paint ramp holds the upper plane and bottom separation
        # when rendered small, without any painted fake cast shadows.
        facing = np.clip(n @ lit_axis, -.6, .9)
        plane = np.where(facing > .35, 1.04, np.where(facing < -.2, .90, 1.0))
        plane = 1 + (plane - 1) * (.7 if kind == 2 else 1)
        rgb = base[None, :] * (variation * contact * plane)[:, None]
        # A few engineered panel insets on broad planar armor faces. Coordinates
        # come from the real part, never a repeating texture tile or random scratch.
        span = part_max[group] - part_min[group]
        surface_axis = int(np.argmax(np.abs(n.mean(axis=0))))
        axes = [axis for axis in range(3) if axis != surface_axis]
        if kind in (0, 1) and int(group) % 4 == 0 and min(span[axes]) > .20:
            planar = np.abs(n[:, surface_axis]) > .94
            local = bary @ pos[ids] - part_min[group]
            u, v = local[:, axes[0]], local[:, axes[1]]
            w, h = span[axes]
            within_u = (u > .14*w) & (u < .86*w)
            within_v = (v > .14*h) & (v < .86*h)
            du = np.minimum(np.abs(u - .14*w), np.abs(u - .86*w))
            dv = np.minimum(np.abs(v - .14*h), np.abs(v - .86*h))
            seam = planar & ((within_v & (du < .006)) | (within_u & (dv < .006)))
            bevel = planar & ~seam & ((within_v & (du < .014)) | (within_u & (dv < .014)))
            rgb[seam] *= .54
            rgb[bevel] *= 1.13
        color[iy, ix] = rgb
        # Keep broad modeled bevels prominent; remove the strong repeated bump lattice.
        if kind == 2:
            strength = .28 if dark else .22
        else:
            strength = .10
        old_n = old_normal[iy, ix].astype(np.float32) / 127.5 - 1
        old_n[:, :2] *= strength
        old_n[:, 2] = np.maximum(old_n[:, 2], .85)
        old_n /= np.maximum(np.linalg.norm(old_n, axis=1, keepdims=True), 1e-6)
        normal[iy, ix] = (old_n + 1) * 127.5
        roughness = .66 if kind == 0 else .63 if kind == 1 else .72 if dark else .47
        # Bright joint housings carry a grey protective coat; tiny exposed edge
        # strips are bare steel. This stays readable without brightening black frame.
        metallic = .12 if dark else .42 if kind == 2 else 0.0
        orm[iy, ix, 0] = 255 * (.55 + .45 * np.sqrt(ao[iy, ix]))
        orm[iy, ix, 1] = 255 * roughness
        orm[iy, ix, 2] = 255 * metallic
        cover[iy, ix] = True
    # Six texels of gutter dilation protects every island under filtering/mipmaps.
    filled = cover.copy()
    for _ in range(6):
        count = np.zeros((height, width), dtype=np.float32)
        accum = [np.zeros_like(color), np.zeros_like(orm), np.zeros_like(normal)]
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ys = slice(max(0, dy), min(height, height + dy))
            xs = slice(max(0, dx), min(width, width + dx))
            sy = slice(max(0, -dy), min(height, height - dy))
            sx = slice(max(0, -dx), min(width, width - dx))
            mask = filled[sy, sx]
            count[ys, xs] += mask
            for total, source_map in zip(accum, (color, orm, normal)):
                total[ys, xs] += source_map[sy, sx] * mask[:, :, None]
        update = ~filled & (count > 0)
        for target, total in zip((color, orm, normal), accum):
            target[update] = total[update] / count[update, None]
        filled |= update
    orm[~filled] = [255, 170, 0]
    normal[~filled] = [128, 128, 255]
    replacements = {}
    for i, (name, data) in enumerate((('ape_l_atlas_normal.png', normal), ('ape_l_atlas.png', color), ('ape_l_atlas_orm.png', orm))):
        payload = encode_image(data)
        (out / name).write_bytes(payload)
        replacements[doc['images'][i]['bufferView']] = payload
    _, preserved = write_glb(out / 'ape_l.glb', doc, binary, replacements)
    report = {
        'source_sha256': hashlib.sha256(raw).hexdigest(),
        'finished_sha256': hashlib.sha256((out / 'ape_l.glb').read_bytes()).hexdigest(),
        'resolution': [width, height], 'coverage': float(cover.mean()),
        'connected_parts': int(len(votes)), 'triangles_body': int(len(indices)),
        'preserved_non_image_buffer_views': preserved,
        'geometry_uv_skin_bones_animations_unchanged': True,
        'clips': [a['name'] for a in doc.get('animations', [])],
        'material_parts': {name: int((part_family == i).sum()) for i, name in enumerate(('green', 'orange', 'steel', 'cyan'))},
        'paint_metallic': 0, 'paint_roughness': [.63, .66], 'coated_steel_metallic': .42,
        'steel_part_brightness_percentiles': np.percentile(part_brightness[part_family == 2], [0, 25, 50, 75, 100]).tolist(),
        'normal_strength': .45,
    }
    (out / 'audit.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    finish(args.source, args.out)
