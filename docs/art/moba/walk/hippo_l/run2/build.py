"""hippo-walk35-run2: run1 native parts, fennec run2 depth ordering.
All writes are relative to this run2 directory. Run with python -B.
"""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json, importlib.util
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R.parent/'run1'))
spec=importlib.util.spec_from_file_location('run1_build',R.parent/'run1/build.py')
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
b=old.b;P=old.P;X=old.X;Y=old.Y;load=old.load
T=json.loads((R/'targets.json').read_text())
save=lambda a,p:Image.fromarray(a).save(R/p)
def rect(x0,y0,x1,y1):return (X>=x0)&(X<=x1)&(Y>=y0)&(Y<=y1)

def sources(v):
    ref=load(R/f'stills/{v}.png');parts={};used=np.zeros((192,192),bool)
    if v=='s':
        # Native jaw contour, traced at 8x. This foreground piece is NEVER
        # assigned to either foot or knee, including its charcoal underside.
        jaw=np.zeros_like(used)
        left={134:71,135:71,136:71,137:70,138:70,139:70,140:70,141:70,142:70,143:70,144:70,145:70,146:71,147:71,148:71,149:71,150:71,151:72,152:73,153:74,154:75,155:76,156:77}
        for y,l in left.items():jaw[y,l:192-l]=True
        for n,x0,x1 in [('RF',50,85),('LF',106,141)]:
            knee=rect(x0,138,x1,149)&~jaw
            lower=rect(x0,150,x1,160)&~jaw
            # No background and no jaw paint enters the moving sources.
            parts[n]={'knee':b.piece(ref,knee),'lower':b.piece(ref,lower)}
            used|=knee|lower
        # The main shoulder housings (above row138) remain pinned. Front
        # upper links emerge beneath them, beside the tusks and jaw.
        defs={'RF':dict(root=(65,134),k=(65,145),join=(66,151),w=5),
              'LF':dict(root=(126,134),k=(126,145),join=(125,151),w=5)}
        cutoff=111
    else:
        # Rear discs end at row140. The steel joint, dark casing and whole
        # toe/heel assembly beneath them move; no leg-shaped body patches.
        for n,x0,x1 in [('LH',58,86),('RH',105,133)]:
            knee=rect(x0,141,x1,150)
            lower=rect(x0,151,x1,160)
            parts[n]={'knee':b.piece(ref,knee),'lower':b.piece(ref,lower)}
            used|=knee|lower
        defs={'LH':dict(root=(71,139),k=(71,146),join=(72,152),w=6),
              'RH':dict(root=(120,139),k=(120,146),join=(119,152),w=6)}
        cutoff=128
    pinned=b.piece(ref,~used)
    # Separate the trunk from its fixed foreground assemblies. In s the
    # head and jaw conceal the trunk; in n the rump/tail lies over the legs.
    body=b.piece(pinned,Y<=cutoff)
    foreground=b.piece(pinned,Y>cutoff)
    # Hidden native feet are translated dark-ramp counterparts. Their entire
    # layers are kept for measurement; depth compositing reveals only pixels
    # which actually clear the original head/body/near legs.
    pairs=[('RH','RF'),('LH','LF')] if v=='s' else [('LF','LH'),('RF','RH')]
    for n,src in pairs:
        dy=-25 if v=='s' else -28
        parts[n]={p:old.dark(b.shift(a,0,dy)) for p,a in parts[src].items()}
        defs[n]={k:(tuple(np.array(z)+[0,dy]) if k in ['root','k','join'] else z) for k,z in defs[src].items()}
    for n,pp in parts.items():
        defs[n]['sole']=b.support(pp['lower']).tolist()
        for p,a in pp.items():save(a,f'source/{v}_{n}_{p}.png')
    save(body,f'source/{v}_body.png');save(foreground,f'source/{v}_foreground.png')
    # Discs/head/rump stay complete in the foreground; this also documents
    # the exact fixed pixels separately from the trunk belly audit.
    save(pinned,f'source/{v}_pinned.png')
    return ref,parts,body,foreground,defs

