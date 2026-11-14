from pathlib import Path
import sys, shutil, json
sys.dont_write_bytecode=True
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as nd
P=Path(__file__).parent
HEX='141218 211e27 2e1a6e 3d3a44 3fe8b0 6a3cc8 9d9ba2 a46bff b8923a c8fff0 d6d6dc e0c8ff f0d27a f6fffb fff4d6'.split()
PAL=np.array([list(bytes.fromhex(h)) for h in HEX],np.uint8)
def load(p):return np.array(Image.open(p).convert('RGBA'))
def snap(rgb):return ((rgb.astype(float)[...,None,:]-PAL.astype(float))**2).sum(-1).argmin(-1)
def extract(view):
    raw=load(P/f'sheet_raw_{view}.png')
    rgb=raw[:,:,:3].astype(int)
    fg=~((rgb[:,:,0]>175)&(rgb[:,:,1]<80)&(rgb[:,:,2]>160))
    labs,n=nd.label(fg,np.ones((3,3)))
    obs=[s for i,s in enumerate(nd.find_objects(labs),1) if s and (labs[s]==i).sum()>1200]
    obs.sort(key=lambda s:s[1].start)
    print(view,'objects',[(s[1].start,s[0].start,s[1].stop,s[0].stop) for s in obs])
    assert len(obs)==6
    still=Image.open(P/f'refs/still_{view}.png').convert('RGBA');sw,sh=still.crop(still.getbbox()).size
    s0=obs[0];scale=(sw/(s0[1].stop-s0[1].start)+sh/(s0[0].stop-s0[0].start))/2
    (P/'frames').mkdir(exist_ok=True)
    shutil.copyfile(P/f'refs/still_{view}.png',P/f'frames/{view}_f0.png')
    for f,s in enumerate(obs[1:],1):
        crop=Image.fromarray(raw[s]);size=(round(crop.width*scale),round(crop.height*scale))
        im=np.array(crop.resize(size,Image.Resampling.NEAREST));idx=snap(im[:,:,:3])
        mask=np.array(Image.fromarray((fg[s]*255).astype('uint8')).resize(size,Image.Resampling.NEAREST))>0
        mask=nd.binary_fill_holes(mask)
        lab,n=nd.label(mask,np.ones((3,3)));counts=np.bincount(lab.ravel());counts[0]=0;mask=lab==counts.argmax()
        nearest=nd.distance_transform_edt(~mask,return_distances=False,return_indices=True)
        idx[~mask]=idx[tuple(nearest[:,~mask])]
        a=np.zeros((160,160,4),np.uint8)
        # Whole drawing at fixed native scale; each fall pivots around the same standing body.
        centre=79 if view=='se' else [0,79,80,82,88,92][f]
        x=round(centre-size[0]/2);y=141-size[1]
        a[y:141,x:x+size[0],:3]=PAL[idx];a[y:141,x:x+size[0],3]=mask*255;a[a[:,:,3]==0]=0
        Image.fromarray(a).save(P/f'frames/{view}_f{f}.png')
    settle(view)
def settle(view):
    a=load(P/f'frames/{view}_f5.png')
    for c in PAL[[4,9,13]]:a[(a[:,:,:3]==c).all(-1)&(a[:,:,3]>0),:3]=PAL[2]
    Image.fromarray(a).save(P/f'frames/{view}_f6.png')
def workboard(view):
    board=Image.new('RGB',(6*660,650),'#5a6058');d=ImageDraw.Draw(board)
    for f in range(6):
        im=Image.open(P/f'frames/{view}_f{f}.png').crop((40,50,150,145)).resize((660,570),Image.Resampling.NEAREST)
        board.paste(im,(f*660,25),im);d.text((f*660+10,8),f'{view} f{f}',fill='white')
    board.save(P/f'work_{view}.png')
