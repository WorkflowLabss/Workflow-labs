"""Original motion graphics for manufacturer-source vehicle tips. No publishing."""
import argparse, asyncio, hashlib, json, math, os, ssl, subprocess, wave, time, uuid
from datetime import date
from urllib.parse import urlparse
from pathlib import Path
from functools import lru_cache
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
W,H,FPS=1080,1920,30
VOICE_LIMIT=asyncio.Semaphore(2)
from extra_visuals import wipers, pin, walkaway
def digest(topic):
 return hashlib.sha256(json.dumps(topic,sort_keys=True).encode()+Path(__file__).read_bytes()+(ROOT/'extra_visuals.py').read_bytes()).hexdigest()
def filehash(path):return hashlib.sha256(path.read_bytes()).hexdigest()
INK='#0A1017'; WHITE='#F4F3EB'; MUTED='#A8B1BB'; GREEN='#C4F15B'; RED='#FF8C7A'; PANEL='#17222D'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
@lru_cache(None)
def font(n,b=True): return ImageFont.truetype(BOLD if b else FONT,n)
def run(a): subprocess.run(a,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,timeout=600)
def probe(p): return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(p)]))
def ease(v): v=max(0,min(1,v)); return 1-(1-v)**3
def txt(d,xy,s,n=40,c=WHITE,b=True): d.text(xy,s,font=font(n,b),fill=c)
def center(d,y,s,n=40,c=WHITE,b=True): txt(d,((W-font(n,b).getlength(s))/2,y),s,n,c,b)
def box(d,coords,fill=PANEL,r=28,outline=None,width=2): d.rounded_rectangle(tuple(map(int,coords)),radius=r,fill=fill,outline=outline,width=width)
def wrap(s,n,width):
 lines=[]
 for word in s.split():
  if lines and font(n).getlength(lines[-1]+' '+word)<width: lines[-1]+=' '+word
  else: lines.append(word)
 return lines

def base(topic,t,total,scene):
 im=Image.new('RGB',(W,H),INK); d=ImageDraw.Draw(im)
 # Quiet technical grid anchors the original illustrations.
 for x in range(60,W,80):
  for y in range(370,1370,80): d.ellipse((x,y,x+2,y+2),fill='#24303B')
 box(d,(66,92,120,146),GREEN,12); txt(d,(76,101),'M',29,INK)
 txt(d,(142,100),'MANUAL MINUTE',28)
 txt(d,(66,185),topic['label'],25,MUTED)
 txt(d,(66,233),scene['eyebrow'].upper(),24,GREEN)
 for i,line in enumerate(scene['headline'].split('|')): txt(d,(62,285+i*86),line,72)
 box(d,(66,1642,933,1650),'#2D3843',4)
 box(d,(66,1642,66+max(2,867*t/total),1650),GREEN,4)
 txt(d,(66,1685),'ILLUSTRATED GUIDE',22,MUTED)
 txt(d,(66,1724),'Match your vehicle • Try while parked',23,MUTED,False)
 return im,d

def pointer(d,x,y,t):
 r=22+int(20*(t%1)); d.ellipse((x-r,y-r,x+r,y+r),outline=GREEN,width=3)
 d.ellipse((x-9,y-9,x+9,y+9),fill=GREEN)

def screen(d,mode,p):
 box(d,(84,550,952,1140),'#020609',34, '#56626F',3)
 if mode in ['clean','exit']:
  center(d,695,'SCREEN CLEAN MODE',37)
  center(d,759,'Touch controls are inactive',28,MUTED,False)
  box(d,(310,936,730,1024),'#1E2A34',18)
  if mode=='exit': box(d,(310,936,310+max(3,int(420*ease(p))),1024),GREEN,18)
  center(d,961,'HOLD TO EXIT',29,INK if mode=='exit' and ease(p)>.45 else WHITE)
  if mode=='clean':
   x=165+int(560*(.5+.5*math.sin(p*math.pi*2)))
   box(d,(x,820,x+120,910),'#8CA4B5',18)
   for k in range(4): d.line((x+20,835+k*17,x+100,835+k*17),fill='#B9C7D0',width=2)
 else:
  box(d,(106,575,370,1114),'#111D28',20)
  for i,s in enumerate(['Controls','Display','Lights','Locks']):
   y=624+i*90
   if s==('Controls' if mode=='controls' else 'Display'): box(d,(120,y-8,355,y+58),GREEN,12)
   txt(d,(139,y),s,29,INK if s==('Controls' if mode=='controls' else 'Display') else MUTED)
  txt(d,(415,610),'Display',39)
  txt(d,(415,695),'Brightness',28,MUTED,False)
  box(d,(415,757,883,768),'#41505C',5); d.ellipse((715,744,751,780),fill=WHITE)
  box(d,(412,876,904,980),GREEN if mode=='mode' else '#293843',18)
  txt(d,(440,909),'Screen Clean Mode',32,INK if mode=='mode' else WHITE)
  if mode=='controls': pointer(d,331,651,p*3)
  elif mode=='display': pointer(d,331,741,p*3)
  else: pointer(d,859,929,p*3)
 center(d,1196,'Simplified menu • Layout varies by software',23,MUTED,False)

