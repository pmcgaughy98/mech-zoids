from pathlib import Path
P=Path(__file__).resolve().parent;p=P/'finish.py';s=p.read_text();key="Image.fromarray(out).save(P/'sheet_finished.png')"
s=s.replace(key,"""# Restore only existing narrow dark seam pixels, ranked by contrast, up to the
# approved accent share. Broad ramp shadows and the silhouette remain untouched.
accent_restored={}
L=out[:,:,:3]@[.2126,.7152,.0722]
dark=vis&(L<75)
narrow=dark&~ndi.binary_opening(dark,structure=np.ones((3,3)))
contrast=ndi.maximum_filter(L,size=5)-L
candidate=narrow&(contrast>48)&ndi.binary_erosion(vis)&~lens
for d,(rr,cc) in slots.items():
 y0,y1=rr*out.shape[0]//3,(rr+1)*out.shape[0]//3; x0,x1=cc*out.shape[1]//3,(cc+1)*out.shape[1]//3
 m=vis[y0:y1,x0:x1]; part=out[y0:y1,x0:x1]
 ink=np.all(part[:,:,:3]==(20,18,24),axis=2)&m
 target={'s':.073,'se':.060,'sw':.060,'e':.082,'w':.082,'ne':.060,'nw':.060,'n':.071}[d]
 need=max(0,round(m.sum()*target)-int(ink.sum()))
 cy,cx=np.where(candidate[y0:y1,x0:x1]&~ink)
 order=np.argsort(-contrast[y0+cy,x0+cx],kind='stable')[:need]
 out[y0+cy[order],x0+cx[order],:3]=(20,18,24)
 accent_restored[d]=int(len(order))
Image.fromarray(out).save(P/'sheet_finished.png')""")
s=s.replace("'seam_pixels':int(seam.sum())","'seam_pixels':int(seam.sum()),'accent_restored':accent_restored")
p.write_text(s)
