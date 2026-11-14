p='D:/dev/new-mech-rpg/docs/art/moba/walk/lobster_l/run1/build.py'
s=open(p).read();s=s.replace("q['sole']=[(label[0]+label[1])/2,label[2]]", "q['label_sole']=[(label[0]+label[1])/2,label[2]];q['sole']=b.support(foot).tolist()")
open(p,'w').write(s)
p='D:/dev/new-mech-rpg/docs/art/moba/walk/lobster_l/run1/verify.py';s=open(p).read().replace("sole=np.array(rr['source_sole'])", "sole=b.support(src)")
s=s.replace("Sole references are the supplied labelled sole centres; pixel stamp independently recovers each displacement.", "Sole centres are measured from the source foot bottom two painted rows; exhaustive pixel stamp independently recovers each displacement.")
open(p,'w').write(s)