def usb(d,mode,p):
 # Original schematic: charge path and data path are deliberately distinct.
 if mode=='date':
  box(d,(84,575,952,1100),PANEL,35)
  txt(d,(126,627),'BUILD DATE MATTERS',31,MUTED)
  txt(d,(126,712),'NOV 2021',82,GREEN)
  for i in range(6):
   x=132+i*125; box(d,(x,866,x+76,947),'#293B47',12)
  center(d,1011,'Some later builds: charging only',32)
 else:
  x1,x2=118,926
  for i,(label,value,c) in enumerate([('CENTER CONSOLE','POWER',GREEN),('GLOVEBOX','DATA',GREEN)]):
   y=580+i*270; box(d,(x1,y,x2,y+231),PANEL,28)
   txt(d,(x1+34,y+25),label,29,MUTED)
   box(d,(x1+38,y+101,x1+178,y+161),'#060D14',25 if i==0 else 4,'#718491',3)
   d.line((x1+62,y+132,x1+151,y+132),fill=MUTED,width=5)
   if i==1:
    for pin in range(4): d.rectangle((x1+66+pin*22,y+111,x1+74+pin*22,y+118),fill=GREEN)
   d.line((x1+198,y+131,x1+470,y+131),fill='#40524A',width=4)
   for k in range(4):
    x=x1+210+int(((p*.8+k*.25)%1)*244)
    d.ellipse((x,y+124,x+13,y+137),fill=GREEN)
   txt(d,(x1+517,y+105),value,36,GREEN)
  center(d,1165,'Power does not guarantee data support.',31)
  center(d,1225,'Port locations shown schematically',23,MUTED,False)
 if mode=='rear':
  box(d,(110,1280,926,1370),'#302420',20)
  center(d,1306,'Rear-console ports: charging only',29,RED)

def truck(d,mode,p):
 # Unbranded, schematic pickup body with animated glass lowering.
 x,y=103,651
 d.polygon([(x,y+210),(x+55,y+105),(x+210,y+90),(x+295,y),(x+544,y),(x+620,y+95),(x+810,y+105),(x+828,y+267),(x,y+267)],fill='#B5C0C9')
 for wx in [x+160,x+676]:
  d.ellipse((wx-73,y+194,wx+73,y+340),fill='#05090E',outline='#566774',width=5)
  d.ellipse((wx-36,y+231,wx+36,y+303),fill='#5C6B78')
 opening=ease(p) if mode=='open' else (1 if mode=='stop' else 0)
 for a,b in [(x+293,x+395),(x+414,x+536)]:
  box(d,(a,y+23,b,y+97),'#101A24',7)
  if opening<.98: box(d,(a,y+23+int(74*opening),b,y+97),'#66ACC0',4)
 d.line((x+400,y+15,x+400,y+252),fill='#667580',width=3)
 box(d,(394,1050,666,1370),'#080D12',64,'#7E8C98',5)
 box(d,(430,1095,630,1180),GREEN if mode in ['tap','hold','open'] else '#27333F',20)
 txt(d,(452,1124),'UNLOCK',30,INK if mode in ['tap','hold','open'] else WHITE)
 box(d,(430,1212,630,1298),'#27333F',20); txt(d,(478,1240),'LOCK',30)
 if mode in ['tap','hold']: pointer(d,615,1140,p*3)
 label={'tap':'1  TAP + RELEASE','hold':'2  HOLD WITHIN 1 SECOND','open':'3  RELEASE AS WINDOWS MOVE','stop':'LOCK OR UNLOCK = STOP','hook':'GLOBAL OPENING • IF EQUIPPED'}[mode]
 center(d,1430,label,29,GREEN)