def make(v):
    for d in ['source','walk/frames','walk/layers']:(R/d).mkdir(parents=True,exist_ok=True)
    ref,parts,body,foreground,D=sources(v);frames=[];rig=[]
    for f in range(8):
        dip=int(f in [0,4]);ll={}
        for n,pp in parts.items():
            q=D[n];sole=np.array(q['sole']);off,lift=T['paths'][n][f];vt=T['views'][v]
            target=np.array(vt['visible_feet'][n]['frames'][f]['sole_centre']) if n in vt['visible_feet'] else sole+off*np.array(vt['u'])*vt['f']-[0,lift]
            delta=np.floor(target+[0,lift]-sole+.5).astype(int)-[0,lift]
            # Depth only: the native pad centre can differ half a pixel from
            # a label; never shift a leg sideways to compensate for that.
            delta[0]=0
            dx,dy=map(int,delta);kd=np.array([0,int(np.floor((dy+dip)*.5+.5))])
            socket=np.array(q['root'])+[0,dip]
            # The attachment slides inside the pinned housing in this depth
            # projection. Keep the two-link projected length native while the
            # exposed knee moves half the foot travel. The socket-to-root
            # connector is concealed by the housing, apart from its seam.
            root=np.array(q['root'])+delta;kn=np.array(q['k'])+kd;jn=np.array(q['join'])+delta
            native_length=np.linalg.norm(np.array(q['k'])-q['root'])+np.linalg.norm(np.array(q['join'])-q['k'])
            length_error=float(abs(np.linalg.norm(kn-root)+np.linalg.norm(jn-kn)-native_length))
            far=n.endswith('H') if v=='s' else n.endswith('F')
            a=np.zeros_like(ref)
            old.casing(a,socket,root,q['w']+3,far);old.casing(a,root,kn,q['w']+3,far);old.casing(a,kn,jn,q['w']+3,far)
            old.band(a,socket,root,q['w'],far);old.band(a,root,kn,q['w'],far);old.band(a,kn,jn,q['w'],far)
            # Continue the native casing's full bevel/seam profile across a
            # one- or two-row downward extension. A narrow centre band alone
            # would leave a horizontal cut in the wide inner casing of n.
            ky,kx=np.where(pp['knee'][:,:,3]>0);ly,lx=np.where(pp['lower'][:,:,3]>0)
            boundary=int(ky.max());top=int(ly.min())
            cols=np.where(pp['knee'][boundary,:,3]>0)[0]
            for row in range(boundary+int(kd[1])+1,top+dy):
                a[row,cols]=pp['knee'][boundary,cols]
            b.comp(a,b.shift(pp['knee'],*kd));raw=b.shift(pp['lower'],dx,dy);b.comp(a,raw)
            bottom=int(sole[1]+dy);a[Y>bottom]=0;a[(Y>=bottom-1)&(raw[:,:,3]==0)]=0
            ll[n]=a;save(a,f'walk/layers/{v}_{n}_f{f}.png')
            rig.append(dict(foot=n,frame=f,delta=delta.tolist(),knee_delta=kd.tolist(),source_sole=sole.tolist(),target=target.tolist(),lift=lift,root=root.tolist(),socket=socket.tolist(),knee=kn.tolist(),ankle=jn.tolist(),native_projected_length=float(native_length),leg_length_error=length_error,hidden_in_still=n not in vt['visible_feet']))
        a=np.zeros_like(ref);far=['RH','LH'] if v=='s' else ['LF','RF'];near=['RF','LF'] if v=='s' else ['LH','RH']
        for n in far:b.comp(a,ll[n])
        b.comp(a,b.shift(body,0,dip))
        # Housing foreground is drawn before near legs, then its actual
        # fixed pixels are restored; gaps in the native outline remain open.
        b.comp(a,b.shift(foreground,0,dip))
        for n in near:b.comp(a,ll[n])
        b.comp(a,b.shift(foreground,0,dip))
        st=b.shift(ref,0,dip);cut=(138 if v=='s' else 141)+dip
        a[:cut]=st[:cut]
        # Only enclosed join holes; no automatic slit fill in open leg gaps.
        holes=b.fill_holes(a[:,:,3]>0)&(a[:,:,3]==0)
        for y,x in zip(*np.where(holes)):a[y,x]=st[y,x] if st[y,x,3] else P['211e27']
        protected=b.shift(body,0,dip);b.comp(protected,b.shift(foreground,0,dip))
        for n in near:
            rr=next(q for q in rig if q['frame']==f and q['foot']==n)
            b.comp(protected,b.shift(parts[n]['lower'],*rr['delta']))
        # Cleanup is limited to redrawn connectors; every fixed pixel and
        # every exposed native pad pixel is locked against recolouring.
        b.comp(protected,b.shift(foreground,0,dip))
        edits=old.joint_cleanup(a,ref,b.shift(protected,0,-dip),parts,[q for q in rig if q['frame']==f],dip)
        save(a,f'walk/frames/{v}_f{f}.png');save(b.shift(body,0,dip),f'walk/layers/{v}_body_f{f}.png');save(b.shift(foreground,0,dip),f'walk/layers/{v}_foreground_f{f}.png')
        (R/f'walk/layers/{v}_join_edits_f{f}.json').write_text(json.dumps(edits))
        frames.append(a)
    path=R/'rig.json';allrig=json.loads(path.read_text()) if path.exists() else {};allrig[v]=rig;path.write_text(json.dumps(allrig,indent=2))
    report=R/'REPORT.txt';lines=report.read_text().splitlines() if report.exists() else ['hippo-walk35-run2; tokens: unavailable.','Reused run1 native translations/joints and fennec run2 front/back depth order.']
    lines=[s for s in lines if not s.startswith(v+':')];lines.append(v+': 8 native frames and source/layers saved; audit pending.');report.write_text('\n'.join(lines)+'\n')
    old.R=R;old.boards(v,ref,frames)
    print(v,'source soles',{n:q['sole'] for n,q in D.items()})
    return frames

def combine():
    for suffix in ['board.png','legs_zoom.png']:
        ims=[Image.open(R/f'{v}_{suffix}').convert('RGB') for v in ['s','n']]
        out=Image.new('RGB',(max(i.width for i in ims),sum(i.height for i in ims)));y=0
        for im in ims:out.paste(im,(0,y));y+=im.height
        out.save(R/suffix)
if __name__=='__main__':
    for v in sys.argv[1:] or ['s','n']:make(v)
    if all((R/f'{v}_board.png').exists() for v in ['s','n']):combine()
