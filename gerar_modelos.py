# Gera modelos 3D de exemplo (.glb) em escala real (metros). Prato com 26 cm.
# Inclui normais e UVs (necessários para o AR Quick Look do iPhone).
import struct, json, math
def lathe(profile, seg=48):
    n=len(profile); P=[];UV=[];I=[]
    for s in range(seg+1):
        a=2*math.pi*s/seg
        for k,(r,y) in enumerate(profile):
            P.append((r*math.cos(a),y,r*math.sin(a))); UV.append((s/seg,k/(n-1)))
    for s in range(seg):
        for k in range(n-1):
            a,b,c,d=s*n+k,s*n+k+1,(s+1)*n+k,(s+1)*n+k+1
            I+=[a,c,b,b,c,d]
    N=[[0,0,0] for _ in P]
    def sub(u,v):return [u[i]-v[i] for i in range(3)]
    for t in range(0,len(I),3):
        a,b,c=I[t:t+3]; u=sub(P[b],P[a]); v=sub(P[c],P[a])
        f=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
        for q in (a,b,c):
            for i in range(3):N[q][i]+=f[i]
    cy=sum(p[1] for p in P)/len(P)
    if sum(N[i][0]*P[i][0]+N[i][1]*(P[i][1]-cy)+N[i][2]*P[i][2] for i in range(len(P)))<0:
        I=[I[t+j] for t in range(0,len(I),3) for j in (0,2,1)]
        N=[[-x for x in n_] for n_ in N]
    for n_ in N:
        l=math.sqrt(sum(x*x for x in n_)) or 1
        for i in range(3):n_[i]/=l
    return P,N,UV,I
def glb(nome, comida, escala=1.0, alt=1.0):
    prato=[(0,.012),(.09,.012),(.13,.028),(.13,.024),(.085,0),(0,0)]
    mont=[(0,.012+.04*alt),(.035*escala,.012+.036*alt),(.06*escala,.012+.024*alt),(.078*escala,.012),(0,.012)]
    buf=b'';views=[];acc=[];prims=[]
    def add(data,target):
        nonlocal buf
        data+=b'\0'*((4-len(data)%4)%4)
        views.append({"buffer":0,"byteOffset":len(buf),"byteLength":len(data),"target":target}); buf+=data
        return len(views)-1
    for m,prof in enumerate([prato,mont]):
        P,N,UV,I=lathe(prof)
        flat=[c for p in P for c in p]
        xs,ys,zs=flat[0::3],flat[1::3],flat[2::3]
        vp=add(struct.pack(f'{len(flat)}f',*flat),34962)
        vn=add(struct.pack(f'{len(P)*3}f',*[c for n in N for c in n]),34962)
        vu=add(struct.pack(f'{len(UV)*2}f',*[c for u in UV for c in u]),34962)
        vi=add(struct.pack(f'{len(I)}H',*I),34963)
        base=len(acc)
        acc+=[{"bufferView":vp,"componentType":5126,"count":len(P),"type":"VEC3","min":[min(xs),min(ys),min(zs)],"max":[max(xs),max(ys),max(zs)]},
              {"bufferView":vn,"componentType":5126,"count":len(P),"type":"VEC3"},
              {"bufferView":vu,"componentType":5126,"count":len(P),"type":"VEC2"},
              {"bufferView":vi,"componentType":5123,"count":len(I),"type":"SCALAR"}]
        prims.append({"attributes":{"POSITION":base,"NORMAL":base+1,"TEXCOORD_0":base+2},"indices":base+3,"material":m})
    mats=[{"name":"ceramica","pbrMetallicRoughness":{"baseColorFactor":[.96,.96,.94,1],"metallicFactor":0,"roughnessFactor":.3}},
          {"name":"comida","pbrMetallicRoughness":{"baseColorFactor":comida+[1],"metallicFactor":0,"roughnessFactor":.8}}]
    j=json.dumps({"asset":{"version":"2.0"},"scene":0,"scenes":[{"nodes":[0]}],"nodes":[{"mesh":0,"name":nome}],
      "meshes":[{"name":nome,"primitives":prims}],"materials":mats,"accessors":acc,"bufferViews":views,"buffers":[{"byteLength":len(buf)}]}).encode()
    j+=b' '*((4-len(j)%4)%4)
    out=struct.pack('<III',0x46546C67,2,28+len(j)+len(buf))+struct.pack('<II',len(j),0x4E4F534A)+j+struct.pack('<II',len(buf),0x004E4942)+buf
    open(f'pratos/{nome}.glb','wb').write(out)
glb('feijoada',[.18,.1,.07],1.0,1.0)
glb('parmegiana',[.85,.45,.15],1.0,.6)
glb('salada',[.25,.55,.2],1.0,1.3)
glb('pudim',[.78,.5,.12],.55,1.4)
