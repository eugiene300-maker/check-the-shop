'use strict';
const ShopSearch = {
 normalize(value) {
  return String(value || '').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase()
   .replace(/\bstreet\b/g,'st').replace(/\bavenue\b/g,'ave').replace(/\bboulevard\b/g,'blvd').replace(/\broad\b/g,'rd').replace(/\bdrive\b/g,'dr').replace(/\bcircle\b/g,'cir')
   .replace(/\bnorth\b/g,'n').replace(/\bsouth\b/g,'s').replace(/\bwest\b/g,'w').replace(/\beast\b/g,'e').replace(/[^a-z0-9]+/g,' ').trim();
 },
 active(record) { return ['Active','About to Expire'].includes(record.licenseStatus); },
 matches(record, query) {
  const q=this.normalize(query),hay=this.normalize(record.searchText);
  return !q || q.split(/\s+/).every(token=>hay.includes(token)) || hay.replace(/\s/g,'').includes(q.replace(/\s/g,''));
 },
 filter(records,query,status='all') {
  return records.filter(record=>this.matches(record,query) && (status==='all' || (status==='active' ? this.active(record) : !this.active(record))));
 }
};
if(typeof module!=='undefined'&&module.exports)module.exports=ShopSearch;
if(typeof document!=='undefined'){
 const data=JSON.parse(document.getElementById('site-data').textContent);
 const input=document.getElementById('shop-search'),list=document.getElementById('suggestions');
 let filter='all',suggestions=[],active=-1;
 function close(){if(!list)return;list.hidden=true;input.setAttribute('aria-expanded','false');input.removeAttribute('aria-activedescendant');active=-1;}
 function update(){
  const matches=ShopSearch.filter(data.records,input.value,filter),found=new Set(matches.map(record=>record.licenseNumber));
  document.querySelectorAll('[data-record]').forEach(card=>card.hidden=!found.has(card.dataset.record));
  document.getElementById('empty').hidden=matches.length>0;
  document.getElementById('result-count').textContent=matches.length+' license record'+(matches.length===1?'':'s')+(input.value.trim()?' match':' · San Jose');
 }
 function pick(index){const record=suggestions[index];if(!record)return;input.value=record.licenseNumber;filter='all';document.querySelectorAll('[data-filter]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.filter===filter)));update();close();input.focus();document.getElementById('results').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});}
 function show(){
  suggestions=ShopSearch.filter(data.records,input.value).slice(0,7);active=-1;list.replaceChildren();input.removeAttribute('aria-activedescendant');
  suggestions.forEach((record,index)=>{
   const item=document.createElement('li');item.role='option';item.id='suggestion-'+index;item.setAttribute('aria-selected','false');
   const name=document.createElement('strong');name.textContent=record.displayName;item.append(name);
   const details=document.createElement('small');details.textContent=record.premiseStreetAddress+' · '+record.licenseNumber;item.append(details);
   item.addEventListener('pointerdown',event=>event.preventDefault());item.addEventListener('click',()=>pick(index));list.append(item);
  });
  list.hidden=!suggestions.length;input.setAttribute('aria-expanded',String(suggestions.length>0));
 }
 if(input){
  input.addEventListener('input',()=>{update();show();});input.addEventListener('focus',show);input.addEventListener('blur',close);
  input.addEventListener('keydown',event=>{
   if(event.isComposing)return;
   if(event.key==='Escape'||event.key==='Tab'){close();return;}
   if(event.key==='Enter'&&active>=0&&!list.hidden){event.preventDefault();pick(active);return;}
   if(!['ArrowDown','ArrowUp'].includes(event.key))return;
   event.preventDefault();if(list.hidden)show();if(!suggestions.length)return;
   active=(active+(event.key==='ArrowDown'?1:(active<0?0:-1))+suggestions.length)%suggestions.length;
   [...list.children].forEach((item,index)=>item.setAttribute('aria-selected',String(index===active)));
   input.setAttribute('aria-activedescendant',list.children[active].id);list.children[active].scrollIntoView({block:'nearest'});
  });
  document.getElementById('lookup').addEventListener('submit',event=>{event.preventDefault();close();update();document.getElementById('results').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});});
  document.querySelectorAll('[data-filter]').forEach(button=>button.addEventListener('click',()=>{filter=button.dataset.filter;document.querySelectorAll('[data-filter]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));update();close();}));
  document.addEventListener('pointerdown',event=>{if(!event.target.closest('.typeahead'))close();});
  const age=Date.now()-Date.parse(data.checked_at);if(!Number.isFinite(age)||age>3*86400000){const status=document.getElementById('freshness');status.hidden=false;status.textContent='This snapshot is more than three days old or its date could not be read. Open the official state record for the latest published status.';}
 }
 document.querySelector('[data-share]')?.addEventListener('click',async()=>{const url=document.querySelector('link[rel=canonical]').href;const status=document.getElementById('share-status');try{await navigator.clipboard.writeText(url);status.textContent='Record link copied.';}catch{status.textContent=url;}});
}
