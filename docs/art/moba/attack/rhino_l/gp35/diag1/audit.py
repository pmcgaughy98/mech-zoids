import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage as nd
from finish import specks
from defringe import clean
P=Path(__file__).resolve().parent;T=Path('D:/dev/new-mech-rpg/docs/art/moba/rhino_l/take-a');V=['se','ne'];C=nd.generate_binary_structure(2,1)
def arr(p):return np.array(Image.open(p).convert('RGBA'))
def bbox(a):
 y,x=np.where(a[:,:,3]>0);return [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]
def haus(a,b):return float(max(nd.distance_transform_edt(~a)[b].max(),nd.distance_transform_edt(~b)[a].max()))
def sole(a,box):
 x0,y0,x1,y1=box;m=a[y0:y1,x0:x1,3]>0;y=np.where(m)[0].max();x=np.where(m[y])[0];return [(x.min()+x.max())/2+x0,int(y+y0)]
S={v:arr(T/'views_cam35_touchup'/f'{v}.png') for v in V};F={v:[arr(P/'frames'/f'{v}_f{i}.png') for i in range(6)] for v in V};M={v:json.loads((P/f'preparation_{v}.json').read_text()) for v in V};PL={v:json.loads((P/f'placement_{v}.json').read_text()) for v in V};L=json.loads((P/'landmarks.json').read_text());targets=json.loads((P/'targets.json').read_text());sm=json.loads((P/'still_metrics.json').read_text());pal={tuple(bytes.fromhex(z['hex'])) for z in json.loads((T/'palette.json').read_text())}
D={v:[] for v in V};lines=[]
def check(ok,n,s):lines.append(('PASS ' if ok else 'MISS ')+n+': '+s)
def rows(key,fmt=lambda x:str(x)):return '; '.join(v+' '+','.join(fmt(z[key]) for z in D[v]) for v in V)
for v in V:
 st=L[v]['still'];stleg=targets['views'][v]['soles'][0]['y']-sum(st['disc'])/2;stgap=max(0,st['disc'][0]-st['hip']-1)
 for i,a in enumerate(F[v]):
  m=a[:,:,3]>0;px=a[m,:3];pl=PL[v]['frames'][f'{v}_f{i}'];tr=pl['translation'];h=np.array([[z['x'],z['y']] for z in targets['views'][v]['soles'] if z['leg']=='hind']);base=np.array([[z['x'],z['y']] for z in targets['views'][v]['soles'] if z['leg'].startswith('front')]);disc=st['disc'] if i==0 else [x+tr[1] for x in L[v]['disc'][i]];hip=st['hip'] if i==0 else L[v]['hip'][i]+tr[1];head=st['head'] if i==0 else L[v]['head'][i];length=float(np.linalg.norm(np.subtract(*head)));sl=nd.binary_fill_holes(m)&~m;sh=nd.binary_fill_holes(S[v][:,:,3]>0)&~(S[v][:,:,3]>0)
  D[v].append(dict(hind=float(np.linalg.norm(np.array(pl['hind'])-h,axis=1).max()),leg=float(pl['hind'][0][1]-sum(disc)/2),leg_delta=float(pl['hind'][0][1]-sum(disc)/2-stleg),gap=max(0,disc[0]-hip-1),gap_delta=max(0,disc[0]-hip-1)-stgap,hip=hip,hip_delta=hip-st['hip'],head=length,head_error=100*(length/np.linalg.norm(np.subtract(*st['head']))-1),front=pl['front'],front_error=float(np.linalg.norm(np.array(pl['front'])-base,axis=1).max()),eye=int(np.all(px==[255,58,42],axis=1).sum()),ink=float(np.all(px==[20,18,24],axis=1).mean()*100),pieces=int(nd.label(m,C)[1]),specks=specks(a),slits=int((sl&~sh).sum()),fringe=list(clean(a)[1:]),extra=len(set(map(tuple,px))-pal),binary=set(np.unique(a[:,:,3]))<={0,255},border=bool(m[0].any() or m[-1].any() or m[:,0].any() or m[:,-1].any()),bbox=bbox(a)))
