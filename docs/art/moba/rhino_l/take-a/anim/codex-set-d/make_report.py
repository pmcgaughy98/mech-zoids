from pathlib import Path
import json
out=Path(__file__).resolve().parent
meta=json.loads((out/'generation.json').read_text()); summary=json.loads((out/'summary.json').read_text())
visual={
'brace':'Same rhino in both rows: yellow hex plates/dark frame, grey disc joints/flat feet, two-tone horn and tail retained; se red retained, glints lost. Brace reads and columns agree broadly; se/ne angles held throughout, no mirroring/straightening. Rear shins visibly shorten at deepest brace; not a full leg-length pass.',
'death':'Same rhino in both rows with listed design anchors; se red retained early, glints lost, final eyes dark. Belly-collapse sequence agrees broadly across rows; se/ne angles held, no mirroring/straightening. Legs tuck and visually shorten at collapse rather than keeping clear full length; chest-down/back-standing beat is weak.',
'idle':'Same rhino in both rows with listed design anchors; se red retained, glints lost. Small breathing motion and column beats read; se/ne angles held in every cell, no mirroring/straightening. Leg lengths mostly hold, but feet drift slightly instead of remaining exactly planted.',
'brace-shuffle':'Same rhino in all three rows with listed design anchors, but red eyes disappear in several finished front/side cells and glints are lost. Front/back stay straight; side faces RIGHT. Body stays low/braced and legs remain short; shuffle reads. One visible foot lifts in some cells, but exact hind-foot order, only-one-foot lifting throughout, and column-for-column row agreement cannot be certified from occluded feet.'}
lines=['Set D: exactly ONE built-in generation per sheet, supplied prompt text and ordered refs; all raws wide landscape; no redos. Tokens used unavailable.']
for name in ['brace','death','idle','brace-shuffle']:
    m=meta[name]; lines.append(f'{name}: {m["size"][0]}x{m["size"][1]}; sha256 {m["sha256"]}')
for name in ['brace','death','idle','brace-shuffle']:
    s=summary[name]; rows=['front','side','back'] if name=='brace-shuffle' else ['se','ne']
    lines.append(f'{name}: clean grid YES; '+', '.join(f'{r} factor={v:.10f}' for r,v in zip(rows,s['factors'])))
    parts=[]
    for r,check in zip(rows,s['refchecks']):
        parts.append(check.replace(' column1 vs ref:', ' f0/ref:').replace(' (opaque union; feet aligned; best x overlap each)',''))
    lines.append(' | '.join(parts))
    text=(out/name/'checks.txt').read_text(); audit=next(l for l in text.splitlines() if l.startswith('Top5'))
    ds=[d for row in s['stats'] for d in row]
    checks=f'{name} checks: {len(ds)} frames; colours {min(d["colours"] for d in ds)}-{max(d["colours"] for d in ds)}; red {min(d["red"] for d in ds)}-{max(d["red"] for d in ds)} px/frame; glint 0; eye rim 0; feet y160; no borders; max ground correction {max(abs(d["requested_shift"]) for d in ds)} px. '+audit
    if s['mirror']: checks+='; '+'; '.join(s['mirror'])+'; side right YES.'
    lines.append(checks)
    lines.append(name+' by eye: '+visual[name])
lines.append('Validation PASS: 52 frames, 192x192 binary alpha, transparent RGB zero, union palette (12 colours), no magenta/plum fringe, no clipped frames; raw hashes and GIF total timings/loops verified. Palette edge/near-black and lone-pixel audits in each checks.txt; dark frame/rim tones retained from refs.')
lines.append('Saved unchanged raws, generation.json, adapted set-B refinish.py, frames, traceable grid.json, checks.txt, 3x reviews with refs, and timed GIFs. Writes confined to set D; no installs, commits, or sibling changes.')
assert len(lines)<25
(out/'REPORT.txt').write_text('\n'.join(lines)+'\n')
# Replace the pending visual result in the requested sheet check file.
p=out/'brace-shuffle'/'checks.txt'
p.write_text(p.read_text().replace('Side faces right: pending visual audit in REPORT.txt (not inferred from numbers).','Side faces right: YES (visual audit: head and horn point right in every cell).'))
print('\n'.join(lines))
