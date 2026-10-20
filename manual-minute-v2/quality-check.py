"""Decode videos, validate audio/captions and build a deduplicated private-upload queue."""
import argparse,hashlib,json,subprocess
from pathlib import Path
from build import digest
from datetime import datetime,timezone,date
root=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--topic',default='all');a=p.parse_args()
all_topics=json.loads((root/'storyboards.json').read_text())
topics=[t for t in all_topics if a.topic=='all' or t['key'] in a.topic.split(',')]
if len({t['key'] for t in all_topics})!=len(all_topics):raise ValueError('Duplicate topic keys')
if a.topic!='all' and set(a.topic.split(','))-{t['key'] for t in all_topics}:raise ValueError('Unknown topic selection')
if not topics:raise ValueError('No topics selected')
# Never leave a previous success queue behind when this check fails.
(root/'ready-queue.json').unlink(missing_ok=True)
(root/'quality-results.json').unlink(missing_ok=True)
results=[];queue=[];seen=set()
for topic in topics:
    folder=root/'output'/topic['key'];video=folder/(topic['key']+'.mp4')
    assert date.fromisoformat(topic['source_reviewed_on'])<=date.today()<=date.fromisoformat(topic['review_due']),'Source review expired'
    script_id=hashlib.sha256(' '.join(s['voice'].strip().lower() for s in topic['scenes']).encode()).hexdigest()
    assert script_id not in seen,'Duplicate narration script';seen.add(script_id)
    p=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]))
    v=next(x for x in p['streams'] if x['codec_type']=='video');audio=next(x for x in p['streams'] if x['codec_type']=='audio')
    duration=float(p['format']['duration'])
    assert (v['width'],v['height'],v['r_frame_rate'])==(1080,1920,'30/1')
    assert 15<duration<60 and audio['sample_rate']=='48000'
    words=json.loads((folder/'words.json').read_text())
    assert words and all(0<=w['start']<w['end']<=duration+.15 for w in words)
    assert all(words[i]['start']<=words[i+1]['start'] for i in range(len(words)-1))
    log=subprocess.run(['ffmpeg','-v','info','-i',str(video),'-af','volumedetect','-f','null','-'],capture_output=True,text=True,check=True).stderr
    assert not any(e in log.lower() for e in ['error while decoding','invalid data found','corrupt decoded frame'])
    mean=next(l.split('mean_volume:')[1].strip() for l in log.splitlines() if 'mean_volume:' in l)
    peak=next(l.split('max_volume:')[1].strip() for l in log.splitlines() if 'max_volume:' in l)
    assert -35<float(mean.split()[0])<-8 and float(peak.split()[0])<0
    sha=hashlib.sha256(video.read_bytes()).hexdigest()
    meta=json.loads((folder/'metadata.json').read_text())
    assert meta.get('build_digest')==digest(topic),'Render is stale; rebuild after source or renderer changes'
    assert (folder/'captions.srt').is_file() and (folder/'captions.srt').stat().st_size>0,'Missing captions'
    assert meta.get('video_sha256')==sha,'Video changed after render metadata was written'
    assert meta['source_url']==topic['source_url'] and len(meta['title'])<=100
    results.append(dict(topic=topic['key'],duration=duration,resolution='1080x1920',fps=30,words=len(words),mean_volume=mean,peak_volume=peak,status='passed',sha256=sha))
    queue.append(dict(topic=topic['key'],title=meta['title'],video=str(video.relative_to(root)),metadata=str((folder/'metadata.json').relative_to(root)),captions=str((folder/'captions.srt').relative_to(root)),script_id=script_id,video_sha256=sha,status='rendered_verified',publication_status='not_uploaded',privacy='private',source_review_due=topic['review_due']))
stamp=datetime.now(timezone.utc).isoformat()
(root/'quality-results.json').write_text(json.dumps({'checked_at':stamp,'results':results},indent=2))
queue_path=root/'ready-queue.json';temporary=queue_path.with_suffix('.tmp')
temporary.write_text(json.dumps({'generated_at':stamp,'publishing_enabled':False,'entries':queue},indent=2));temporary.replace(queue_path)
print(json.dumps(results,indent=2))

