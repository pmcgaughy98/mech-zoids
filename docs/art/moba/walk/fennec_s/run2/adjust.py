p='frontback.py'
s=open(p,encoding='utf-8-sig').read().replace("'RH':dict(root=(82,133),k=(82,139),join=(82,143))","'RH':dict(root=(84,129),k=(84,135),join=(82,139))").replace("'LH':dict(root=(109,133),k=(109,139),join=(109,143))","'LH':dict(root=(107,129),k=(107,135),join=(109,139))").replace("-3 if n=='RH' else 3,4","-1 if n=='RH' else 1,0")
open(p,'w',encoding='utf-8').write(s)