def repaint(view):
    for f in range(1,6):
        a=load(P/f'frames/{view}_f{f}.png');im=Image.fromarray(a);d=ImageDraw.Draw(im)
        def poly(c,p):d.polygon(p,fill=tuple(PAL[HEX.index(c)])+(255,))
        def line(c,p):d.line(p,fill=tuple(PAL[HEX.index(c)])+(255,),width=1)
        if view=='back' and f>=3:
            # Remove the generator's broad rounded ear silhouettes and redraw complete
            # pointed ears and rear cranium in their new orientations, pixel polygons.
            cutoff={3:106,4:117,5:115}[f]
            d.rectangle((0,0,159,cutoff),fill=(0,0,0,0))
            if f==3:
                poly('141218',[(75,102),(83,99),(92,104),(96,111),(92,115),(80,114),(74,109)])
                poly('2e1a6e',[(75,99),(80,94),(88,95),(94,102),(95,108),(90,112),(80,111),(74,106)])
                poly('6a3cc8',[(77,98),(81,95),(87,96),(92,102),(92,107),(87,109),(78,106)])
                poly('a46bff',[(79,97),(83,96),(87,98),(89,103),(87,105),(78,104)])
                poly('e0c8ff',[(81,97),(84,97),(86,99),(86,101),(83,102),(80,101)])
                ears=[([(58,78),(64,79),(74,87),(81,97),(81,103),(76,106),(69,102),(62,94),(58,86)],[(59,79),(64,81),(73,89),(78,97),(77,101),(72,99),(65,92),(60,85)],[(59,79),(62,80),(68,85),(68,87),(65,86),(61,83)]),
                      ([(108,80),(109,85),(105,94),(99,103),(93,107),(88,104),(87,99),(93,91),(101,84)],[(107,82),(107,87),(102,95),(96,101),(92,102),(90,100),(96,92),(103,85)],[(105,82),(107,82),(105,86),(103,88),(101,88),(102,85)])]
            elif f==4:
                poly('211e27',[(80,119),(85,113),(92,115),(95,119),(91,125),(85,125),(80,122)])
                poly('3d3a44',[(82,119),(86,115),(90,117),(91,120),(87,123),(83,122)])
                poly('141218',[(84,108),(92,109),(100,115),(99,120),(93,123),(86,119),(81,114)])
                poly('2e1a6e',[(88,100),(96,101),(103,108),(105,114),(102,119),(95,121),(87,117),(83,111)])
                poly('6a3cc8',[(90,101),(96,102),(101,108),(102,114),(97,117),(89,114),(86,108)])
                poly('a46bff',[(90,102),(95,103),(98,107),(97,112),(91,113),(87,109)])
                poly('e0c8ff',[(91,103),(94,103),(96,105),(94,107),(90,107)])
                ears=[([(104,79),(107,81),(107,87),(103,98),(97,107),(92,109),(88,105),(89,99),(95,89),(101,82)],[(104,81),(105,84),(103,92),(98,101),(93,105),(91,103),(93,96),(99,86)],[(103,81),(104,81),(104,85),(102,88),(100,89),(101,85)]),
                      ([(119,91),(121,94),(120,100),(114,109),(106,116),(100,117),(97,114),(98,108),(106,100),(115,93)],[(118,93),(119,96),(116,103),(110,110),(104,113),(101,113),(101,109),(109,101)],[(117,93),(119,94),(117,97),(114,99),(112,99),(114,96)])]
            else:
                # Rear head remains visible below the flattened ears; broad neck joins torso.
                poly('141218',[(93,120),(103,119),(111,125),(110,133),(104,137),(96,134),(91,128)])
                poly('2e1a6e',[(96,111),(104,110),(112,116),(115,123),(113,130),(108,134),(100,132),(94,126),(91,119)])
                poly('6a3cc8',[(96,113),(103,112),(110,117),(112,123),(110,129),(105,131),(99,128),(94,122)])
                poly('a46bff',[(97,113),(102,113),(108,117),(109,121),(106,125),(101,125),(96,121),(94,117)])
                poly('e0c8ff',[(97,114),(101,114),(104,116),(104,118),(100,119),(96,117)])
                poly('d6d6dc',[(98,114),(100,115),(102,115),(102,117),(99,117)])
                ears=[([(125,100),(129,101),(129,105),(125,112),(115,120),(107,123),(102,122),(100,118),(102,114),(112,107),(120,102)],[(125,102),(127,103),(125,108),(118,114),(109,119),(104,120),(102,118),(108,113),(118,105)],[(124,102),(126,102),(125,105),(121,108),(118,108),(120,105)]),
                      ([(136,118),(137,121),(133,126),(122,133),(113,136),(107,135),(104,132),(105,128),(114,123),(127,119)],[(134,120),(135,121),(131,125),(121,130),(113,133),(108,132),(107,130),(115,126),(127,122)],[(132,120),(134,120),(132,122),(127,124),(123,124),(127,121)])]
            # Reconstructed ear plates, not image cutouts: each rear leaf is 33px
            # from root to tip, with a 17px broad middle matching the still.
            axes={3:[((78,103),(58,78)),((90,104),(109,78))],
                  4:[((95,111),(105,80)),((103,115),(124,90))],
                  5:[((103,119),(131,102)),((110,130),(140,117))]}[f]
            for base,tip in axes:
                b=np.array(base,float);u=np.array(tip,float)-b;u=u/np.linalg.norm(u);v=np.array([-u[1],u[0]])
                def ep(c,points):poly(c,[tuple(np.rint(b+u*x+v*y).astype(int)) for x,y in points])
                ep('2e1a6e',[(0,-3),(6,-8),(17,-8),(26,-4),(33,0),(28,4),(20,8),(9,9),(2,5)])
                ep('6a3cc8',[(2,-3),(7,-7),(17,-7),(26,-3),(32,0),(26,3),(18,6),(8,6),(3,3)])
                ep('a46bff',[(5,-4),(9,-7),(18,-6),(25,-3),(31,0),(24,2),(17,3),(9,3),(5,1)])
                ep('e0c8ff',[(18,-6),(25,-3),(32,0),(28,1),(24,-1),(22,-1),(21,-3),(18,-3)])
                ep('d6d6dc',[(24,-3),(28,-1),(31,0),(28,0),(25,-1)])
                # One-pixel attachment seam, short and continuous.
                d.line([tuple(np.rint(b+v*z).astype(int)) for z in (-3,3)],fill=tuple(PAL[0])+(255,),width=1)
            # Continuous neck seam and hinge plates; no stippled interior ink.
            if f==3:
                line('141218',[(77,111),(82,113),(88,114)])
                line('9d9ba2',[(74,114),(73,117)])
            elif f==4:line('141218',[(85,115),(89,119),(94,121)])
            else:
                line('141218',[(93,125),(97,130),(102,133)])
                poly('2e1a6e',[(88,130),(94,128),(98,131),(96,135),(90,136),(86,134)])
                poly('9d9ba2',[(88,131),(92,130),(95,132),(93,134),(89,134)])
                line('d6d6dc',[(88,131),(91,131)])
        if view=='se' and f==5:
            d.rectangle((67,105,114,130),fill=(0,0,0,0))
            # Broad flank remains at standing scale behind the laid-down head/ears.
            poly('2e1a6e',[(63,123),(68,117),(77,116),(84,120),(87,126),(83,132),(74,133),(66,129)])
            poly('6a3cc8',[(65,122),(69,118),(77,117),(82,120),(85,125),(81,129),(73,130),(67,127)])
            poly('a46bff',[(67,121),(70,118),(76,118),(81,121),(81,124),(76,126),(70,125)])
            line('e0c8ff',[(69,119),(73,118),(76,118)])
            line('9d9ba2',[(64,123),(65,126),(67,128)])
            # The far ear is also an intact leaf lying along the upper flank.
            poly('2e1a6e',[(68,112),(75,112),(84,116),(92,121),(95,125),(92,128),(85,127),(77,123),(71,118),(67,115)])
            poly('6a3cc8',[(69,113),(75,113),(83,117),(91,121),(93,125),(90,126),(83,124),(76,120),(70,117)])
            poly('a46bff',[(69,113),(74,113),(82,116),(87,119),(83,119),(76,117),(71,116)])
            line('e0c8ff',[(69,113),(73,113),(77,115)])
            poly('141218',[(73,115),(78,116),(86,120),(92,123),(92,125),(88,126),(81,122),(76,119)])
            poly('b8923a',[(74,116),(78,117),(85,120),(91,123),(91,125),(88,125),(81,121),(77,119)])
            poly('f0d27a',[(75,116),(78,117),(85,121),(90,123),(90,124),(87,124),(81,120),(77,118)])
            # Redraw the upright generated face as a cheek-down head; no source parts
            # are copied or transformed. Preserve the two long ground-resting ears.
            d.rectangle((91,118,118,140),fill=(0,0,0,0))
            poly('141218',[(87,121),(94,119),(100,121),(103,126),(102,133),(97,138),(90,138),(85,134),(84,127)])
            poly('2e1a6e',[(87,122),(93,120),(99,122),(101,126),(100,132),(96,136),(90,137),(86,132),(85,127)])
            poly('6a3cc8',[(87,122),(93,120),(98,122),(100,126),(98,130),(94,134),(89,133),(86,129)])
            poly('a46bff',[(88,122),(92,121),(97,123),(98,127),(95,130),(91,132),(88,129),(86,126)])
            poly('e0c8ff',[(88,123),(91,122),(94,123),(96,125),(96,127),(93,129),(90,129),(88,127)])
            poly('d6d6dc',[(89,123),(91,123),(91,124),(94,124),(95,126),(93,127),(92,126),(90,127),(88,126)])
            poly('141218',[(99,130),(103,131),(108,135),(108,138),(104,140),(97,139),(95,136)])
            poly('b8923a',[(100,131),(104,133),(107,136),(107,138),(104,139),(98,138),(97,135)])
            poly('f0d27a',[(100,131),(103,133),(105,134),(106,137),(103,138),(99,137),(98,135)])
            poly('fff4d6',[(100,132),(102,133),(102,135),(105,136),(104,137),(100,136),(99,134)])
            line('141218',[(99,127),(99,130),(97,133),(94,135)])
            line('3fe8b0',[(100,128),(99,131),(97,134)])
            line('c8fff0',[(99,129),(99,130),(98,132),(97,133)])
            line('f6fffb',[(99,130),(98,131)])
            # Four folded limb segments overlap the flank, behind the head/ear roots.
            poly('141218',[(65,128),(71,125),(76,126),(80,131),(78,136),(73,138),(66,136)])
            poly('2e1a6e',[(66,128),(71,126),(75,127),(78,131),(76,135),(70,136),(66,134)])
            poly('6a3cc8',[(66,128),(71,127),(74,128),(76,131),(73,133),(68,132)])
            line('a46bff',[(67,128),(71,128),(73,129)])
            poly('141218',[(75,132),(81,130),(85,132),(85,136),(80,139),(75,138)])
            poly('9d9ba2',[(76,133),(80,132),(83,133),(83,136),(79,137),(76,136)])
            line('d6d6dc',[(77,133),(80,133)])
            # Resting near ear laid over the forelimbs, whole gold inset and violet rim.
            poly('141218',[(57,136),(62,130),(72,127),(83,128),(90,133),(91,137),(87,140),(72,140),(62,139)])
            poly('2e1a6e',[(58,136),(63,131),(73,128),(83,129),(89,133),(90,136),(86,139),(73,139),(63,138)])
            poly('6a3cc8',[(59,135),(64,131),(74,128),(82,129),(86,131),(78,131),(69,133),(63,136)])
            line('a46bff',[(59,135),(64,131),(73,129),(80,129)])
            line('e0c8ff',[(60,134),(63,132),(66,132)])
            poly('b8923a',[(64,136),(70,133),(79,132),(84,133),(88,136),(85,138),(73,138)])
            poly('f0d27a',[(65,135),(72,133),(79,133),(83,134),(85,136),(82,137),(73,137),(68,136)])
            line('fff4d6',[(68,134),(73,133),(77,133)])
            # Bent thigh -> short shin -> silver foot remain visible above the near ear.
            poly('211e27',[(65,123),(69,121),(73,123),(74,127),(71,130),(66,128)])
            poly('6a3cc8',[(66,123),(69,122),(72,124),(72,126),(69,128),(66,126)])
            line('a46bff',[(66,123),(69,123),(71,124)])
            poly('211e27',[(69,128),(73,127),(76,129),(75,132),(70,133),(68,131)])
            poly('9d9ba2',[(70,129),(73,128),(75,130),(74,131),(70,132),(69,131)])
            line('d6d6dc',[(70,129),(72,129)])
            poly('211e27',[(79,127),(82,126),(85,128),(84,131),(80,131),(78,130)])
            poly('9d9ba2',[(80,128),(82,127),(84,129),(82,130),(80,130)])
        # Explicit native plate seams on the generated early cells, read against still.
        if view=='se' and f<5:
            dy={1:0,2:5,3:11,4:17}[f]
            line('141218',[(79,106+dy),(81,110+dy),(85,112+dy)])
            line('141218',[(82,111+dy),(85,112+dy),(89,112+dy)])
            line('141218',[(68,122),(70,125),(72,126)])
            line('141218',[(73,128),(75,129),(77,129)])
            line('141218',[(62,119),(62,122),(64,125)])
            line('141218',[(55,115),(53,118),(54,120)])
            if f<4:
                line('141218',[(80,126),(81,130),(83,132)])
                line('141218',[(89,125),(89,129),(91,130)])
                line('141218',[(82,137),(86,137),(87,136)])
                line('141218',[(95,136),(99,136)])
        if view=='back' and f<3:
            dy=0 if f==1 else 6
            line('141218',[(70,115),(70,119),(72,121)])
            line('141218',[(87,115),(88,120),(87,123)])
        a=np.array(im)
        if (view=='se' and f<5) or (view=='back' and f<3):
            a[load(P/f'frames/{view}_f{f}.png')[:,:,3]==0]=0
        # Native cleanup: repair palette speckles, ink islands, enclosed pinholes.
        mask=a[:,:,3]>0;idx=snap(a[:,:,:3]);idx[~mask]=0
        # Raw sprites have material edges, not a baked black contour.
        if (view=='se' and f==5) or (view=='back' and f>=3):
            edge=mask&~nd.binary_erosion(mask)
            idx[edge&(idx==0)]=1
        if view=='back':
            idx[np.isin(idx,[4,9,13])&mask]=10
        if view=='se' and f==5:
            yy,xx=np.indices(mask.shape)
            # Broad black generator joins become shadow material; single ink seams remain.
            shade=((yy>=138)&(xx<91))|((xx>=99)&(yy<132))|((xx<=87)&(yy>=124)&(yy<=130))
            idx[shade&(idx==0)&mask]=2
            steel=((xx>=87)&(xx<=93)&(yy<=127))|((xx>=74)&(xx<=83)&(yy<=117))
            idx[steel&(idx==11)&mask]=10
        for color in [0,4,9,13]:
            lab,n=nd.label((idx==color)&mask,np.ones((3,3)))
            for label,s in enumerate(nd.find_objects(lab),1):
                if s is None:continue
                region=lab==label
                if region.sum()>1:continue
                y,x=np.argwhere(region)[0]
                if color in [4,9,13] and view=='se' and x>85:continue
                if color==0 and nd.binary_erosion(mask)[y,x]:
                    around=idx[max(0,y-1):y+2,max(0,x-1):x+2].ravel();around=around[around!=0]
                    if len(around):idx[y,x]=np.bincount(around,minlength=15).argmax()
                elif color in [4,9,13]:idx[y,x]=7
        holes=nd.binary_fill_holes(mask)&~mask
        if holes.any():
            near=nd.distance_transform_edt(~mask,return_distances=False,return_indices=True)
            idx[holes]=idx[tuple(near[:,holes])];mask|=holes
        a[:,:,:3]=PAL[idx];a[:,:,3]=mask*255;a[~mask]=0
        # Final short continuous overlaps, clipped to the existing whole drawing.
        im=Image.fromarray(a);d=ImageDraw.Draw(im)
        if view=='se' and f==5:
            line('141218',[(65,125),(68,128),(72,129)])
            line('141218',[(65,135),(71,132),(78,132),(82,133)])
            line('141218',[(85,119),(90,117),(94,117)])
        if view=='back' and f==2:
            line('141218',[(74,119),(77,121),(83,121),(86,119)])
            line('141218',[(74,109),(79,110),(83,110),(86,109)])
        if view=='back' and f>=4:
            if f==4:
                line('141218',[(85,116),(88,120),(93,122)])
                line('141218',[(70,126),(73,129),(74,132)])
                line('141218',[(81,130),(84,132),(86,132)])
            else:
                line('141218',[(94,119),(94,123),(97,127),(101,130)])
                line('141218',[(71,124),(74,127),(75,130)])
                line('141218',[(83,127),(85,130),(88,131)])
                line('141218',[(92,133),(95,134),(98,134)])
        a=np.array(im);a[~mask]=0
        Image.fromarray(a).save(P/f'frames/{view}_f{f}.png')
    settle(view)
if __name__=='__main__':
    for v in sys.argv[1:] or ['se','back']:extract(v);repaint(v);workboard(v)
