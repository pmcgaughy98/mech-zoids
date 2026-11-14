"""Independent exhaustive run1 colour stamps plus trunk belly/full-pad audits."""
import sys
sys.dont_write_bytecode=True
import json,ast
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import label
import build as m
R=m.R;b=m.b;T=m.T;X=m.X;Y=m.Y;load=m.load
tree=ast.parse((R.parents[2]/'walk/tools/walk_tools.py').read_text());ns={'np':np}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='find_slits'],type_ignores=[]),'walk_tools.py','exec'),ns)
find_slits=ns['find_slits']
def specks(a):
    total=0
    for c in set(map(tuple,a[a[:,:,3]>0])):
        lab,num=label(np.all(a[120:165]==c,axis=2),np.ones((3,3)))
        sizes=np.bincount(lab.ravel())[1:];total+=int(((sizes>0)&(sizes<=2)).sum())
    return total
def audit():
    lines=['hippo-walk35-run2: independent run1 exhaustive native sole-stamp search.',
    'Full lower/pad = ALL opaque source lower pixels, including native heel and dark recess.',
    'Composite pad exceptions only actual translated fixed foreground overlap; full layer must match 100%.',
    'Body belly = trunk layer, with head/jaw, shoulder/hip discs and rump/tail separately pinned foreground.',
    'No source body fill or contour extension is used. Real leg/jaw gaps remain open.',
    'GIF 120/130ms alternating (1s loop); APNG exact125ms.']
    result={};fails=[];font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15)
    rig=json.loads((R/'rig.json').read_text())
    for v in ['s','n']:
        if not (R/f'walk/frames/{v}_f7.png').exists():continue
        ref=load(R/f'stills/{v}.png');frames=[load(R/f'walk/frames/{v}_f{f}.png') for f in range(8)]
        body=load(R/f'source/{v}_body.png');pinned=load(R/f'source/{v}_pinned.png');fg=load(R/f'source/{v}_foreground.png')
        allowed=set(map(tuple,ref[ref[:,:,3]>0]));vr=dict(still_specks=specks(ref),structure=[],feet={},belly=[]);result[v]=vr
        near=['RF','LF'] if v=='s' else ['LH','RH']
        for n in near:
            src=load(R/f'source/{v}_{n}_lower.png');yy,xx=np.where(src[:,:,3]>0);l=int(xx.min());r=int(xx.max())
            # Lowest body rows just outside native leg column span.
            rows=lambda x:np.where(body[:,x,3]>0)[0]
            lr=rows(l-1);rr=rows(r+1)
            # A front foot projects beyond the trunk silhouette; its outer
            # neighbour is transparent. Record that fact rather than inventing
            # a belly pixel. The conservative bound is the trunk's lowest row.
            bound=int(np.where(body[:,:,3]>0)[0].max())
            left=int(lr.max()) if len(lr) else bound;right=int(rr.max()) if len(rr) else bound;ex=[]
            for x in range(l,r+1):
                ys=rows(x)
                if len(ys):ex.append(float(ys.max()-(left+(right-left)*(x-l+1)/(r-l+2))))
            q=dict(foot=n,span=[l,r],outside_rows=[int(lr.max()) if len(lr) else None,int(rr.max()) if len(rr) else None],transparent_exterior_uses_conservative_trunk_bound=bound,max_below_line=max(ex),pass_belly=max(ex)<=1)
            vr['belly'].append(q);lines.append('BELLY '+v+' '+json.dumps(q))
            if not q['pass_belly']:fails.append(f'{v} {n} belly')
        for f,a in enumerate(frames):
            op=a[:,:,3]>0;dip=int(f in [0,4]);st=b.shift(ref,0,dip);cut=(138 if v=='s' else 141)+dip
            d=np.any(a[:cut]!=st[:cut],axis=2);pin=b.shift(pinned,0,dip);mask=pin[:,:,3]>0
            cc=b.pieces(op);sl=find_slits(a,ref,dip);bm=b.shift(body,0,dip)
            q=dict(frame=f,binary_alpha=bool(np.isin(a[:,:,3],[0,255]).all()),off_palette_pixels=sum(tuple(c) not in allowed for c in a[op]),colours=len(set(map(tuple,a[op]))),components=len(cc),stray_pixels=sum(map(len,cc[1:])),holes=int((b.fill_holes(op)&~op).sum()),edge=bool(op[[0,-1]].any() or op[:,[0,-1]].any()),lowest_row=int(np.where(op)[0].max()),upper_diff_percent=float(100*d.sum()/d.size),pinned_diff_pixels=int(np.any(a[mask]!=pin[mask],axis=1).sum()),specks=specks(a),seams=sl,body_slits=[p for p in sl if bm[p[1],p[0],3]])
            vr['structure'].append(q);lines.append('STRUCT '+v+' '+json.dumps(q))
            for key,ok in [('structure',q['components']==1 and not q['holes'] and not q['edge'] and not q['off_palette_pixels'] and q['binary_alpha']),('upper',not d.any()),('pinned',not q['pinned_diff_pixels']),('specks',q['specks']<=vr['still_specks']+2),('body_slits',not q['body_slits'])]:
                if not ok:fails.append(f'{v} f{f} {key}')
        footprint=Image.new('RGB',(1480,1080),(58,66,62));dr=ImageDraw.Draw(footprint)
        for j,n in enumerate(['RF','LH','LF','RH']):
            src=load(R/f'source/{v}_{n}_lower.png');sole=b.support(src);yy,xx=np.where(src[:,:,3]>0);pts=[];tracks=[]
            for f,a in enumerate(frames):
                layer=load(R/f'walk/layers/{v}_{n}_f{f}.png');p,score,delta,ends=b.locate(a,src);where='composite'
                if score<1 or not ends:p,score,delta,ends=b.locate(layer,src);where='leg layer (occluded)'
                rr=next(q for q in rig[v] if q['foot']==n and q['frame']==f);target=np.array(rr['target']);dx,dy=delta
                # Exhaustive stamp determines position; rig is used only AFTER
                # locating, to compare target and lift.
                match=np.all(layer[yy+dy,xx+dx]==src[yy,xx],axis=1)
                fgs=b.shift(fg,0,int(f in [0,4]));oc=fgs[yy+dy,xx+dx,3]>0
                cmp=np.all(a[yy+dy,xx+dx]==src[yy,xx],axis=1)
                far=n not in near
                valid=(cmp|oc) if not far else np.ones_like(cmp)
                err=np.abs(p-target);off,lift=T['paths'][n][f]
                ground=sole[1]+int(np.floor(off*T['views'][v]['f']*T['views'][v]['u'][1]+.5))
                measured_lift=float(ground-p[1])
                knee=load(R/f'source/{v}_{n}_knee.png');ky,kx=np.where(knee[:,:,3]>0);kd=rr['knee_delta']
                # A rising whole lower block legitimately covers the bottom
                # of its knee. Compare the remaining native knee pixels only.
                translated=b.shift(src,dx,dy);exposed=translated[ky+kd[1],kx+kd[0],3]==0
                km=float(np.all(layer[ky[exposed]+kd[1],kx[exposed]+kd[0]]==knee[ky[exposed],kx[exposed]],axis=1).mean())
                q=dict(frame=f,sole=p.tolist(),measured_from=where,stamp_match=score,endpoints=ends,delta=delta,target=target.tolist(),target_error_xy=err.tolist(),lift=lift,measured_lift=measured_lift,whole_pad_layer_match=float(match.mean()),whole_pad_frame_match_except_foreground=float(valid.mean()) if not far else 'hidden; layer deciding',foreground_pad_pixels=int(oc.sum()),native_knee_match=km,articulated_length_error=rr['leg_length_error'])
                tracks.append(q);pts.append(p);lines.append('PAD_CONTACT '+v+' '+n+' '+json.dumps(q))
                if err.max()>1 or score!=1 or not ends or measured_lift!=lift:fails.append(f'{v} {n} f{f} contact')
                if not match.all() or not valid.all() or km!=1:fails.append(f'{v} {n} f{f} whole parts')
                if rr['leg_length_error']>1:fails.append(f'{v} {n} f{f} length')
            start=(T['gait'][n]+3)%8;order=[(start+k)%8 for k in range(5)];step=np.array(T['views'][v]['planted_step_px']);locked=np.array([pts[f]-k*step for k,f in enumerate(order)]);spread=np.ptp(locked,axis=0)
            vr['feet'][n]=dict(spread_xy=spread.tolist(),max_target_error=float(max(max(q['target_error_xy']) for q in tracks)),frames=tracks)
            if spread.max()>2:fails.append(f'{v} {n} lock')
            oy=j*270;dr.text((10,oy+4),f'{v} {n} planted {order}; measured spread {spread[0]:.3f}/{spread[1]:.3f}px',font=font,fill='white')
            for k,f in enumerate(order):dr.text((10,oy+28+k*19),f'f{f} sole {pts[f].tolist()} locked {locked[k].round(3).tolist()} {tracks[f]["measured_from"]}',font=font,fill='white')
            for f in range(8):
                box=(int(sole[0])-18,int(sole[1])-21,int(sole[0])+18,int(sole[1])+7)
                source=frames[f] if tracks[f]['measured_from']=='composite' else load(R/f'walk/layers/{v}_{n}_f{f}.png')
                tile=Image.new('RGBA',(144,112),(73,79,75));tile.alpha_composite(Image.fromarray(source).crop(box).resize((144,112),Image.Resampling.NEAREST));footprint.paste(tile.convert('RGB'),(10+180*f,oy+157));dr.text((10+180*f,oy+137),f'f{f}',font=font,fill='white')
            colors=['#ffb575','#75e5cf','#e99fe2','#c9e978','#aab8ff'];origin=locked.mean(0)
            for k,f in enumerate(order):
                dx,dy=tracks[f]['delta'];ys,xs=np.where((src[:,:,3]>0)&(Y>=sole[1]-1))
                for y,x in zip(ys,xs):
                    px,py=np.floor((np.array([x+dx,y+dy])-k*step-origin)*6+[1200,oy+50]).astype(int);dr.rectangle((px,py,px+5,py+5),fill=colors[k])
        footprint.save(R/f'{v}_footprints.png')
        print(v,'specks',vr['still_specks'],[s['specks'] for s in vr['structure']],'pinned',[s['pinned_diff_pixels'] for s in vr['structure']])
        print(v,'feet',{n:(q['spread_xy'],q['max_target_error']) for n,q in vr['feet'].items()})
    result['failures']=fails;(R/'verification.json').write_text(json.dumps(result,indent=2));lines.append('FAILURES '+repr(fails));(R/'checks.txt').write_text('\n'.join(lines)+'\n');print('FAILURES',fails)
    return result
if __name__=='__main__':audit()
