from pathlib import Path
ROOT=Path(__file__).parent
s=Path('D:/dev/_scratch/mech-art-direction/bison-review-2026-11-11/analyze_repair.py').read_text().replace('Meshy_AI_bison_remeshed','Meshy_AI_chameleon_remeshed')
s=s.replace("print('JOINT CENTERS',json.dumps([{'bone':v['bone'],'n':v['influenced_vertices'],'center':v['center_gltf']} for v in rows]))", "print('JOINT REGIONS SAVED',len(rows))")
exec(compile(s,str(ROOT/'analyze_repair.py'),'exec'))