def captions(d,words,t):
 if not words: return
 if t<words[0]['start'] or t>words[-1]['end']+.2:return
 active=max(i for i,w in enumerate(words) if w['start']<=t)
 # Four-word phrases retain context without presenting paragraph slides.
 first=(active//4)*4; group=words[first:first+4]; line=' '.join(w['text'] for w in group)
 n=45
 while font(n).getlength(line)>820:n-=1
 x=(W-font(n).getlength(line))/2
 box(d,(x-24,1520,x+font(n).getlength(line)+24,1604),'#03080D',16)
 for j,w in enumerate(group):
  txt(d,(x,1540),w['text'],n,GREEN if first+j==active else WHITE)
  x+=font(n).getlength(w['text']+' ')

def valid_speech(audio,timing):
 try:
  words=[json.loads(x) for x in timing.read_text().splitlines()]
  last=max((x['offset']+x['duration'])/1e7 for x in words if x['type']=='WordBoundary')
  return float(probe(audio)['format']['duration'])>=last-.05
 except Exception:return False

async def speech(text,out):
 async with VOICE_LIMIT:
  return await speech_request(text,out)

async def speech_request(text,out):
 import edge_tts,edge_tts.communicate as comm
 # Honor the runtime's trusted CA bundle; TLS verification stays enabled.
 if os.environ.get('SSL_CERT_FILE'): comm._SSL_CTX=ssl.create_default_context()
 key=hashlib.sha256((text+'Andrew+4').encode()).hexdigest()[:16]
 audio=out/(key+'.mp3'); timing=out/(key+'.jsonl')
 if not valid_speech(audio,timing):
  for attempt in range(4):
   try:
    t=edge_tts.Communicate(text,voice='en-US-AndrewMultilingualNeural',rate='+4%',boundary='WordBoundary',receive_timeout=20)
    tag=uuid.uuid4().hex
    temp_audio=out/(key+'.'+tag+'.part.mp3');temp_timing=out/(key+'.'+tag+'.part.jsonl')
    try:
     await t.save(str(temp_audio),str(temp_timing))
     if not valid_speech(temp_audio,temp_timing):raise RuntimeError('Voice stream was truncated; retrying')
     os.replace(temp_audio,audio);os.replace(temp_timing,timing)
    finally:
     temp_audio.unlink(missing_ok=True);temp_timing.unlink(missing_ok=True)
    break
   except Exception:
    audio.unlink(missing_ok=True); timing.unlink(missing_ok=True)
    if attempt==3: raise
    await asyncio.sleep(1+attempt)
 words=[]
 for l in timing.read_text().splitlines():
  w=json.loads(l)
  if w['type']=='WordBoundary': words.append({'start':w['offset']/1e7,'end':(w['offset']+w['duration'])/1e7,'text':w['text']})
 if not words: raise RuntimeError('Narration contains no word timing')
 return audio,words

def srtstamp(t):
 ms=round(t*1000); return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
async def build(topic,output):
 out=output/topic['key']; out.mkdir(parents=True,exist_ok=True)
 started=time.monotonic()
 allwords=[]; timeline=[]; cursor=0; pcm=[]
 voices=await asyncio.gather(*(speech(s['voice'],out) for s in topic['scenes']))
 for i,s in enumerate(topic['scenes']):
  audio,words=voices[i]
  wav=out/f'scene-{i}.wav'
  run(['ffmpeg','-y','-v','error','-i',str(audio),'-ar','48000','-ac','1',str(wav)])
  with wave.open(str(wav)) as f: data=f.readframes(f.getnframes())
  duration=len(data)/2/48000+.16
  duration=math.ceil(duration*FPS)/FPS
  samples=round(duration*48000); a=np.frombuffer(data,dtype='<i2').copy()
  a=np.pad(a,(0,samples-len(a)))
  # Small original tonal cue at each transition, under the narrator.
  k=np.arange(4800); cue=(np.sin(2*np.pi*(640+100*i)*k/48000)*np.exp(-k/850)*170).astype(np.int16)
  a[:len(cue)]=np.clip(a[:len(cue)].astype(np.int32)+cue,-32768,32767)
  pcm.append(a); timeline.append({'start':cursor,'end':cursor+duration,**s})
  allwords.extend({**w,'start':w['start']+cursor,'end':w['end']+cursor} for w in words); cursor+=duration
 with wave.open(str(out/'narration.wav'),'wb') as f:
  f.setnchannels(1);f.setsampwidth(2);f.setframerate(48000);f.writeframes(np.concatenate(pcm).astype('<i2').tobytes())
 (out/'timeline.json').write_text(json.dumps(timeline,indent=2))
 (out/'words.json').write_text(json.dumps(allwords,indent=2))
 srt=''
 for i in range(0,len(allwords),4):
  g=allwords[i:i+4]; srt+=f'{i//4+1}\n{srtstamp(g[0]["start"])} --> {srtstamp(g[-1]["end"])}\n'+ ' '.join(w['text'] for w in g)+'\n\n'
 (out/'captions.srt').write_text(srt)
 final_target=out/(topic['key']+'.mp4')
 target=out/(topic['key']+'.rendering.mp4')
 cmd=['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i',str(out/'narration.wav'),'-map','0:v','-map','1:a','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-af','loudnorm=I=-16:TP=-1.5:LRA=9','-ar','48000','-movflags','+faststart','-shortest',str(target)]
 process=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=open(out/'render.log','w'))
 count=round(cursor*FPS)
 try:
  for frame in range(count):
   t=frame/FPS; s=next(s for s in timeline if s['start']<=t<s['end']+1e-5); local=(t-s['start'])/(s['end']-s['start'])
   im,d=base(topic,t,cursor,s)
   {'screen':screen,'usb':usb,'truck':truck,'wipers':wipers,'pin':pin,'walkaway':walkaway}[topic['visual']](d,s['mode'],local)
   captions(d,allwords,t)
   if frame in [0,int(count*.27),int(count*.59),int(count*.84)]: im.save(out/f'check-{frame}.jpg')
   process.stdin.write(im.tobytes())
  process.stdin.close(); code=process.wait(timeout=180)
  if code:raise RuntimeError((out/'render.log').read_text())
 except BaseException:
  process.kill();raise
 result=probe(target); v=next(x for x in result['streams'] if x['codec_type']=='video'); a=next(x for x in result['streams'] if x['codec_type']=='audio')
 assert v['width']==1080 and v['height']==1920 and v['r_frame_rate']=='30/1'
 assert a['sample_rate']=='48000' and 15<float(result['format']['duration'])<60
 assert all(0<=w['start']<w['end']<=cursor+.1 for w in allwords)
 os.replace(target,final_target)
 meta={k:topic[k] for k in ['key','title','label','source_url','source_section','equipment']}
 meta.update(duration=float(result['format']['duration']),privacy='private',review_status='source-reviewed; not vehicle-tested',voice='AndrewMultilingualNeural',source_checked=topic['source_reviewed_on'],build_digest=digest(topic),video_sha256=filehash(final_target),build_seconds=round(time.monotonic()-started,2),description=topic['description']+'\n\nOfficial manufacturer source: '+topic['source_url']+'\nIndependent, AI-assisted illustrated guide. Synthetic narration. Match your build, market and software; use your supplied manual. Not affiliated with the manufacturer. #Shorts #CarTips #ManualMinute')
 (out/'metadata.json').write_text(json.dumps(meta,indent=2)); (out/'script.txt').write_text('\n\n'.join(s['voice'] for s in topic['scenes']))
 print(json.dumps({'video':str(final_target),'duration':meta['duration'],'frames':count,'word_captions':len(allwords)}),flush=True)
