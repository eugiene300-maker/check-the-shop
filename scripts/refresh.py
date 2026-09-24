"""Refresh public license records. Preserve the last valid snapshot on failure."""
from pathlib import Path
from datetime import datetime,timezone
from html.parser import HTMLParser
import json,urllib.request,urllib.parse,re,sys
ROOT=Path(__file__).resolve().parents[1]
CITY='https://www.sjpd.org/about-us/organization/chief-executive-officer/cannabis-regulation/be-confident-buy-legal'
API='https://as-dcc-pub-cann-w-p-002.azurewebsites.net/licenses/AdvancedSearch'
FIELDS=['id','licenseNumber','licenseStatus','licenseType','licenseDesignation','issueDate','expirationDate','businessLegalName','businessDbaName','activity','premiseStreetAddress','premiseCity','premiseState','premiseZipCode','dataRefreshedDate']
def get(url):
 req=urllib.request.Request(url,headers={'User-Agent':'CheckTheShop/1.0 public-records refresh'})
 with urllib.request.urlopen(req,timeout=35) as r:return r.read()
def write(path,data):
 temp=path.with_suffix('.tmp');temp.write_text(json.dumps(data,indent=2)+'\n');temp.replace(path)
def refresh():
 now=datetime.now(timezone.utc).isoformat();log={'attempted_at':now,'checks':[]}
 try:
  records=[];page=1
  while True:
   d=json.loads(get(API+'?'+urllib.parse.urlencode({'premiseCity':'San Jose','pageSize':1000,'page':page})))
   if not isinstance(d.get('data'),list) or 'metadata' not in d:raise ValueError('Unexpected DCC response')
   records.extend(d['data'])
   if not d['metadata'].get('hasNext'):break
   page+=1
   if page>20:raise ValueError('Unexpected pagination')
  records=[{k:r.get(k) for k in FIELDS} for r in records if r.get('premiseCity','').lower()=='san jose' and ('retailer' in r.get('licenseType','').lower() or 'retailer' in r.get('activity','').lower())]
  if len(records)<10 or any(not r.get('licenseNumber') or not r.get('licenseStatus') for r in records):raise ValueError('DCC returned incomplete data; retaining previous snapshot')
  if len({r['licenseNumber'] for r in records})!=len(records):raise ValueError('Duplicate license records')
  write(ROOT/'data/state.json',{'checked_at':now,'source':'https://search.cannabis.ca.gov/','api':API,'records':records})
  log['checks'].append({'source':'DCC','status':'ok','records':len(records)})
 except Exception as error:log['checks'].append({'source':'DCC','status':'error','message':str(error)})
 try:
  html=get(CITY).decode();parser=CityTable();parser.feed(html)
  rows=[]
  for cells in parser.rows:
   if len(cells)>=5 and re.search(r'\d',cells[3]) and re.match(r'^\d',cells[3]):
    name=re.sub(r'^\d+\.\s*','',cells[0]).strip()
    if name:rows.append({'name':name,'address':cells[3],'district':cells[2]})
  date=re.search(r'as\s+of\s+(\d{2}/\d{2}/\d{4})',re.sub('<[^>]+>',' ',html),re.I)
  if len(rows)<10 or not date:raise ValueError('City table or source date could not be validated')
  write(ROOT/'data/city.json',{'source':CITY,'source_date':datetime.strptime(date.group(1),'%m/%d/%Y').date().isoformat(),'reviewed_at':now,'method':'official page','records':rows})
  log['checks'].append({'source':'SJPD','status':'ok','records':len(rows)})
 except Exception as error:log['checks'].append({'source':'SJPD','status':'error','message':str(error)})
 write(ROOT/'data/refresh-status.json',log)
 print(json.dumps(log))
 if not (ROOT/'data/state.json').exists():sys.exit('No valid DCC snapshot available')
class CityTable(HTMLParser):
 def __init__(self):super().__init__();self.rows=[];self.row=[];self.cell=None
 def handle_starttag(self,tag,attrs):
  if tag=='tr':self.row=[]
  if tag in ['td','th']:self.cell=''
 def handle_data(self,text):
  if self.cell is not None:self.cell+=text
 def handle_endtag(self,tag):
  if tag in ['td','th'] and self.cell is not None:self.row.append(re.sub(r'\s+',' ',self.cell).strip());self.cell=None
  if tag=='tr' and self.row:self.rows.append(self.row)
if __name__=='__main__':refresh()
