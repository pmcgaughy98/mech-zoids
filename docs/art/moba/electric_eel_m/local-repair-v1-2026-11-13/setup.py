from pathlib import Path
ROOT=Path(__file__).parent;previous=ROOT.parent/'dragonfly-review-2026-11-13'
for name in ['diagnose_model.py','render_model.py']:
 s=(previous/name).read_text();s=s.replace('dragonfly-review-2026-11-13','electric-eel-review-2026-11-13').replace('dragonfly_m','electric_eel_m').replace("e['id']=='dragonfly'","e['id']=='electric_eel'").replace('Meshy_AI_dragonfly_remeshed_25k_20261111_character.glb','Meshy_AI_electric_eel_remeshed_25k_20261108_character.glb').replace('dragonfly-rigged-local-repair-v1.glb','electric-eel-rigged-local-repair-v1.glb').replace('ORIGINAL_DRAGONFLY_','ORIGINAL_ELECTRIC_EEL_');(ROOT/name).write_text(s)