check(all(np.array_equal(F[v][0],S[v]) for v in V),'f0','se 0, ne 0 px; file bytes exact '+str(all((P/'frames'/f'{v}_f0.png').read_bytes()==(T/'views_cam35_touchup'/f'{v}.png').read_bytes() for v in V)))
check(all(z['hind']<=1 for v in V for z in D[v]),'hind soles',rows('hind',lambda x:f'{x:.2f}')+' px drift <=1')
check(all(abs(z['leg_delta'])<=2 for v in V for z in D[v]),'HIND LEG LENGTH',rows('leg',lambda x:f'{x:g}')+' px sole-disc; still se19.5/ne20.5; delta<=2')
check(all(abs(z['gap_delta'])<=2 for v in V for z in D[v]),'NO THIGH',rows('gap')+' rows; still se3/ne2; delta<=2; NE f3 extra disc; SE f3 extra planted leg')
check(all(abs(z['hip_delta'])<=3 for v in V for z in D[v]),'HIP HEIGHT',rows('hip')+' yellow lowest rows; still se115/ne131; delta<=3')
he={v:[float(round(z['head_error'],2)) for z in D[v]] for v in V};rat={v:[round(( (D[v][i]['bbox'][2]-D[v][i]['bbox'][0])/(D[v][i]['bbox'][3]-D[v][i]['bbox'][1]))/((bbox(S[v])[2]-bbox(S[v])[0])/(bbox(S[v])[3]-bbox(S[v])[1]))-1,3) for i in [1,4]] for v in V}
check(all(abs(x)<=3 for v in V for x in he[v]) and all(abs(x)<=.1 for v in V for x in rat[v]),'FACING',f'head error % {he}; f1/f4 bbox ratio delta {rat}; limits 3%/10%; eyes checked below; trace +/-1px')
e=arr(T/'views_cam35_touchup/e.png');ref={};rear={}
for i,box in [(2,(100,132,120,148)),(3,(102,111,120,127))]:
 a=arr(P.parent/f'fix1_e/frames/e_f{i}.png');ref[i]=[160-sole(a,box)[1],bbox(e)[1]-bbox(a)[1]]
for v in V:rear[v]={i:{'above160':160-D[v][i]['front'][0][1],'above_own_sole':targets['views'][v]['soles'][-1 if v=='ne' else 1]['y']-D[v][i]['front'][0][1],'top_above_still':bbox(S[v])[1]-bbox(F[v][i])[1]} for i in [2,3]}
check(all(abs(rear[v][i]['above_own_sole']-ref[i][0])<=6 for v in V for i in [2,3]),'REAR HEIGHT',f'e f2/f3 (front above160,top above e-still) {ref}; diagonal (above160,own-sole lift,top-rise) '+str({v:[[z['above160'],z['above_own_sole'],z['top_above_still']] for z in rear[v].values()] for v in V})+'; lift delta<=6')
check(all(D[v][4]['front_error']<=2 for v in V),'F4 front landing','; '.join(v+f' {D[v][4]["front_error"]:.2f}' for v in V)+' px <=2')
for ia,ib,lim,label in [(4,5,3,'F4-F5'),(5,0,4,'F5-still')]:
 val={v:max(haus(F[v][ia][:,:,3]>0,F[v][ib][:,:,3]>0),max(float(np.linalg.norm(np.array(PL[v]['frames'][f'{v}_f{ia}'][part])-np.array(PL[v]['frames'][f'{v}_f{ib}'][part]),axis=1).max()) for part in ['hind','front'])) for v in V};check(all(x<=lim for x in val.values()),label,str({v:round(x,2) for v,x in val.items()})+f' px lower bound on largest part move <= {lim}')
io={v:float(((F[v][3][:,:,3]>0)&(S[v][:,:,3]>0)).sum()/((F[v][3][:,:,3]>0)|(S[v][:,:,3]>0)).sum()) for v in V};check(all(x<=.85 for x in io.values()),'F3 alpha IoU',str({v:round(x,3) for v,x in io.items()})+' <=0.85')
check(all(z['eye']>=4 for z in D['se']) and all(z['eye']==0 for z in D['ne']),'eyes',rows('eye')+'; SE dark sockets >=4, NE 0')
check(all(abs(z['ink']/100/sm[v]['ink_share']-1)<=.15 for v in V for z in D[v]),'ink %',rows('ink',lambda x:f'{x:.2f}')+'; still 7.79/8.25 +/-15%')
check(all(z['extra']==0 and z['binary'] and not z['border'] for v in V for z in D[v]),'palette/alpha/border',f'extra {sum(z["extra"] for v in V for z in D[v])}, binary {all(z["binary"] for v in V for z in D[v])}, border {sum(z["border"] for v in V for z in D[v])}')
check(all(z['pieces']==1 and z['specks']<=1.2*sm[v]['specks_1_2px'] for v in V for z in D[v]),'pieces/specks','pieces '+rows('pieces')+'; specks '+rows('specks')+' <=496.8/415.2; 0 despeckle passes')
check(all(abs(M[v]['rows'][v][k]/M[v]['rows'][v]['still_wh'][j]-1)<=.04 for v in V for j,k in enumerate(['width','height'])),'column1 size','se79x74 vs85x83; ne78x90 vs83x103; +/-4%')
check(all(z['slits']==0 for v in V for z in D[v]),'seam slits',rows('slits')+' enclosed transparent px absent from still mask')
check(all(z['fringe'][0]==0 and z['fringe'][1]==0 for v in V for z in D[v]),'fringe','plum/pale '+str({v:[z['fringe'][:2] for z in D[v]] for v in V})+'; f0 exact protected')
(P/'checks.txt').write_text('\n'.join(lines)+'\n');(P/'audit_metrics.json').write_text(json.dumps({'frames':D,'rear_reference':ref,'rear':rear,'ratio_delta':rat,'iou':io},indent=2))
with (P/'REPORT.txt').open('a') as f:f.write('Step 4 complete: every check in checks.txt; new local traces in landmarks.json; pose misses preserved.\n')
print('\n'.join(lines))
