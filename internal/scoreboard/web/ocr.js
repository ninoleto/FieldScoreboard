'use strict';
window.FieldOCRControls={create({api,begin,finish,apply,message}){
 const $=id=>document.getElementById(id),targets=['main','shot','home_score','away_score','home_fouls','away_fouls','period'];
 const el=(target,suffix)=>$('ocr-'+target+'-'+suffix);
 let addressDirty=false,connectionAction=null,current=null;
 const busy=new Set(),signatures={};
 $('ocrAddress').addEventListener('input',()=>{addressDirty=true;if(current)sync(current)});
 async function command(path,body){
  const key=body.target||'connection';
  if(key==='connection'&&(connectionAction||(path==='connect'&&['connecting','connected'].includes(current?.ocr?.connection))))return;
  if(key!=='connection'&&connectionAction)return;
  if(busy.has(key)&&path!=='manual')return;
  const epoch=begin();busy.add(key);if(key==='connection')connectionAction=path;if(current)sync(current);
  try{const state=await api('/api/ocr/'+path,'POST',body);if(path==='connect')addressDirty=false;apply(state,epoch)}
  catch(err){message(err.message)}
  finally{finish();busy.delete(key);if(key==='connection')connectionAction=null;if(current)sync(current)}
 }
 $('ocrConnect').addEventListener('click',()=>command('connect',{address:$('ocrAddress').value.trim()}));
 $('ocrDisconnect').addEventListener('click',()=>command('disconnect',{}));
 for(const target of targets){
  el(target,'field').addEventListener('change',()=>command('field',{target,field:el(target,'field').value}));
  el(target,'follow').addEventListener('click',()=>command('follow',{target}));
  el(target,'manual').addEventListener('click',()=>command('manual',{target}));
 }
 function sync(state){
  current=state;
  const o=state.ocr||{address:'http://127.0.0.1:18099',fields:[],connection:'disconnected'},views=o.targets||{};
  const follows=target=>!!views[target]?.following;
  if(!addressDirty&&document.activeElement!==$('ocrAddress'))$('ocrAddress').value=o.address;
  const pending=!!connectionAction,monitoring=!!o.monitoring;
  const connectionState=connectionAction==='connect'?'connecting':o.connection||'disconnected';
  const connect=$('ocrConnect'),disconnect=$('ocrDisconnect');
  connect.disabled=pending||['connecting','connected'].includes(o.connection);
  disconnect.disabled=pending||!monitoring;
  connect.setAttribute('aria-busy',String(connectionAction==='connect'||o.connection==='connecting'));
  disconnect.setAttribute('aria-busy',String(connectionAction==='disconnect'));
  $('ocrConnectHelp').textContent=connectionAction==='disconnect'?'Disconnecting and returning followed fields to manual control…':connectionState==='connecting'?'Connecting to ScoreSight. You can disconnect to cancel once this request completes.':monitoring?'Disconnect stops polling and returns followed fields to manual control, keeping their values and pausing followed clocks.':'Connect to inspect readings, then choose Follow OCR for each field. Connecting never starts clocks.';
  $('ocrAddress').disabled=pending||monitoring;
  const connection={disconnected:'Not connected',connecting:'Connecting…',connected:'Connected',error:o.response_age_ms>=0?'Connection lost':'Connection failed'};
  $('ocrConnection').textContent=connection[connectionState]||'Connection failed';
  $('ocrConnection').dataset.connection=connectionState;
  $('ocrWarning').textContent=o.connection_warning||'';
  $('ocrWarning').classList.toggle('ocr-attention',!!o.connection_warning);
  const reading={unconfigured:'Unconfigured — manual',not_checked:'Not checked',disconnected:'Disconnected — value retained',waiting:'Waiting for a reading',accepted:'Accepted reading',missing:'Selected field missing',rejected:'Reading rejected or empty',malformed:'Invalid reading',unavailable:'No reading available',save_error:'Could not save'};
  for(const target of targets){
   const t=views[target]||{},field=t.field||'',fields=o.fields||[],following=follows(target);
   const next=JSON.stringify([fields,field]);
   if(signatures[target]!==next){
    signatures[target]=next;
    const options=[new Option('Unconfigured — manual',''),...fields.map(name=>new Option(name,name))];
    if(field&&!fields.includes(field))options.push(new Option(field+' (missing)',field));
    el(target,'field').replaceChildren(...options);el(target,'field').value=field;
   }
   el(target,'field').disabled=pending||busy.has(target)||following;
   el(target,'mode').textContent=following?'FOLLOWING OCR':'MANUAL';
   el(target,'mode').classList.toggle('ocr-following',following);
   el(target,'follow').setAttribute('aria-pressed',String(following));
   el(target,'follow').disabled=pending||busy.has(target)||addressDirty||following||!t.can_follow;
   el(target,'manual').disabled=pending||!following;
   el(target,'recognized').textContent=t.recognized||'—';
   el(target,'accepted').textContent=t.last_accepted||'—';
   el(target,'reading').textContent=(reading[t.reading]||reading.unconfigured)+(t.detection_state?' · '+t.detection_state:'');
   el(target,'warning').textContent=t.warning||'';
   el(target,'warning').classList.toggle('ocr-attention',!!t.warning);
  }
  for(const target of ['main','shot']){
   const following=follows(target);
   document.querySelectorAll(`[data-clock-action^="${target}:"],[data-clock-set="${target}"],[data-clock-adjust^="${target}:"]${target==='shot'?', [data-shot-preset]':''}`).forEach(button=>{
    if(following)button.disabled=true;
    else if(button.dataset.clockAction){
     const action=button.dataset.clockAction.split(':')[1];
     button.disabled=action==='start'?state[target].state==='running':action==='pause'?state[target].state!=='running':false;
    }else button.disabled=false;
   });
  }
  const clockOwned=follows('main')||follows('shot');
  document.querySelectorAll('[data-clock-action^="both:"]').forEach(b=>b.disabled=clockOwned);
  $('bothOCRHelp').hidden=!clockOwned;
  for(const target of ['home_score','away_score','home_fouls','away_fouls','period']){
   document.querySelectorAll(`[data-adjust^="${target}:"],[data-exact="${target}"]`).forEach(b=>b.disabled=follows(target)||(target==='period'&&!!b.dataset.adjust&&state.period_overtime));
   const owner={home_score:'homeScoreOwner',away_score:'awayScoreOwner',home_fouls:'homeFoulsOwner',away_fouls:'awayFoulsOwner',period:'periodOwner'};$(owner[target]).hidden=!follows(target);
  }
  // Server guards also reject stale dialogs and external API/Companion requests.
  const reset=$('resetMatch');if(reset)reset.disabled=['home_score','away_score','home_fouls','away_fouls','period'].some(follows);
  window.refreshTouchOptions?.();
 }
 return {sync};
}};
