from finish import *

def board(name):
 out=ROOT/name;N=COUNTS[name];checks=[]
 review=Image.new('RGB',((N+1)*288,3*310+35),'#59616a');d=ImageDraw.Draw(review);d.text((8,8),f'FENNEC TAKE B / {name} / approved still then frames / cyan ground 160',fill='white')
 for r,n in enumerate(NAMES):
  frames=[];ref=np.array(approved(n));rm=ref[:,:,3]>0
  for c in range(-1,N):
   im=approved(n) if c<0 else Image.open(out/'frames'/f'{n}_f{c}.png').convert('RGBA')
   bg=Image.new('RGB',(192,192),'#737980');bg.paste(im,mask=im.getchannel('A'))
   # Native drawing crop preserves square pixels; no nonuniform display scaling.
   tile=bg.crop((32,75,160,171)).resize((288,216),Image.Resampling.NEAREST)
   px=(c+1)*288;py=60+r*310;review.paste(tile,(px,py));d.text((px+8,py-18),f'{n} '+('STILL' if c<0 else f'f{c} / {TIMINGS[name][c]} ms'),fill='white');d.line((px,py+192,px+287,py+192),fill='#63dada')
   if c<0:continue
   frames.append(bg.resize((576,576),Image.Resampling.NEAREST))
   a=np.array(im);m=a[:,:,3]>0;yy,xx=np.where(m);col=np.unique(a[m,:3],axis=0);u=m|rm
   iou=float((m&rm).sum()/u.sum());ciou=float((np.all(a==ref,2)&u).sum()/u.sum())
   lab,k=ndi.label(m,structure=np.ones((3,3)));sizes=np.bincount(lab.ravel())[1:]
   req=name!='walk' and (c==0 or c==N-1)
   checks.append(dict(frame=f'{n}_f{c}',duration_ms=TIMINGS[name][c],bottom_row=int(yy.max()),colour_count=len(col),pixels_below_160=int(m[161:].sum()),silhouette_IoU=iou if req else None,colour_IoU=ciou if req else None,required_exact_still=req,palette_ok=all(any(np.array_equal(v,p) for p in PAL) for v in col),binary_alpha=bool(np.isin(a[:,:,3],[0,255]).all()),canvas_edge=bool(m[0].any() or m[-1].any() or m[:,0].any() or m[:,-1].any()),stray_components=int((sizes<3).sum()),enclosed_hole_pixels=int((ndi.binary_fill_holes(m)&~m).sum())))
  frames[0].save(out/f'preview_{n}.gif',save_all=True,append_images=frames[1:],duration=TIMINGS[name],loop=0,disposal=2,optimize=False)
 review.save(out/'review.png');review.resize((min(1800,review.width),round(review.height*min(1800,review.width)/review.width)),Image.Resampling.NEAREST).save(out/'review_small.png')
 (out/'checks.txt').write_text('IoU against approved still at (+16,+20); exact-colour IoU counts identical RGBA on silhouette union.\n'+'\n'.join(json.dumps(c) for c in checks)+'\n')
 return checks

if __name__=='__main__':
 import sys
 allchecks={}
 for name in sys.argv[1:] or COUNTS:
  checks=board(name);allchecks[name]=checks
  print(name,len(checks),'frames; faults',[(c['frame'],c['bottom_row'],c['enclosed_hole_pixels'],c['stray_components']) for c in checks if c['bottom_row']!=160 or c['enclosed_hole_pixels'] or c['stray_components']])
 (ROOT/'verification.json').write_text(json.dumps(allchecks,indent=2))
