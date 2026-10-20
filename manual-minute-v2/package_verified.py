"""Package only the selection that passed the current quality check."""
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def package():
    queue = json.loads((ROOT / 'ready-queue.json').read_text())
    if not queue['entries']:
        raise ValueError('No verified videos')
    target = ROOT / 'review-package'
    if target.exists():
        shutil.rmtree(target)
    target.mkdir()
    for entry in queue['entries']:
        video = ROOT / entry['video']
        if hashlib.sha256(video.read_bytes()).hexdigest() != entry['video_sha256']:
            raise ValueError('Video changed after quality check')
        for field in ('video', 'metadata', 'captions'):
            source = (ROOT / entry[field]).resolve()
            source.relative_to(ROOT / 'output')
            destination = target / source.relative_to(ROOT)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
    for name in ('ready-queue.json', 'quality-results.json'):
        shutil.copy2(ROOT / name, target / name)
    print(f"Packaged {len(queue['entries'])} verified videos")

if __name__ == '__main__':
    package()
