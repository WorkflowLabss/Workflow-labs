import json, subprocess, pathlib, textwrap, random
from PIL import Image, ImageDraw, ImageFont
ROOT=pathlib.Path(__file__).parent
OUT=ROOT/'output'; OUT.mkdir(exist_ok=True)
items=json.loads((ROOT/'topics.json').read_text())
item=items[0]
font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
regular='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
W,H=720,1280
slides=item['slides']; duration=6
for i,slide in enumerate(slides):
    im=Image.new('RGB',(W,H),(13,26,44)); d=ImageDraw.Draw(im)
    d.rounded_rectangle((40,55,680,135),radius=20,fill=(30,88,98))
    d.text((65,78),'WORKFLOW LAB',font=ImageFont.truetype(font,35),fill='white')
    d.text((54,250),f'{i+1:02d} / {len(slides):02d}',font=ImageFont.truetype(regular,35),fill=(90,219,188))
    words=textwrap.wrap(slide,width=19)
    y=420
    for line in words:
        d.text((54,y),line,font=ImageFont.truetype(font,54),fill='white'); y+=78
    d.rounded_rectangle((54,1050,666,1118),radius=22,fill=(30,88,98))
    d.text((78,1067),'BETTER TOOLS. LESS WORK.',font=ImageFont.truetype(font,25),fill='white')
    im.save(OUT/f'slide_{i:02d}.png')
    subprocess.run(['ffmpeg','-y','-loglevel','error','-loop','1','-i',str(OUT/f'slide_{i:02d}.png'),'-t',str(duration),'-r','24','-c:v','libx264','-pix_fmt','yuv420p',str(OUT/f'clip_{i:02d}.mp4')],check=True)
with (OUT/'concat.txt').open('w') as f:
    for i in range(len(slides)): f.write(f"file 'clip_{i:02d}.mp4'\n")
subprocess.run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i',str(OUT/'concat.txt'),'-c','copy',str(OUT/'workflow_lab_short.mp4')],check=True)
(OUT/'youtube_metadata.txt').write_text(item['title']+'\n\n'+item['description']+'\n\n'+item['hashtags'])
print('Created output/workflow_lab_short.mp4 (silent storyboard).')
