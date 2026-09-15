"""Reference-projected, genuinely volumetric family meshes. Python standard library only.
Coordinates: metres, +Z up, front -Y. The reference's front lighting is baked in.
Unseen depth/back design is inferred, not recovered from the single image.
"""
from __future__ import annotations
import math

PALETTE = {
 'skin':'EAAF79','skin_dark':'CC8D59','hair':'292B2D','blue':'69B5E1',
 'navy':'263E58','brown':'805029','sole':'D3BE96','white':'E4E6E5',
 'yellow':'E7AB35','teal':'286E70','pink':'DE73A1','skirt':'2D5682',
 'cyan':'218AA5','black':'262A2C','helmet_blue':'218AD2','stripe':'F2F0E6',
 'helmet_pink':'E985B2','gold':'DDA345',
}
KEYS=list(PALETTE)
TAU=math.tau

def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def unit(a):
 n=math.sqrt(dot(a,a))
 return tuple(x/max(n,1e-12) for x in a)

# All profile positions are measured against a 1408 x 1056 working copy.
# A vertical row is [source_y, source_left, source_right, depth_in_pixels].
# A horizontal row is [source_x, source_top, source_bottom, depth_in_pixels].
# Original attached image is retained separately in the downloadable package.
SPECS = {
 'father':dict(height=1.75,top=164,bottom=883,cx=279,offset=-1.16,
  skin='skin',shirt='blue',pants='navy',shoe='brown',helmet='helmet_blue',
  head=[[215,244,319,45],[225,229,335,52],[245,221,340,54],[264,221,338,55],[279,225,335,55],[299,235,327,49],[315,251,310,38],[329,274,286,11]],
  nose=[286,276,13,21,11],
  helmet_rows=[[164,277,290,2],[170,258,307,24],[183,235,327,44],[199,219,339,61],[220,207,350,72],[237,201,354,77],[247,206,350,73],[255,212,342,65]],
  torso=[[334,253,301,22],[348,239,316,32],[355,213,344,35],[384,209,345,38],[414,214,342,37],[472,222,335,33],[518,210,344,35],[526,231,324,31]],
  neck=[[321,262,298,21],[350,262,298,23],[365,274,289,15]],
  pelvis=[[523,218,339,34],[543,216,341,37],[565,214,343,40],[584,215,341,39]],
  legs=[[[561,215,273,31],[600,212,272,33],[690,211,266,27],[760,207,257,24],[837,206,253,22],[842,213,246,20]],[[560,288,343,31],[600,289,344,33],[690,294,345,27],[759,298,345,24],[837,302,348,22],[842,310,342,20]]],
  shoes=[[[838,213,247,22],[848,203,250,34],[864,195,254,42],[879,193,254,43],[883,196,250,42]],[[838,308,342,22],[848,306,350,34],[864,303,361,42],[879,302,363,43],[883,307,360,42]]],
  sleeves=[[[147,355,407,23],[170,355,412,27],[209,354,419,29],[218,362,416,28]],[[338,357,417,27],[372,355,413,27],[410,355,406,23]]],
  arms=[[[59,368,386,10],[99,363,394,15],[147,362,398,17]],[[410,362,398,17],[464,365,392,14],[508,370,384,9]]],
  hands=[[[20,372,378,3],[26,370,381,6],[42,367,386,9],[55,369,386,10],[67,370,384,9]],[[500,370,384,8],[514,367,387,10],[529,370,383,8],[548,373,379,3]]],
  ears=[(217,279,11,19),(339,278,10,18)],
  joints=dict(hips=555,spine=470,chest=381,neck=345,head=327,head_end=223,shoulders=[217,341],elbows=[139,426],wrists=[64,507],hands=[24,542],arm_y=378,thighs=[245,316],knees=[237,321],ankles=[227,326],hip_y=570,knee_y=708,ankle_y=837,toe_y=869)),
 'daughter':dict(height=1.10,top=429,bottom=883,cx=594,offset=-.385,
  skin='skin',shirt='white',pants='skirt',shoe='black',helmet='helmet_pink',
  head=[[465,554,628,28],[478,542,642,37],[495,537,647,44],[513,538,646,45],[529,546,639,42],[543,562,624,33],[557,585,602,12]],
  nose=[596,514,9,13,7],
  helmet_rows=[[429,584,606,3],[436,560,630,28],[451,542,645,44],[471,531,655,55],[489,525,661,60],[502,531,654,53]],
  torso=[[565,572,615,16],[576,555,633,23],[594,551,638,27],[624,552,637,27],[652,549,642,26],[672,547,642,27],[677,558,629,24]],
  neck=[[548,578,607,16],[570,578,607,18],[588,590,597,5]],
  legs=[[[744,554,584,18],[774,553,583,18],[800,553,579,16],[839,552,578,14],[852,551,578,14]],[[744,608,638,18],[774,609,638,18],[800,612,638,16],[839,613,638,14],[852,613,638,14]]],
  shoes=[[[848,552,577,15],[855,546,581,21],[870,542,583,26],[883,541,583,27]],[[848,614,638,15],[855,610,643,21],[870,609,649,26],[883,609,649,27]]],
  sleeves=[[[527,573,609,15],[548,572,610,17],[561,575,607,17]],[[627,575,607,17],[643,573,610,17],[664,575,607,15]]],
  arms=[[[470,583,598,8],[500,579,601,11],[528,579,603,12]],[[663,580,603,12],[693,582,600,10],[722,585,598,8]]],
  hands=[[[439,585,592,3],[453,582,595,6],[470,581,599,8],[481,584,598,8]],[[714,585,597,7],[731,582,599,8],[744,585,595,6],[754,586,593,3]]],
  ears=[(540,520,10,15),(646,520,10,15)],
  pigtails=[[[534,534,549,9],[548,524,553,17],[568,518,553,19],[575,523,550,16]],[[534,639,652,9],[549,638,662,17],[568,636,669,19],[575,638,665,16]]],
  skirt=[[676,556,633,28],[699,549,641,34],[721,539,651,41],[745,529,660,45],[754,561,633,42]],
  bag=[[564,563,625,22],[578,542,649,32],[655,536,655,32],[677,545,646,24]],
  straps=[[[569,559,572,5],[603,554,566,5],[650,543,555,5],[674,539,551,5]],[[569,619,632,5],[603,625,639,5],[650,637,649,5],[674,640,652,5]]],
  joints=dict(hips=678,spine=632,chest=590,neck=571,head=555,head_end=475,shoulders=[547,643],elbows=[503,690],wrists=[472,722],hands=[443,750],arm_y=590,thighs=[568,623],knees=[568,623],ankles=[565,627],hip_y=694,knee_y=780,ankle_y=848,toe_y=874)),
 'mother':dict(height=1.62,top=210,bottom=883,cx=908,offset=.385,
  skin='skin',shirt='yellow',pants='teal',shoe='brown',
  head=[[241,899,933,25],[259,874,953,42],[283,850,963,53],[302,847,963,54],[324,858,953,48],[342,879,937,33],[356,900,918,12]],
  nose=[910,309,10,20,10],
  hair=[[210,898,912,3],[218,876,933,26],[234,856,957,43],[253,843,965,56],[277,837,971,63],[299,836,973,64]],
  hair_tails=[[[294,846,876,19],[328,846,887,27],[349,853,890,25],[365,870,891,15]],[[292,937,963,19],[327,931,965,27],[349,932,964,25],[369,936,951,15]]],
  torso=[[368,883,934,22],[380,868,951,29],[386,851,962,35],[429,851,962,40],[465,867,949,34],[499,872,946,30],[548,839,977,41],[560,875,947,32]],
  neck=[[344,895,926,20],[379,891,925,21],[396,903,916,15]],
  pelvis=[[548,844,972,38],[574,840,975,39],[592,838,977,41]],
  legs=[[[578,842,904,32],[602,839,902,33],[681,838,892,28],[755,840,887,24],[837,841,882,23],[842,848,878,19]],[[578,912,974,32],[602,914,977,33],[680,921,975,28],[755,927,974,24],[837,932,971,23],[842,938,966,19]]],
  shoes=[[[840,847,879,19],[852,843,882,27],[865,837,881,36],[879,836,881,39],[883,838,880,38]],[[840,938,966,19],[852,934,970,27],[865,932,975,36],[879,931,975,39],[883,933,974,38]]],
  sleeves=[[[798,386,429,19],[826,383,435,25],[855,385,435,27]],[[959,385,435,27],[989,385,434,25],[1015,388,429,19]]],
  arms=[[[697,402,418,9],[748,397,423,13],[798,395,425,15]],[[1015,395,425,15],[1064,399,422,13],[1111,405,419,8]]],
  hands=[[[672,406,413,3],[684,401,419,7],[698,402,420,9],[711,405,418,8]],[[1104,405,419,7],[1123,401,421,9],[1137,405,417,6],[1148,407,414,3]]],
  ears=[(846,312,11,18),(961,312,12,18)],
  joints=dict(hips=570,spine=484,chest=407,neck=375,head=352,head_end=259,shoulders=[853,962],elbows=[779,1038],wrists=[698,1115],hands=[678,1143],arm_y=412,thighs=[873,943],knees=[865,947],ankles=[862,951],hip_y=585,knee_y=711,ankle_y=840,toe_y=869)),
 'son':dict(height=1.05,top=444,bottom=883,cx=1222,offset=1.16,
  skin='skin',shirt='white',pants='navy',shoe='cyan',
  head=[[469,1189,1251,26],[487,1176,1267,37],[508,1165,1276,44],[530,1168,1275,43],[548,1185,1261,35],[563,1208,1235,18],[568,1219,1227,6]],
  nose=[1225,533,9,13,6],
  hair=[[444,1210,1238,3],[451,1189,1259,24],[466,1170,1277,40],[485,1160,1283,50],[508,1163,1280,51],[520,1173,1270,43]],
  torso=[[574,1203,1245,17],[583,1183,1263,24],[607,1175,1270,28],[649,1178,1266,28],[680,1174,1269,27],[688,1184,1258,25]],
  neck=[[558,1209,1237,14],[580,1207,1239,16],[592,1220,1228,6]],
  pelvis=[[687,1181,1263,28],[707,1176,1269,30],[722,1174,1271,30]],
  shorts=[[[705,1181,1215,21],[732,1174,1215,23],[751,1170,1213,22],[756,1177,1210,20]],[[705,1227,1262,21],[733,1227,1270,23],[752,1231,1275,22],[756,1236,1270,20]]],
  legs=[[[750,1180,1210,16],[778,1181,1210,17],[807,1177,1208,15],[839,1175,1207,14],[850,1175,1207,13]],[[750,1238,1268,16],[778,1238,1268,17],[807,1240,1270,15],[839,1242,1270,14],[850,1242,1270,13]]],
  shoes=[[[846,1178,1207,13],[858,1169,1210,21],[872,1163,1210,27],[883,1163,1209,27]],[[846,1244,1269,13],[858,1240,1275,21],[872,1240,1281,27],[883,1241,1281,27]]],
  sleeves=[[[1147,589,622,14],[1170,588,626,18],[1189,584,621,18]],[[1256,585,621,18],[1278,590,625,18],[1295,592,621,14]]],
  arms=[[[1090,596,610,8],[1118,592,614,10],[1148,592,616,12]],[[1295,592,616,12],[1326,595,613,10],[1356,598,610,8]]],
  hands=[[[1058,598,605,3],[1071,595,611,7],[1088,595,613,8],[1101,598,611,8]],[[1347,598,610,7],[1363,595,613,8],[1376,598,609,6],[1383,600,606,3]]],
  ears=[(1165,533,11,16),(1278,532,10,15)],
  bag=[[573,1198,1247,20],[585,1172,1276,27],[667,1166,1276,28],[689,1178,1265,23]],
  straps=[[[577,1183,1196,4],[612,1180,1192,4],[658,1169,1183,4],[688,1167,1179,4]],[[577,1250,1262,4],[612,1257,1269,4],[658,1265,1277,4],[688,1267,1279,4]]],
  joints=dict(hips=703,spine=648,chest=604,neck=581,head=565,head_end=485,shoulders=[1181,1264],elbows=[1127,1318],wrists=[1092,1355],hands=[1064,1378],arm_y=603,thighs=[1198,1248],knees=[1197,1253],ankles=[1192,1256],hip_y=717,knee_y=789,ankle_y=847,toe_y=873)),
}

