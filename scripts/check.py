from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
import json,subprocess
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'dist'
class Check(HTMLParser):
 def __init__(self):super().__init__();self.h1=0;self.refs=[];self.ids=[];self.a=0;self.sponsor=0
 def handle_starttag(self,t,a):
  a=dict(a)
  if t=='h1':self.h1+=1
  if a.get('id'):self.ids.append(a['id'])
  if t=='a':
   assert self.a==0,'Nested links';self.a+=1
   if 'plpcsanjose.com' in a.get('href','') and 'sponsored' in a.get('rel',''):self.sponsor+=1
  if t in ['a','link','script','img']:
   self.refs.append(a.get('href') or a.get('src') or '')
 def handle_endtag(self,t):
  if t=='a':self.a-=1
pages=list(OUT.glob('*.html'))
for file in pages:
 p=Check();p.feed(file.read_text());assert p.h1==1,file.name;assert len(p.ids)==len(set(p.ids)),file.name;assert p.sponsor==1,file.name
 for link in p.refs:
  u=urlsplit(link)
  if not u.scheme and not u.netloc and u.path:assert (OUT/u.path).exists(),(file.name,link)
data=json.loads((OUT/'data.json').read_text());nums=[r['licenseNumber'] for r in data['records']];assert len(nums)==len(set(nums))
for r in data['records']:assert (OUT/r['url']).exists()
subprocess.run(['node','--check',str(ROOT/'src/app.js')],check=True)
print(json.dumps({'pages':len(pages),'local_links':'passed','sponsor_links':'passed','license_records':len(nums)}))
