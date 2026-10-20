"""Offline narrated Shorts, finite original topic queue, and private-only uploads."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import textwrap
import urllib.error
import urllib.parse
import urllib.request
import wave
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'output'
STATE = ROOT / 'publish_state.json'
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
BRAND = 'WORKFLOW LAB'
TAGLINE = 'BETTER TOOLS. LESS WORK.'

def run(args):
    subprocess.run(args, check=True, timeout=300, stdout=subprocess.DEVNULL)

def load(path, default=None):
    return json.loads(path.read_text()) if path.exists() else default

def save(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n')

def topic_id(item):
    return hashlib.sha256(json.dumps(item, sort_keys=True).encode()).hexdigest()[:20]

def generate():
    OUT.mkdir(exist_ok=True)
    state = load(STATE, {})
    # An uncertain upload is never automatically retried or bypassed.
    if any(v.get('status') == 'reserved' for v in state.values()):
        raise RuntimeError('Unresolved upload reservation: reconcile in YouTube Studio before another upload.')
    items = load(ROOT / 'topics.json', [])
    item = next((x for x in items if topic_id(x) not in state), None)
    if item is None:
        raise RuntimeError('Original topic queue exhausted. Add reviewed scripts; do not recycle uploads.')
    slides = item['slides']
    if not 3 <= len(slides) <= 10 or len(item['title']) > 100:
        raise ValueError('Invalid topic structure')
    clips = []
    total = 0
    for i, text in enumerate(slides):
        if not isinstance(text, str) or not 1 <= len(text) <= 260:
            raise ValueError('Invalid narration length')
        wav = OUT / f'voice_{i:02d}.wav'
        run(['espeak-ng', '-v', 'en-us', '-s', '165', '-w', str(wav), text])
        with wave.open(str(wav)) as audio:
            duration = audio.getnframes() / audio.getframerate() + 0.4
        total += duration
        im = Image.new('RGB', (720, 1280), '#0d1a2c')
        draw = ImageDraw.Draw(im)
        draw.rounded_rectangle((40, 65, 680, 145), radius=20, fill='#1e5862')
        draw.text((65, 88), BRAND, font=ImageFont.truetype(FONT, 35), fill='white')
        draw.text((54, 235), f'{i+1:02d} / {len(slides):02d}', font=ImageFont.truetype(FONT, 30), fill='#5adbbc')
        size = 43
        caption_font = ImageFont.truetype(FONT, size)
        lines = []
        for word in text.split():
            candidate = (lines[-1] + ' ' + word) if lines else word
            if lines and caption_font.getlength(candidate) <= 612:
                lines[-1] = candidate
            else:
                lines.append(word)
        if len(lines) > 9:
            raise ValueError('Caption exceeds safe frame')
        y = max(330, 620 - len(lines)*30)
        for line in lines:
            draw.text((54, y), line, font=ImageFont.truetype(FONT, size), fill='white')
            y += 62
        draw.rectangle((54, 1040, 54 + int(612*(i+1)/len(slides)), 1052), fill='#5adbbc')
        draw.text((54, 1090), TAGLINE, font=ImageFont.truetype(FONT, 25), fill='white')
        png, clip = OUT/f'slide_{i:02d}.png', OUT/f'clip_{i:02d}.mp4'
        im.save(png)
        run(['ffmpeg', '-y', '-loglevel', 'error', '-loop', '1', '-i', str(png), '-i', str(wav), '-t', str(duration), '-af', 'apad', '-r', '24', '-c:v', 'libx264', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-ar', '48000', '-ac', '1', str(clip)])
        clips.append(clip)
    if not 15 <= total <= 90:
        raise ValueError(f'Video duration outside allowed range: {total:.1f}s')
    (OUT/'concat.txt').write_text(''.join(f"file '{p.name}'\n" for p in clips))
    run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', str(OUT/'concat.txt'), '-c', 'copy', '-movflags', '+faststart', str(OUT/'workflow_lab_short.mp4')])
    probe = subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(OUT/'workflow_lab_short.mp4')])
    streams = json.loads(probe)['streams']
    assert any(s['codec_type']=='audio' for s in streams), 'Missing narration'
    assert any(s['codec_type']=='video' and s['width']==720 and s['height']==1280 for s in streams)
    metadata = {'id': topic_id(item), 'title': item['title'], 'description': item['description']+'\n\n'+item.get('hashtags','#Shorts #WorkflowLab'), 'duration': round(total,2), 'privacy': 'private'}
    save(OUT/'metadata.json', metadata)
    (OUT/'script.txt').write_text('\n\n'.join(slides)+'\n')
    print(f'Validated narrated vertical video: {total:.1f}s; topic {metadata["id"]}')

def request(url, data=None, headers=None, method=None):
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    return urllib.request.urlopen(req, timeout=180)

def reserve():
    metadata = load(OUT/'metadata.json')
    state = load(STATE, {})
    if metadata['id'] in state:
        raise RuntimeError('Topic already uploaded or reserved')
    state[metadata['id']] = {'status':'reserved', 'run_id':os.environ.get('GITHUB_RUN_ID'), 'title': metadata['title']}
    save(STATE, state)

def upload():
    # Private is hard-coded until the owner approves public publishing.
    config = json.loads(os.environ['YOUTUBE_CREDENTIALS'])
    body = urllib.parse.urlencode({'client_id':config['client_id'], 'client_secret':config['client_secret'], 'refresh_token':config['refresh_token'], 'grant_type':'refresh_token'}).encode()
    with request('https://oauth2.googleapis.com/token', body) as res:
        token = json.load(res)['access_token']
    print('::add-mask::'+token)
    metadata = load(OUT/'metadata.json')
    state = load(STATE, {})
    entry = state.get(metadata['id'], {})
    if entry.get('status') != 'reserved' or entry.get('run_id') != os.environ.get('GITHUB_RUN_ID'):
        raise RuntimeError('Upload must have a persisted reservation from this run')
    video = OUT/'workflow_lab_short.mp4'
    payload = {'snippet':{'title':metadata['title'], 'description':metadata['description'], 'categoryId':'27'}, 'status':{'privacyStatus':'private','selfDeclaredMadeForKids':False}}
    headers = {'Authorization':'Bearer '+token, 'Content-Type':'application/json; charset=UTF-8', 'X-Upload-Content-Type':'video/mp4', 'X-Upload-Content-Length':str(video.stat().st_size)}
    with request('https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status', json.dumps(payload).encode(), headers) as res:
        location = res.headers['Location']
    # Never print the resumable session URL or automatically retry an uncertain upload.
    with request(location, video.read_bytes(), {'Authorization':'Bearer '+token,'Content-Type':'video/mp4'}, 'PUT') as res:
        result = json.load(res)
    state[metadata['id']] = {'status':'uploaded','video_id':result['id'],'privacy':result.get('status',{}).get('privacyStatus'),'run_id':os.environ.get('GITHUB_RUN_ID'),'title':metadata['title']}
    save(STATE,state)
    save(OUT/'upload_result.json',state[metadata['id']])
    if state[metadata['id']]['privacy'] != 'private':
        raise RuntimeError('Unexpected privacy status; inspect YouTube Studio immediately')
    print('Private upload accepted by YouTube: '+result['id'])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['generate','reserve','upload'], nargs='?', default='generate')
    args = parser.parse_args()
    try:
        {'generate':generate,'reserve':reserve,'upload':upload}[args.command]()
    except urllib.error.HTTPError as error:
        # Avoid emitting tokens, request bodies, or resumable session locations.
        print(f'Google API returned HTTP {error.code}. Inspect account authorization/quota; no automatic upload retry.',file=sys.stderr)
        sys.exit(1)