class Character:
 def __init__(self,name):
  self.name=name;self.spec=SPECS[name];self.scale=self.spec['height']/(self.spec['bottom']-self.spec['top'])
  self.parts=[];self.joints=[];self.joint_ids={};self.skeleton()
 def xyz(self,x,y,d=0): return ((x-self.spec['cx'])*self.scale,d*self.scale,(self.spec['bottom']-y)*self.scale)
 def skeleton(self):
  j=self.spec['joints'];cx=self.spec['cx']
  def add(n,x,y,parent=None,d=0):
   self.joint_ids[n]=len(self.joints)
   self.joints.append(dict(name=n,position=self.xyz(x,y,d),parent=self.joint_ids[parent] if parent else None))
  add('root',cx,self.spec['bottom'])
  add('hips',cx,j['hips'],'root');add('spine',cx,j['spine'],'hips');add('chest',cx,j['chest'],'spine')
  add('neck',cx,j['neck'],'chest');add('head',cx,j['head'],'neck');add('head_end',cx,j['head_end'],'head')
  for k,side in enumerate(('R','L')):
   add('upper_arm.'+side,j['shoulders'][k],j['arm_y'],'chest')
   add('forearm.'+side,j['elbows'][k],j['arm_y'],'upper_arm.'+side)
   add('hand.'+side,j['wrists'][k],j['arm_y'],'forearm.'+side)
   add('fingers.'+side,j['hands'][k],j['arm_y'],'hand.'+side)
   add('thigh.'+side,j['thighs'][k],j['hip_y'],'hips')
   add('shin.'+side,j['knees'][k],j['knee_y'],'thigh.'+side)
   add('foot.'+side,j['ankles'][k],j['ankle_y'],'shin.'+side)
   add('toe.'+side,j['ankles'][k],j['toe_y'],'foot.'+side,d=-26)
 def weights(self,bone,x,y):
  if bone=='torso':
   j=self.spec['joints'];t=max(0,min(1,(j['hips']-y)/(j['hips']-j['chest'])))
   if t<.5:return [('hips',1-2*t),('spine',2*t)]
   return [('spine',2-2*t),('chest',2*t-1)]
  if bone.startswith('leg.'):
   side=bone[-1];ky=self.spec['joints']['knee_y'];t=max(0,min(1,(y-ky+13)/26))
   return [('thigh.'+side,1-t),('shin.'+side,t)]
  if bone.startswith('arm.'):
   side=bone[-1];k=0 if side=='R' else 1;el=self.spec['joints']['elbows'][k]
   t=max(0,min(1,((el-x) if k==0 else (x-el))/20+.5))
   return [('upper_arm.'+side,1-t),('forearm.'+side,t)]
  return [(bone,1.)]
 def loft(self,name,rows,color,bone,axis='z',cy=0,n=16,power=1,project=True,nose=None,color_fn=None):
  rows=[list(r) for r in rows];verts=[];pixels=[];centers=[]
  for row in rows:
   a,lo,hi,dep=row;mid=(lo+hi)/2;half=(hi-lo)/2
   center=self.xyz(mid,a,cy) if axis=='z' else self.xyz(a,mid,cy)
   centers.append(center)
   for k in range(n):
    t=TAU*k/n;co=math.cos(t);si=math.sin(t)
    xx=math.copysign(abs(co)**power,co);dd=math.copysign(abs(si)**power,si)
    if axis=='z': x,y=mid+half*xx,a;depth=cy+dep*dd
    else:x,y=a,mid+half*xx;depth=cy+dep*dd
    if nose and si<0:
     nx,ny,wx,wy,amount=nose
     depth-=amount*math.exp(-((x-nx)/wx)**2-((y-ny)/wy)**2)*max(0,-si)**4
    verts.append(self.xyz(x,y,depth));pixels.append((x,y));
  faces=[]
  for i in range(len(rows)-1):
   for k in range(n):
    a=i*n+k;b=i*n+(k+1)%n;c=(i+1)*n+(k+1)%n;d=(i+1)*n+k
    faces.extend([(a,b,c),(a,c,d)])
  for i in (0,len(rows)-1):
   idx=len(verts);verts.append(centers[i]);a,lo,hi,_=rows[i]
   pixels.append(((lo+hi)/2,a) if axis=='z' else (a,(lo+hi)/2))
   for k in range(n):faces.append((idx,i*n+k,i*n+(k+1)%n))
  out=[]
  for f in faces:
   ps=[verts[k] for k in f];cen=tuple(sum(v[a] for v in ps)/3 for a in range(3))
   normal=unit(cross(sub(ps[1],ps[0]),sub(ps[2],ps[0])))
   if f[0]>=len(rows)*n:
    along=2 if axis=='z' else 0
    direction=1 if (f[0]==len(rows)*n)==(axis=='z') else -1
    expected=tuple(direction if q==along else 0 for q in range(3))
   else:
    ri=min(len(rows)-2,min(f)//n)
    ctr=tuple((centers[ri][a]+centers[ri+1][a])/2 for a in range(3))
    expected=sub(cen,ctr)
   if dot(normal,expected)<0:f=(f[0],f[2],f[1]);normal=tuple(-x for x in normal)
   area=math.sqrt(dot(cross(sub(ps[1],ps[0]),sub(ps[2],ps[0])),cross(sub(ps[1],ps[0]),sub(ps[2],ps[0]))))
   if area<1e-12:continue
   isfront=project and cen[1]<cy*self.scale-1e-8
   yc=(rows[min(len(rows)-2,min(f)//n)][0]+rows[min(len(rows)-2,min(f)//n)+1][0])/2 if axis=='z' and f[0]<len(rows)*n else sum(pixels[k][1] for k in f)/3
   co=color_fn(yc,cen) if color_fn else color
   shade=1. if isfront else .80+.20*max(0,dot(normal,unit((-.35,-.5,.8))))
   out.append((f,normal,isfront,co,shade))
  self.parts.append(dict(name=name,vertices=verts,pixels=pixels,faces=out,bone=bone))
 def helmet_stripe(self,rows):
  vs=[];pix=[];faces=[]
  for y,lo,hi,depth in rows:
   cx=(lo+hi)/2;w=min(4,(hi-lo)*.28);radius=(hi-lo)/2
   d=1+depth*math.sqrt(max(0,1-(w/max(radius,1))**2))+1.2
   for x in (cx-w,cx+w):vs.append(self.xyz(x,y,d));pix.append((x,y))
  for i in range(len(rows)-1):
   for f in [(2*i,2*i+2,2*i+3),(2*i,2*i+3,2*i+1)]:
    n=unit(cross(sub(vs[f[1]],vs[f[0]]),sub(vs[f[2]],vs[f[0]])))
    if n[1]<0:f=(f[0],f[2],f[1]);n=tuple(-a for a in n)
    faces.append((f,n,False,'stripe',.95))
  self.parts.append(dict(name='Helmet_Rear_Stripe',vertices=vs,pixels=pix,faces=faces,bone='head'))
 def ear(self,x,y,rx,ry):
  rows=[]
  for t in [0,.15,.4,.65,.85,1]:
   half=max(.8,rx*math.sqrt(max(0,1-(2*t-1)**2)))
   rows.append([y+(2*t-1)*ry,x-half,x+half,max(1,half*.66)])
  self.loft('Ear_R' if x<self.spec['cx'] else 'Ear_L',rows,'skin','head',cy=-3,n=12)
 def build(self):
  s=self.spec
  # Backpacks are real solids behind the torso; front straps are separate meshes.
  if 'bag' in s:
   bc='pink' if self.name=='daughter' else 'cyan'
   self.loft('Backpack',s['bag'],bc,'chest',cy=40,n=16,power=.65,project=False)
   mid=s['cx'];y0=s['bag'][1][0]+35;y1=s['bag'][-1][0]-8
   self.loft('Backpack_Rear_Pocket',[[y0,mid-30,mid+30,3],[y0+6,mid-37,mid+37,7],[y1-5,mid-36,mid+36,7],[y1,mid-30,mid+30,3]],bc,'chest',cy=71,n=12,power=.65,project=False)
  if 'hair_tails' in s:
   for k,r in enumerate(s['hair_tails']):self.loft('Hair_Bob_'+str(k),r,'hair','head',cy=16,n=12)
  if 'pigtails' in s:
   for k,r in enumerate(s['pigtails']):self.loft('Hair_Pigtail_'+str(k),r,'hair','head',cy=14,n=12)
  self.loft('Neck',s['neck'],'skin','neck',cy=0,n=16)
  self.loft('Shirt',s['torso'],s['shirt'],'torso',n=20,power=.72)
  if 'pelvis' in s:self.loft('Pelvis',s['pelvis'],s['pants'],'hips',n=16,power=.7,color_fn=(lambda y,c:'black' if y<544 else 'navy') if self.name=='father' else None)
  for k,r in enumerate(s['legs']):
   if self.name in ('daughter','son'):
    r=[list(a) for a in r]
    for i in range(len(r)-1):
     if r[i][0]<819<r[i+1][0]:
      t=(819-r[i][0])/(r[i+1][0]-r[i][0]);r.insert(i+1,[819]+[r[i][j]+t*(r[i+1][j]-r[i][j]) for j in range(1,4)]);break
   side='R' if k==0 else 'L'
   color=s['pants'] if self.name in ('father','mother') else 'skin'
   fn=(lambda y,c:'white' if y>819 else 'skin') if self.name in ('daughter','son') else None
   self.loft('Leg_'+side,r,color,'leg.'+side,n=16,power=.82,color_fn=fn)
  if 'shorts' in s:
   for k,r in enumerate(s['shorts']):self.loft('Shorts_'+str(k),r,s['pants'],'thigh.'+('R' if k==0 else 'L'),n=16,power=.78)
  if 'skirt' in s:self.loft('Skirt',s['skirt'],'skirt','hips',n=24,power=.85)
  for k,r in enumerate(s['shoes']):
   side='R' if k==0 else 'L'
   self.loft('Shoe_'+side,r,s['shoe'],'foot.'+side,cy=-13,n=16,power=.66,color_fn=lambda y,c:'sole' if y>877 else s['shoe'])
  for group,key,color,bone in [('Sleeve','sleeves',s['shirt'],'arm.'),('Arm','arms','skin','arm.'),('Hand','hands','skin','hand.')]:
   for k,r in enumerate(s[key]):self.loft(group+('_R' if k==0 else '_L'),r,color,bone+('R' if k==0 else 'L'),axis='x',n=16,power=.85)
  for k,r in enumerate(s.get('straps',[])):
   self.loft('Backpack_Strap_'+str(k),r,'pink' if self.name=='daughter' else 'cyan','chest',cy=-31,n=10,power=.6)
  for e in s['ears']:self.ear(*e)
  hairline=dict(father=296,daughter=537,mother=347,son=538)[self.name]
  self.loft('Head',s['head'],'skin','head',n=32,nose=s['nose'],color_fn=lambda y,c:'hair' if y<hairline else 'skin')
  if 'hair' in s:self.loft('Hair_Crown',s['hair'],'hair','head',cy=6,n=20)
  if 'helmet_rows' in s:
   self.loft('Helmet',s['helmet_rows'],s['helmet'],'head',cy=1,n=24,power=1,
             color_fn=None)
   self.helmet_stripe(s['helmet_rows'])
  return self

def build_family(names=None):
 return [Character(n).build() for n in (names or SPECS)]