async def main():
 p=argparse.ArgumentParser();p.add_argument('--topic',default='all');p.add_argument('--output',default=str(ROOT/'output'));p.add_argument('--force',action='store_true');a=p.parse_args()
 topics=json.loads((ROOT/'storyboards.json').read_text()); selected=[t for t in topics if a.topic=='all' or t['key'] in a.topic.split(',')]
 if len({t['key'] for t in topics})!=len(topics):raise ValueError('Duplicate topic keys')
 if not selected:raise ValueError('Unknown topic')
 for t in selected:
  if not date.fromisoformat(t['source_reviewed_on'])<=date.today()<=date.fromisoformat(t['review_due']):
   raise ValueError('Manufacturer source review expired; recheck before rendering')
  if urlparse(t['source_url']).hostname not in {'www.tesla.com','www.fordservicecontent.com'}:
   raise ValueError('Unapproved manufacturer source')
  out=Path(a.output)/t['key'];meta_path=out/'metadata.json';video=out/(t['key']+'.mp4')
  if not a.force and meta_path.exists() and video.exists():
   m=json.loads(meta_path.read_text())
   if m.get('build_digest')==digest(t) and m.get('video_sha256')==filehash(video):
    print(json.dumps({'topic':t['key'],'status':'reused validated render'}),flush=True);continue
  await build(t,Path(a.output))
if __name__=='__main__':asyncio.run(main())
