"""Isolated draft-only manufacturer-manual video series. No upload path."""
import argparse
from datetime import date
import json
from pathlib import Path
import tempfile
from urllib.parse import urlparse
import generate as engine

ROOT=Path(__file__).resolve().parent
DATA=ROOT
ALLOWED_HOSTS={'www.tesla.com','www.fordservicecontent.com','www.toyota.com','assets.sia.toyota.com'}

def validate(topic,today=None):
    today=today or date.today()
    for key in ('key','vehicle','model_years','market','equipment','source_section','source_url','manual_edition','source_reviewed_on','review_due','review_status','risk_class','title','description','slides'):
        if not topic.get(key): raise ValueError('Missing required field: '+key)
    parsed=urlparse(topic['source_url'])
    if parsed.scheme!='https' or parsed.hostname not in ALLOWED_HOSTS or parsed.username or parsed.password:
        raise ValueError('Use an approved official manufacturer source URL')
    reviewed=date.fromisoformat(topic['source_reviewed_on']); due=date.fromisoformat(topic['review_due'])
    if not reviewed<=today<=due or (due-reviewed).days>30:
        raise ValueError('Source review expired or invalid: '+topic['key'])
    if topic['review_status']!='source-reviewed-draft' or topic['risk_class']!='stationary-convenience':
        raise ValueError('Topic is outside this draft pipeline review policy')
    if topic['source_url'] not in topic['description']:
        raise ValueError('Manufacturer source must appear in video description')
    if len(topic['title'])>100 or len(topic['description'])>5000:
        raise ValueError('YouTube metadata length exceeded')
    if not 3<=len(topic['slides'])<=10 or any(not isinstance(x,str) or not 1<=len(x)<=260 for x in topic['slides']):
        raise ValueError('Invalid scene structure')

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--topic',default='all',help='all or one checked topic key')
    parser.add_argument('--validate-only',action='store_true')
    args=parser.parse_args()
    topics=json.loads((DATA/'vehicle_topics.json').read_text())
    if len({t['key'] for t in topics})!=len(topics): raise ValueError('Duplicate topic key')
    selected=[t for t in topics if args.topic=='all' or t['key']==args.topic]
    if not selected: raise ValueError('Unknown topic key')
    for topic in selected: validate(topic)
    if args.validate_only:
        print(f'Validated {len(selected)} source-reviewed drafts; publishing is disabled.')
        return
    for topic in selected:
        with tempfile.TemporaryDirectory() as temporary:
            engine.ROOT=Path(temporary)
            (engine.ROOT/'topics.json').write_text(json.dumps([topic]))
            engine.OUT=ROOT/'output'/'vehicle-manuals'/topic['key']
            engine.OUT.mkdir(parents=True,exist_ok=True)
            # Separate future upload ledger; the Workflow Lab topic state is never used.
            engine.STATE=DATA/'vehicle_publish_state.json'
            engine.BRAND='MANUAL MINUTE'
            engine.TAGLINE='KNOW YOUR VEHICLE.'
            engine.generate()
            provenance={k:topic[k] for k in ('key','vehicle','model_years','market','equipment','source_section','source_url','manual_edition','source_reviewed_on','review_due','review_status')}
            (engine.OUT/'source_review.json').write_text(json.dumps(provenance,indent=2)+'\n')
            print('Draft ready: '+topic['key'])

if __name__=='__main__': main()
