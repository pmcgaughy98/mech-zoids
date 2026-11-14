"""Adapt the copied set A finishers; every write is local to set B."""
from pathlib import Path
R=Path(__file__).resolve().parent
p=R/'finish.py';s=p.read_text()
s=s.replace("COUNTS={'idle':5,'walk':8,'chest_beat':8,'hex_shield':6}","COUNTS={'bound':9,'hex_dome':8,'death':8}\nTIMINGS={'bound':[300,120,80,90,200,90,80,150,250],'hex_dome':[300,150,150,300,60,350,150,300],'death':[80,120,120,140,160,180,250,1000]}\nLIFTS={3:16,4:28,5:12}")
s=s.replace("y=161-fin.height","y=161-fin.height-(LIFTS.get(c,0) if name=='bound' else 0)-(1 if name=='death' and c==6 else 0)")
s=s.replace("['chest_beat','hex_shield']","['bound','hex_dome']")
start=s.index("  durations={'idle':")
end=s.index('\n',start)
s=s[:start]+"  durations=TIMINGS[name]"+s[end:]
s=s.replace("frame0_IoU=iou if c==0 else None", "lift=160-int(yy.max()),enclosed_hole_pixels=int((ndi.binary_fill_holes(m)&~m).sum()),last_frame_IoU=iou if c==N-1 else None,last_frame_exact_colour_IoU=exact if c==N-1 else None,frame0_IoU=iou if c==0 else None")
p.write_text(s)
p=R/'polish.py';s=p.read_text();start=s.index('# Finish the small cyclic');end=s.index('# Restore native face')
s=s[:start]+s[end:];s=s.replace("['chest_beat','hex_shield']","['bound','hex_dome','death']").replace("range(1,COUNTS[name]-1)","range(1,COUNTS[name]-(0 if name=='death' else 1))")
p.write_text(s)
p=R/'gems.py';s=p.read_text().replace("['chest_beat','hex_shield']","['bound','hex_dome','death']").replace("range(1,COUNTS[name]-1)","range(1,COUNTS[name]-(0 if name=='death' else 1))")
start=s.index('for n in NAMES:\n # Penultimate');end=s.index('for name in COUNTS:board(name)',start);s=s[:start]+s[end:];p.write_text(s)
p=R/'seam_fill.py';s=p.read_text().replace('["idle", "walk", "chest_beat", "hex_shield"]','["bound", "hex_dome", "death"]')
s=s.replace('import shutil','import shutil,json\nfrom scipy import ndimage as ndi\nlog={}')
s=s.replace('        a[fill] = INK',"        enclosed=ndi.binary_fill_holes(op)&~op\n        _,count=ndi.label(enclosed)\n        fill |= enclosed\n        # Exact approved endpoints take precedence over seam repair.\n        endpoint=f.stem.endswith('_f0') or (anim=='bound' and f.stem.endswith('_f8')) or (anim=='hex_dome' and f.stem.endswith('_f7'))\n        if endpoint: fill[:]=False\n        log[f'{anim}/{f.stem}']={'enclosed_holes_found':count,'enclosed_hole_pixels_found':int(enclosed.sum()),'hole_pixels_filled':int((fill&enclosed).sum()),'seam_pixels_filled':int((fill&~enclosed).sum())}\n        a[fill] = INK")
s+="\n(HERE/'seam_log.json').write_text(json.dumps(log,indent=2))\n";p.write_text(s)
print('Copied set A finishers adapted')
