'use strict';
window.FieldOCRControls={create({api,apply,message}){
 const $=id=>document.getElementById(id);
 let addressDirty=false,busy=false,current=null,signature='';
 $('ocrAddress').addEventListener('input',()=>{addressDirty=true;if(current)sync(current)});
 async function command(path,body,resetAddress=false){
  // Manual takeover remains available even while a connection request is pending.
  if(busy&&path!=='manual')return;
  busy=true;
  try{const state=await api('/api/ocr/'+path,'POST',body);if(resetAddress)addressDirty=false;apply(state)}
  catch(err){message(err.message)}
  finally{busy=false;if(current)sync(current)}
 }
 $('ocrConnect').addEventListener('click',()=>command('connect',{address:$('ocrAddress').value.trim()},true));
 $('ocrField').addEventListener('change',()=>command('field',{field:$('ocrField').value}));
 $('ocrFollow').addEventListener('click',()=>command('follow',{}));
 $('ocrManual').addEventListener('click',()=>command('manual',{}));
 function sync(state){
  current=state;
  const o=state.ocr||{address:'http://127.0.0.1:18099',fields:[],connection:'disconnected',reading:'not_checked'};
  if(!addressDirty&&document.activeElement!==$('ocrAddress'))$('ocrAddress').value=o.address;
  const fields=o.fields||[],next=JSON.stringify([fields,o.field]);
  if(signature!==next){
   signature=next;
   const options=fields.map(name=>new Option(name,name));
   if(!fields.includes(o.field))options.unshift(new Option(o.field?o.field+' (missing)':'Connect to discover fields',o.field||''));
   $('ocrField').replaceChildren(...options);$('ocrField').value=o.field||'';
  }
  const following=!!o.following;
  $('ocrMode').textContent=following?'FOLLOWING OCR':'MANUAL';
  $('ocrMode').classList.toggle('ocr-following',following);
  $('ocrFollow').setAttribute('aria-pressed',String(following));
  $('ocrFollow').disabled=busy||addressDirty||following||!o.can_follow;
  $('ocrManual').disabled=!following;
  $('ocrConnect').disabled=busy||following;
  $('ocrField').disabled=busy||following||!fields.length;
  $('ocrAddress').disabled=following;
  const connection={disconnected:'Not connected',connecting:'Connecting…',connected:'Connected to ScoreSight',error:'Connection lost / unavailable'};
  const reading={not_checked:'Not checked',waiting:'Waiting for a reading',accepted:'Valid MM:SS reading',missing:'Selected field missing',rejected:'Reading rejected or empty',malformed:'Invalid MM:SS reading',unavailable:'No reading available'};
  $('ocrConnection').textContent=connection[o.connection]||'Connection unavailable';
  $('ocrConnection').classList.toggle('ocr-online',o.connection==='connected');
  $('ocrReadingStatus').textContent=(reading[o.reading]||'Waiting')+(o.detection_state?' · '+o.detection_state:'');
  $('ocrRecognized').textContent=o.recognized||'—';
  $('ocrAccepted').textContent=o.last_accepted||'—';
  $('ocrWarning').textContent=o.warning||'Connect to inspect readings. Only Follow OCR clock changes the match time.';
  $('ocrWarning').classList.toggle('ocr-attention',!!o.warning);
  $('ocrAge').textContent=o.value_change_age_ms>=0?'Value last changed '+Math.floor(o.value_change_age_ms/1000)+'s ago. This is not a video heartbeat.':'Video freshness cannot be verified from this ScoreSight endpoint.';
  $('ocrManualHelp').textContent=following?'Take manual control before using match or combined controls. Shot controls remain independent; shot resets stay Ready because OCR does not report running state.':'Manual takeover keeps the displayed match time paused. Press Start / Resume when ready. Following again is always explicit.';
  document.querySelectorAll('[data-clock-action^="main:"],[data-clock-action^="both:"],[data-clock-set="main"],[data-clock-adjust^="main:"]').forEach(button=>{
   if(following)button.disabled=true;
   else if(button.dataset.clockAction?.startsWith('main:')){
    const action=button.dataset.clockAction.split(':')[1];
    button.disabled=action==='start'?state.main.state==='running':action==='pause'?state.main.state!=='running':false;
   }else button.disabled=false;
  });
  window.refreshTouchOptions?.();
 }
 return {sync};
}};
