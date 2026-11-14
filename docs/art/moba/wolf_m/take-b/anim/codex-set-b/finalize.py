from finish import *
for name in TIMES:
 finalize(name)
 board=Image.open(R/name/'review.png')
 (R/name/'review_pages').mkdir(exist_ok=True)
 for j in range(0,len(TIMES[name]),2):
  inds=[0,j+1]+([j+2] if j+1<len(TIMES[name]) else [])
  b=Image.new('RGB',(640*len(inds),1440),'#596159')
  for c,idx in enumerate(inds):b.paste(board.crop((idx*640,0,(idx+1)*640,1440)),(c*640,0))
  b.save(R/name/'review_pages'/f'frames_{j}_{min(j+1,len(TIMES[name])-1)}.png')
 h='<html><meta charset="utf-8"><title>Wolf '+name+' animation review</title><style>body{background:#596159;color:white;font:16px sans-serif}img{image-rendering:pixelated;width:640px}section{display:flex}a{color:cyan}</style><nav>'+' '.join(f'<a href="../{n}/playback.html">{n}</a>' for n in TIMES)+'</nav><h1>'+name+'</h1><section>'+''.join(f'<div>{v}<br><img src="preview_{v}.gif"></div>' for v in V)+'</section><p>Sel-out applied at native scale, enlarged 4x. All three GIFs use requested timing.</p></html>'
 (R/name/'playback.html').write_text(h)
(R/'review.html').write_text('<html><body><h1>Wolf set B</h1>'+''.join(f'<p><a href="{n}/playback.html">{n} playback</a> | <a href="{n}/review.png">4x board</a></p>' for n in TIMES)+'</body></html>')
print('boards, pages, playback built')
