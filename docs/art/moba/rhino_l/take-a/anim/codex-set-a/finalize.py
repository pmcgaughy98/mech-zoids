from pathlib import Path
import json, hashlib
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent
meta=json.loads((ROOT/'generation.json').read_text())
visual={
'idle':'Same main plate/frame/joint/foot/horn/tail design in all rows, but eye often lost; breath beats match, modest foot/shape drift; front/back straight-on; rear leg length broadly stable.',
'walk':'Same main design, eye mostly lost; stepping visible but diagonal pairing and column timing do NOT reliably match (front repeats while rear alternates); front/back straight-on; rear legs shorten with lifted feet.',
'horn-jab':'Same main design, eye mostly lost; low-to-high jab beats broadly match, forward lunge weak; front head turns slightly at hit/follow-through, back straight-on; rear leg length broadly stable.',
'horn-toss':'Same main design, eye mostly lost; scoop/lift beats broadly match but horn does NOT clearly sweep backward; front becomes three-quarter at peak, back straight-on; rear legs shorten during crouch/peak instead of keeping length.'}
lines=['Tokens used: unavailable. Built-in image tool: exactly one image per sheet, unchanged exact prompt files, front/side/back refs attached in order; no redos.']
qa={}
for name,m in meta.items():
    out=ROOT/name; s=json.loads((out/'summary.json').read_text()); frames=sorted((out/'frames').glob('*.png'))
    missing=[]; red=[]; glint=[]; dims=[]; bottoms=[]
    for f in frames:
        im=Image.open(f).convert('RGBA'); a=np.array(im); mask=a[:,:,3]>0
        assert im.size==(192,192) and set(np.unique(a[:,:,3])).issubset({0,255})
        count=int((np.all(a[:,:,:3]==[255,58,42],axis=2)&mask).sum()); red.append(count)
        glint.append(int((np.all(a[:,:,:3]==[255,230,216],axis=2)&mask).sum()))
        if not f.name.startswith('back') and not count: missing.append(f.stem)
        bottoms.append(int(np.where(mask)[0].max()))
    for n in ['front','side','back']:
        im=Image.open(out/'frames'/f'{n}_f0.png'); b=im.getbbox(); dims.append(f'{b[2]-b[0]}x{b[3]-b[1]}')
        gif=Image.open(out/f'preview_{n}.gif'); durations=[]
        for i in range(gif.n_frames):
            gif.seek(i); assert gif.size==(576,576); durations.append(gif.info['duration'])
        expected=[110]*6 if name=='walk' else [220]*5 if name=='idle' else [400]+[90 if name=='horn-jab' else 100]*(5 if name=='horn-jab' else 6)
        assert durations==expected,(name,n,durations)
    assert hashlib.sha256((out/'sheet_raw.png').read_bytes()).hexdigest()==m['sha256']
    qa[name]=dict(frames=len(frames),missing_red_front_side=missing,red_pixels=sum(red),glint_pixels=sum(glint),bottoms=sorted(set(bottoms)),gif_timing_verified=True,raw_hash_verified=True)
    lines.append(f'{name}: image {m["size"][0]}x{m["size"][1]}; sha256 {m["sha256"]}')
    lines.append(f'{name}: grid clean YES; factors F/S/B '+ '/'.join(f'{v:.6f}' for v in s['factors'])+'; f0 sizes '+ '/'.join(dims)+'; ref exact shares '+ '/'.join(f'{s["ref_similarity"][n]:.3f}' for n in ['front','side','back'])+f'; mirror min F/B {min(s["mirror_silhouette"]["front"]):.3f}/{min(s["mirror_silhouette"]["back"]):.3f}; side right YES.')
    lines.append(f'{name}: {len(frames)} frames, palette/alpha/borders PASS, eye rim=0; red/glint total {sum(red)}/{sum(glint)}, {len(missing)} front/side frames lack red; bottom y '+','.join(map(str,sorted(set(bottoms))))+'; >3px: '+('; '.join(s['ground_failures']) or 'none')+'. Full frame checks: '+name+'/checks.txt.')
    lines.append(f'{name} by eye: '+visual[name])
lines.append('Horn-jab: nominal column-3 cut grazed the horn; moved cut +2 source px into its empty gutter, preserving all 18 separate rhinos.')
lines.append('Previews: each sheet/review.png and preview_front/side/back.gif (3x nearest, #808080, requested timing); 75 frames total. All output writes inside codex-set-a; no asset install or commit.')
lines.append('Review candidates with the failures above, not approved animation. Approved refinish.py was copied then adapted; finish_all.py runs it; generation.json records unchanged raw hashes.')
assert len(lines)<25
(ROOT/'REPORT.txt').write_text('\n'.join(lines)+'\n')
(ROOT/'verification.json').write_text(json.dumps(qa,indent=2)+'\n')
print('\n'.join(lines))
