from pathlib import Path
import ast,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage as ndi
C=Path(__file__).resolve().parent; R=C.parent
ns={'__file__':str(R/'build.py'),'__name__':'source_only'}
exec(compile((R/'build.py').read_text(),str(R/'build.py'),'exec'),ns)
D,K,P,mask,lmask,shift,comp,fp=[ns[k] for k in ['D','K','P','mask','limb_mask','shift','comp','fp']]
rig=json.loads((R/'rig.json').read_text());T=json.loads((R/'targets.json').read_text())
Y,X=np.indices((192,192)); B=R.parents[1]
tree=ast.parse((R.parent/'selout_rhino.py').read_text()); se={'np':np,'OUTLINE':np.array(P[0][:3],np.uint8)}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='selout'],type_ignores=[]),'selout','exec'),se);selout=se['selout']
(C/'walk/frames').mkdir(parents=True,exist_ok=True);(C/'walk/layers').mkdir(exist_ok=True)
allframes={}; sources={}
def poly(a,points,c): ImageDraw.Draw(a).polygon([tuple(map(int,p)) for p in points],fill=P[c])
def socket(root,knee,width=5):
    # Native staircase, horizontal rows; no transform or resampling.
    a=np.zeros((192,192,4),np.uint8)
    x0,y0=map(int,root);x1,y1=map(int,knee)
    if y1<y0:y1=y0
    for y in range(y0,y1+1):
        x=int(np.floor(x0+(x1-x0)*(y-y0)/max(1,y1-y0)+.5))
        a[y,x-width:x+width+1]=P[1]
        a[y,x-width+1:x+width]=P[2]
        a[y,x-width+1:x-width+3]=P[3]
    return a
