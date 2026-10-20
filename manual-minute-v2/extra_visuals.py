"""Original animated schematics; no manufacturer footage or screenshots."""
import math
from PIL import ImageFont
WHITE='#F4F3EB'; GREEN='#C4F15B'; MUTED='#A8B1BB'; PANEL='#17222D';RED='#FF8C7A'
F='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
from functools import lru_cache
@lru_cache(None)
def font(n):return ImageFont.truetype(F,n)
def text(d,x,y,s,n=32,c=WHITE):d.text((x,y),s,font=font(n),fill=c)
def box(d,xy,c=PANEL,r=24):d.rounded_rectangle(xy,radius=r,fill=c)
def center(d,y,s,n=32,c=WHITE):text(d,(1080-font(n).getlength(s))/2,y,s,n,c)
def path(d,labels,active):
 for i,s in enumerate(labels):
  y=1140+i*83;box(d,(105,y,930,y+68),GREEN if i==active else PANEL,14)
  text(d,135,y+13,s,30,'#0A1017' if i==active else WHITE)

def wipers(d,mode,p):
 # Windshield viewed from outside; both wipers stay against glass.
 d.polygon([(200,560),(838,560),(925,1010),(112,1010)],fill='#183342',outline='#728B99',width=5)
 for k in range(4):d.line((280+k*130,590,220+k*150,970),fill='#234454',width=3)
 angle={'park':.15,'menu':.15,'service':.15+min(1,p*2)*.30,'caution':.45,'off':.45-min(1,p*2)*.30}[mode]
 for x,length in [(260,300),(590,260)]:
  ex=x+math.cos(angle)*length; ey=973-math.sin(angle)*length
  d.line((x,973,ex,ey),fill='#A7BCC5',width=13)
  d.line((ex-90*math.cos(angle),ey+90*math.sin(angle),ex+55*math.cos(angle),ey-55*math.sin(angle)),fill=GREEN,width=17)
 if mode in ['park','menu','service']:path(d,['Park • Wipers off','Controls → Service','Wiper Service Mode'],{'park':0,'menu':1,'service':2}[mode])
 elif mode=='caution':
  box(d,(105,1130,930,1360),'#302420')
  center(d,1164,'The arms do not lock upright.',35,RED)
  center(d,1230,'Never lift past their intended travel.',27)
 else:
  box(d,(105,1165,930,1295));center(d,1200,'Wiper Service Mode → OFF',33,GREEN)

def pin(d,mode,p):
 box(d,(124,560,920,995),PANEL,34)
 d.line((157,790,887,790),fill='#607380',width=4)
 box(d,(424,824,620,845),'#70838E',8)
 center(d,615,'GLOVEBOX',36,MUTED)
 if mode in ['hook','set','prompt']:
  n=4 if mode=='hook' else min(4,int(p*5))
  for i in range(4):
   x=401+i*65;d.ellipse((x-14,717,x+14,745),fill=GREEN if i<n else '#3A4C58')
 elif mode=='separate':
  center(d,700,'GLOVEBOX PIN',42,GREEN)
  center(d,877,'Separate from PIN to Drive',31)
 else:
  center(d,700,'RESET ON THE TOUCHSCREEN',29,GREEN)
 if mode in ['hook','set','prompt']:path(d,['Controls','Safety','Glovebox PIN'],2 if mode!='hook' else 0)
 elif mode=='separate':
  box(d,(105,1140,930,1330));center(d,1180,'Two different protections.',34)
  center(d,1242,'A glovebox PIN does not enable PIN to Drive.',26,MUTED)
 else:
  box(d,(105,1140,930,1330));center(d,1180,'Forgot it?',38)
  center(d,1245,'Follow Tesla’s account-reset prompts.',28,MUTED)

def walkaway(d,mode,p):
 # Schematic top view; no fixed distance or timing is implied.
 box(d,(350,565,680,1080),'#AABAC4',80)
 box(d,(383,650,647,840),'#193A4A',35)
 box(d,(383,890,647,997),'#193A4A',25)
 for x in [325,675]:
  for y in [650,925]:box(d,(x,y,x+30,y+100),'#03080D',7)
 if mode in ['hook','on']:
  x=770+int(110*p);box(d,(x,705,x+96,885),'#233444',22)
  box(d,(x+10,725,x+86,852),GREEN,10)
  for r in [35,65,95]:d.arc((x-r,755-r,x+r,755+r),190,340,fill=GREEN,width=3)
 elif mode=='home':
  d.polygon([(785,730),(865,655),(945,730)],fill=GREEN)
  box(d,(800,730,930,850),'#65823C',5);text(d,813,785,'HOME',25)
 elif mode=='key':
  box(d,(458,735,554,900),'#233444',18);box(d,(468,755,544,867),GREEN,8)
 elif mode=='close':
  d.line((350,850,230,805),fill=RED,width=16)
  d.line((680,850,800,805),fill=RED,width=16)
 if mode in ['hook','on']:path(d,['Controls → Locks','Walk-Away Door Lock','Confirm the vehicle actually locks'],1 if mode=='on' else 2)
 else:
  messages={'home':('Exclude Home checked?','It can stay unlocked at Home.'),'key':('Key detected inside?','Automatic locking can be prevented.'),'close':('Door or trunk open?','Close everything and verify the lock.')}
  title,sub=messages[mode];box(d,(100,1140,936,1360));center(d,1182,title,38,GREEN);center(d,1255,sub,29)