for view,legs in D.items():
    ref=np.array(Image.open(B/'views_cam35'/f'{view}.png').convert('RGBA'));body=np.array(Image.open(R/'walk/layers'/f'{view}_body.png'))
    sources[view]={}; hidden={'LH':('RH',(0,-16)),'LF':('RF',(0,-16))} if view=='e' else {'LF':('RF',(-24,-17 if view=='se' else -10))}
    for name,q in legs.items():
        a=ref.copy();a[~lmask(view,name,q)]=0
        if (view,name)==('se','RF'): a[(Y<149)|(X<111)]=0
        if (view,name)==('ne','RF'): a[Y<127]=0
        sources[view][name]=(a,q)
    for name,(donor,delta) in hidden.items():
        a,q=sources[view][donor];qq=[(np.array(p)+delta).tolist() for p in q[:3]]+q[3:];qq[4]=q[4]+delta[1];sources[view][name]=(shift(a,*delta),qq)
    frames=[]
    for f in range(8):
        dip=int(f in (0,4));layers={}
        for name,(src,q) in sources[view].items():
            rr=next(r for r in rig[view] if r['frame']==f and r['name']==name)
            delta=np.array(rr['ankle'])-q[2];dx,dy=delta.astype(int)
            # The complete original cuff, knee disc and foot block translate as one.
            a=socket(np.array(q[0])+[0,dip],np.array(q[2] if view=='se' and name in ('RF','LF') else q[1])+[dx,dy],4 if view=='se' and name in ('RF','LF') else 5)
            comp(a,shift(src,dx,dy));sole,_=fp(src);a[int(sole[1])+dy+1:]=0
            a[Y<int(q[0][1])+dip]=0
            if view=='ne' and name in ('RF','LF'):
                # Neck plate is pinned below; socket belongs behind this native foot.
                a[Y<int(q[0][1])+14+dip]=0
            # Preserve original sole silhouette, never let sockets create a second toe.
            ft=shift(src,dx,dy);a[(Y>=int(sole[1])+dy-2)&(ft[:,:,3]==0)]=0
            layers[name]=a;Image.fromarray(a).save(C/'walk/layers'/f'{view}_{name}_f{f}.png')
        a=np.zeros_like(ref)
        for name in ['LF','LH','RF','RH']:comp(a,layers[name])
        pinned=shift(body,0,dip);comp(a,pinned)
        if view=='ne':
            # The original trace accidentally included shoulder paint as RF upper.
            # Keep that entire plate exactly as run1, including its exposed contour.
            plate=ref.copy();plate[~lmask('ne','RF',D['ne']['RF'])]=0;plate[Y>=127]=0
            comp(a,shift(plate,0,dip))
        # Explicitly close socket wedges using the adjacent metal shadow colour.
        holes=ndi.binary_fill_holes(a[:,:,3]>0)&(a[:,:,3]==0);a[holes]=P[1]
        labs,n=ndi.label(a[:,:,3]>0,np.ones((3,3)));sz=np.bincount(labs.ravel());sz[0]=0
        for l in range(1,n+1):
            if sz[l]<=3:a[labs==l]=0
        # Remove single interior ink pixels with a hand-palette replacement.
        pin=pinned[:,:,3]>0
        for iteration in range(4):
            dark=np.isin(a[:,:,:3].astype('uint32')@np.array([65536,256,1]),[0x141218,0x211e27,0x3d3a44])&(a[:,:,3]>0)
            material=(a[:,:,3]>0)&~dark&~np.all(a[:,:,:3]==[255,58,42],axis=2)
            p=np.pad(material,1);spots=dark&p[:-2,1:-1]&p[2:,1:-1]&p[1:-1,:-2]&p[1:-1,2:]&~pin
            if not spots.any():break
            for y,x in zip(*np.where(spots)):
                neighbours=[tuple(a[y-1,x]),tuple(a[y+1,x]),tuple(a[y,x-1]),tuple(a[y,x+1])]
                # Majority material; ties use the left pixel to continue horizontal bands.
                chosen=max(neighbours,key=lambda c:(neighbours.count(c),c==tuple(a[y,x-1])))
                a[y,x]=chosen
        frames.append(a);Image.fromarray(a).save(C/'walk/frames'/f'{view}_f{f}.png')
    allframes[view]=frames
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18);bg=(86,126,107,255)
# 4 frames per row, every crop exactly 4x native. Per view still, run1, cleaned.
crop=(44,108,144,165);tw,th=400,228;cw,ch=408,256
board=Image.new('RGBA',(cw*4,ch*5*3),bg);dr=ImageDraw.Draw(board)
for vi,view in enumerate(D):
    ref=np.array(Image.open(B/'views_cam35'/f'{view}.png').convert('RGBA'))
    for group,arrs in enumerate([[ref],[np.array(Image.open(R/'walk/frames'/f'{view}_f{f}.png')) for f in range(8)],allframes[view]]):
        for j,a in enumerate(arrs):
            row=vi*5+(0 if group==0 else 1+(group-1)*2+j//4);col=0 if group==0 else j%4
            ox,oy=col*cw,row*ch;dr.text((ox+6,oy+3),f'{view} '+('STILL' if group==0 else ('RUN1' if group==1 else 'CLEAN')+f' f{j}'),fill='white',font=font)
            tile=Image.fromarray(selout(a)[0]).crop(crop).resize((tw,th),Image.Resampling.NEAREST);board.alpha_composite(tile,(ox,oy+26))
    pics=[]
    for a in allframes[view]:
        tile=Image.fromarray(selout(a)[0]).resize((768,768),Image.Resampling.NEAREST);im=Image.new('RGBA',tile.size,bg);im.alpha_composite(tile);pics.append(im.convert('RGB'))
    pics[0].save(C/f'{view}_preview.gif',save_all=True,append_images=pics[1:],duration=[120,130]*4,loop=0,disposal=2,optimize=False)
    raw=[Image.fromarray(a) for a in allframes[view]];raw[0].save(C/f'{view}_preview.apng',save_all=True,append_images=raw[1:],duration=125,loop=0,disposal=0,blend=0)
    board.crop((0,vi*5*ch,cw*4,(vi+1)*5*ch)).convert('RGB').save(C/f'{view}_board.png')
board.convert('RGB').save(C/'board.png')
print('24 frames and boards saved')
