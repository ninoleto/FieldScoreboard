'use strict';
(() => {
 const $=id=>document.getElementById(id);
 const stage=window.FieldStage;
 const names={period:'Period',main_clock:'Match clock',shot_clock:'Shot clock',home_name:'Home name',away_name:'Away name',home_score:'Home score',away_score:'Away score',home_fouls:'Home fouls',away_fouls:'Away fouls'};
 const headers=()=>({'Content-Type':'application/json',...(token?{'Authorization':`Bearer ${token}`}:{})});
 let token=sessionStorage.getItem('field_scoreboard_api_token')||'';
 let s=null,layout=null,dirty=false,selected='main_clock',dragging=null,tab='control',pollBusy=false,opBusy=false,messageTimer;
 let backgroundEditor=null,elementEditor=null,layoutRevision=0,layoutSaveBusy=false;
 const editorSelection=()=>backgroundEditor?.selected?'background':selected;
 let mainDraftDirty=false,shotDraftDirty=false,networkDirty=false,builderHostDirty=false,stateEpoch=0,ocrPending=0;
 let detectedInterfaces=[],selectedIP='',builderToken=token;
 const displayFields={homeFoulStyle:'foul_style_home',awayFoulStyle:'foul_style_away',foulDotsMax:'foul_dots_max',mainFormat:'main_clock_format',shotFormat:'shot_clock_format'};
 const displayPending=new Map(),displayDrafts=new Map();let displayBusy=false,displayWait=null,dotsDirty=false;
 const fullLayout=()=>JSON.parse(JSON.stringify(layout));
 function message(v,good=false){let b=$('banner');b.textContent=v;b.classList.remove('hidden');b.classList.toggle('success',good);clearTimeout(messageTimer);if(good)messageTimer=setTimeout(()=>b.classList.add('hidden'),4000)}
 async function api(path,method='GET',body){
  const opts={method,cache:'no-store',headers:headers()};if(body!==undefined)opts.body=JSON.stringify(body);
  const res=await fetch(path,opts);let j={};try{j=await res.json()}catch(_){throw Error('Invalid server response')}
  if(res.status===401){$('authGate').classList.remove('hidden');throw Error('Remote API token required')}
  if(!res.ok)throw Error(j.error||`HTTP ${res.status}`);
  $('authGate').classList.add('hidden');return j;
 }
 async function action(path,body){if(opBusy)return;opBusy=true;const epoch=++stateEpoch;try{const response=await api(path,'POST',body);if(epoch===stateEpoch){s=response;draw()}return true}catch(err){message(err.message);return false}finally{opBusy=false}}
 async function poll(){if(pollBusy||opBusy||layoutSaveBusy||ocrPending)return;pollBusy=true;const epoch=stateEpoch;try{const response=await api('/api/state');if(epoch!==stateEpoch)return;s=response;$('connected').classList.add('ok');$('connected').classList.remove('bad');$('connectionLabel').textContent='Connected';draw()}catch(err){if(epoch!==stateEpoch)return;$('connected').classList.add('bad');$('connected').classList.remove('ok');$('connectionLabel').textContent='Offline';if(!String(err).includes('token'))message(err.message)}finally{pollBusy=false}}
 const ocrControls=window.FieldOCRControls.create({api,begin:()=>{ocrPending++;return ++stateEpoch},finish:()=>{ocrPending--},apply:(state,epoch)=>{if(epoch===stateEpoch){s=state;draw()}},message});
 function draw(){
  if(!s)return;
  stage.paint($('previewStage'),s,s.layout,null);stage.scale($('previewStage'));
  if(layout)for(const key of Object.values(displayFields))layout[key]=s.layout[key];
  if(!layout || (!dirty && JSON.stringify(layout)!==JSON.stringify(s.layout))){layout=JSON.parse(JSON.stringify(s.layout));updateInspector()}
  stage.paint($('editorStage'),s,layout,editorSelection(),dragging?.id);stage.scale($('editorStage'));
  ['homeName','awayName'].forEach(id=>{const el=$(id);if(document.activeElement!==el)el.value=s[id==='homeName'?'home_name':'away_name']});
  $('periodValue').textContent=s.period_label||String(s.period);
  $('periodOT').checked=!!s.period_overtime;
  for(const button of document.querySelectorAll('[data-period-format]')){
   const active=button.dataset.periodFormat===(s.period_format||'number');
   button.setAttribute('aria-checked',String(active));button.tabIndex=active?0:-1;
  }
  for(const b of document.querySelectorAll('[data-adjust^="period:"]'))b.disabled=!!s.period_overtime;
  for(const [field,id] of [['home_score','homeScore'],['away_score','awayScore'],['home_fouls','homeFouls'],['away_fouls','awayFouls']])$(id).textContent=s[field];
  $('mainDisplay').textContent=s.main.display;$('mainState').textContent=s.main.state.toUpperCase();$('shotDisplay').textContent=s.shot.display;$('shotState').textContent=s.shot.state.toUpperCase();
  for(const id of ['main','shot']){const isRunning=s[id].state==='running';for(const cmd of ['start','pause']){const b=document.querySelector(`[data-clock-action="${id}:${cmd}"]`);if(b)b.disabled=cmd==='start'?isRunning:!isRunning}}
  if(!mainDraftDirty){$('mainSeconds').value=s.main.duration_seconds%60;$('mainMinutes').value=Math.floor(s.main.duration_seconds/60);$('mainDirection').value=s.main.direction}
  if(!shotDraftDirty)$('shotSeconds').value=s.shot.duration_seconds;
  syncDurationPresets();
  $('shotAutoHide').checked=!!s.shot_auto_hide;
  $('shotVisibilityHint').textContent=s.shot_auto_hide && s.shot_visible===false ? 'Shot clock hidden on OBS overlay (match time ≤ shot time).' : '';
  if(!networkDirty){$('networkLan').checked=!/^127\.0\.0\.1:|^localhost:/.test(s.listen);$('networkPort').value=s.listen.split(':').pop()}
  const enabled=$('networkLan').checked;
  $('lanExplanation').textContent=enabled?'ON — trusted LAN devices can connect after restart':'OFF — only this computer can connect';
  $('networkRestart').classList.toggle('hidden',!s.restart_required);
  updateNetworkDisplay();
  $('saveNetwork').disabled=!networkDirty;
  $('unsavedBadge').classList.toggle('hidden',!dirty);
  const port=(s.active_listen||s.listen).split(':').pop();$('overlayUrl').textContent=`http://127.0.0.1:${port}/overlay`;
  updateBuilder();
  backgroundEditor?.sync();elementEditor?.sync();
  ocrControls.sync(s);syncDisplay();
  window.refreshTouchOptions?.();
 }
 const pageNames={control:'Live control',editor:'Layout editor',setup:'Output & API'};
 const compactNavigation=matchMedia('(max-width:720px)');
 let navigationHasFocus=false;
 document.addEventListener('focusin',event=>{navigationHasFocus=$('sectionNavigation').contains(event.target)});
 function closeNavigation(restoreFocus=false){
  $('sectionNavigation').classList.remove('menu-open');
  $('navigationToggle').setAttribute('aria-expanded','false');
  if(restoreFocus)$('navigationToggle').focus();
 }
 function setTab(target){
  if(!Object.hasOwn(pageNames,target))return;
  if(target!==tab)elementEditor?.exitTransform();
  const fromMenu=compactNavigation.matches&&$('sectionNavigation').classList.contains('menu-open');
  tab=target;
  document.querySelectorAll('[data-tab]').forEach(b=>{
   b.classList.toggle('active',b.dataset.tab===target);
   if(b.dataset.tab===target)b.setAttribute('aria-current','page');else b.removeAttribute('aria-current');
  });
  $('currentPage').textContent=pageNames[target];
  document.querySelectorAll('.view').forEach(v=>v.classList.toggle('hidden',v.id!=='tab-'+target));
  closeNavigation(fromMenu);
  if(s)requestAnimationFrame(()=>{stage.scale($('previewStage'));stage.scale($('editorStage'))});
 }
 $('navigationToggle').addEventListener('click',()=>{
  const open=$('sectionNavigation').classList.toggle('menu-open');
  $('navigationToggle').setAttribute('aria-expanded',String(open));
 });
 $('sectionNavigation').addEventListener('keydown',event=>{
  if(event.key==='Escape'){closeNavigation(true);event.preventDefault();}
 });
 document.addEventListener('pointerdown',event=>{if(!$('sectionNavigation').contains(event.target))closeNavigation()});
 compactNavigation.addEventListener('change',()=>{
  // Browsers may blur the newly hidden control before this callback runs.
  const restore=navigationHasFocus;
  closeNavigation(compactNavigation.matches&&restore);
  if(!compactNavigation.matches&&restore)document.querySelector('[data-tab].active')?.focus();
 });
 document.querySelectorAll('[data-tab],[data-tab-link]').forEach(b=>b.addEventListener('click',()=>setTab(b.dataset.tab||b.dataset.tabLink)));
 document.querySelectorAll('[data-adjust]').forEach(b=>b.addEventListener('click',()=>{const [field,n]=b.dataset.adjust.split(':');action('/api/adjust',{field,delta:Number(n)})}));
 document.querySelectorAll('[data-clock-action]').forEach(b=>b.addEventListener('click',()=>{const [id,act]=b.dataset.clockAction.split(':');action(`/api/clock/${id}/${act}`)}));
 document.querySelectorAll('[data-exact]').forEach(el=>el.addEventListener('click',()=>{const field=el.dataset.exact;if(field==='period'&&s?.period_overtime){message('Switch off OT to edit the numeric period.');return}const current=s?.[field];const raw=prompt(`Set ${field.replaceAll('_',' ')} (current: ${current})`,String(current??0));if(raw===null)return;const n=Number(raw);if(!Number.isSafeInteger(n)||n<0){message('Enter a valid nonnegative whole number.');return}action('/api/game',{field,value:n})}));
 document.querySelectorAll('[data-clock-adjust]').forEach(b=>b.addEventListener('click',()=>{const [id,n]=b.dataset.clockAdjust.split(':');action(`/api/clock/${id}/adjust`,{seconds:Number(n)})}));
 document.querySelectorAll('[data-clock-set]').forEach(b=>b.addEventListener('click',async()=>{
  const id=b.dataset.clockSet;
  const m=Number($('mainMinutes').value), ss=Number($('mainSeconds').value);
  if(id==='main'&&(!Number.isSafeInteger(m)||m<0||!Number.isSafeInteger(ss)||ss<0||ss>59)){message('Minutes must be ≥ 0; seconds must be 0–59.');return}
  const seconds=id==='main'?m*60+ss:Number($('shotSeconds').value);
  const dir=id==='main'?$('mainDirection').value:'down';
  if(!Number.isSafeInteger(seconds)||seconds<1||(id==='shot'&&seconds>3600)||seconds>7*86400){message('Duration must be at least 1 second and within the clock limit.');return}
  if(await action(`/api/clock/${id}/set`,{seconds,direction:dir})){if(id==='main')mainDraftDirty=false;else shotDraftDirty=false;draw()}
 }));
 document.querySelectorAll('[data-shot-preset]').forEach(b=>b.addEventListener('click',async()=>{if(await action('/api/clock/shot/set',{seconds:Number(b.dataset.shotPreset),direction:'down'})){shotDraftDirty=false;draw()}}));
 // These shortcuts edit pending setup only, including while the clock follows OCR.
 function syncDurationPresets(){
  const minutes=$('mainMinutes').value,seconds=$('mainSeconds').value;
  for(const button of document.querySelectorAll('[data-main-duration]')){
   const matches=minutes.trim()!==''&&seconds.trim()!==''&&Number(minutes)===Number(button.dataset.mainDuration)&&Number(seconds)===0;
   button.setAttribute('aria-pressed',String(matches));
  }
 }
 document.querySelectorAll('[data-main-duration]').forEach(button=>button.addEventListener('click',()=>{
  $('mainMinutes').value=button.dataset.mainDuration;$('mainSeconds').value=0;mainDraftDirty=true;syncDurationPresets();
 }));
 // Keep draft values untouched by polling until explicitly applied; 0 minutes is valid.
 for(const id of ['mainMinutes','mainSeconds','mainDirection','shotSeconds']){
  $(id).addEventListener('input',()=>{if(id==='shotSeconds')shotDraftDirty=true;else mainDraftDirty=true;syncDurationPresets()});
  $(id).addEventListener('change',()=>{if(id==='shotSeconds')shotDraftDirty=true;else mainDraftDirty=true;syncDurationPresets()});
 }
 function stepInput(id,delta){
  const input=$(id);if(!input)return;
  let value=Number(input.value);if(!Number.isFinite(value))value=0;
  if(id==='mainSeconds'||id==='builderSeconds'){
   const minuteID=id==='mainSeconds'?'mainMinutes':'builderMinutes';
   let m=Number($(minuteID).value);if(!Number.isFinite(m))m=0;
   const max=id==='mainSeconds'?7*86400:3600;
   const total=Math.max(0,Math.min(max,Math.round(m)*60+Math.round(value)+delta));
   $(minuteID).value=Math.floor(total/60);input.value=total%60;
  }else{
   const min=id==='shotSeconds'?1:0;const max=id==='shotSeconds'?3600:10079;
   input.value=Math.min(max,Math.max(min,Math.round(value)+delta));
  }
  if(id.startsWith('builder'))updateBuilder();
  else if(id==='shotSeconds')shotDraftDirty=true;
  else mainDraftDirty=true;
  input.dispatchEvent(new Event('change',{bubbles:true}));
 }
 document.querySelectorAll('[data-step-input]').forEach(b=>b.addEventListener('click',()=>{const [id,delta]=b.dataset.stepInput.split(':');stepInput(id,Number(delta));}));
 // Touch equivalents of native number spinners: retain each input's own
 // step/min/max and its existing draft/validation listeners. No API action.
 document.querySelectorAll('[data-number-step]').forEach(b=>b.addEventListener('click',()=>{
  const [id,delta]=b.dataset.numberStep.split(':'),input=$(id);
  if(Number(delta)>0)input.stepUp();else input.stepDown();
  input.dispatchEvent(new Event('input',{bubbles:true}));
  input.dispatchEvent(new Event('change',{bubbles:true}));
 }));
 $('periodOT').addEventListener('change',()=>action('/api/game',{field:'period_overtime',value:$('periodOT').checked}));
 const periodFormats=[...document.querySelectorAll('[data-period-format]')];
 for(const button of periodFormats){
  button.addEventListener('click',()=>action('/api/game',{field:'period_format',value:button.dataset.periodFormat}));
  button.addEventListener('keydown',event=>{
   if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','Home','End'].includes(event.key))return;
   event.preventDefault();const index=periodFormats.indexOf(button),delta=['ArrowLeft','ArrowUp'].includes(event.key)?-1:1;
   const next=periodFormats[event.key==='Home'?0:event.key==='End'?periodFormats.length-1:(index+delta+periodFormats.length)%periodFormats.length];
   next.focus({preventScroll:true});next.click();
  });
 }
 $('shotAutoHide').addEventListener('change',()=>action('/api/game',{field:'shot_auto_hide',value:$('shotAutoHide').checked}));
 [['homeName','home_name'],['awayName','away_name']].forEach(([id,key])=>{$(id).addEventListener('change',()=>{let v=$(id).value.trim();if(v)action('/api/game',{field:key,value:v});else message('Team name cannot be empty')})});
 $('resetMatch').addEventListener('click',()=>{if(confirm('Reset BOTH scores, fouls, and period to initial values? Clocks will not be changed.'))action('/api/reset-game')});
 // Touch layout adjustment: deliberate pixel increments, not native number spinners.
 let nudgeSize=5;
 const elementBounds={elementX:[0,1920],elementY:[0,1080],elementSize:[12,240]};
 function stepElement(id,delta){
  if(!layout||!Object.hasOwn(elementBounds,id))return;
  const input=$(id),[min,max]=elementBounds[id];
  const raw=Number(input.value);
  const value=Math.max(min,Math.min(max,Math.round((Number.isFinite(raw)?raw:min)+delta)));
  input.value=String(value);
  input.dispatchEvent(new Event('change',{bubbles:true}));
 }
 document.querySelectorAll('[data-element-step]').forEach(b=>b.addEventListener('click',()=>{
  const [id,direction]=b.dataset.elementStep.split(':');
  // Numeric steppers stay precise; the selected step belongs to the arrow pad.
  stepElement(id,Number(direction));
 }));
 document.querySelectorAll('[data-nudge-size]').forEach(b=>b.addEventListener('click',()=>{
  nudgeSize=Number(b.dataset.nudgeSize);
  document.querySelectorAll('[data-nudge-size]').forEach(x=>{x.classList.toggle('active',x===b);x.setAttribute('aria-pressed',String(x===b))});
 }));
 document.querySelectorAll('[data-nudge]').forEach(b=>b.addEventListener('click',()=>{
  const direction=b.dataset.nudge;
  stepElement(direction==='left'||direction==='right'?'elementX':'elementY',nudgeSize*(direction==='left'||direction==='up'?-1:1));
 }));
 // All controls below edit a temporary layout until the operator chooses Save.
 function mark(){layoutRevision++;dirty=true;$('unsavedBadge').classList.remove('hidden');if(s){stage.paint($('editorStage'),s,layout,editorSelection(),dragging?.id);stage.scale($('editorStage'));elementEditor?.sync()}}
 const fieldPills=$('fieldPills');for(const id of ['main_clock','shot_clock','period','home_name','home_score','home_fouls','away_name','away_score','away_fouls']){const b=document.createElement('button');b.textContent=names[id];b.dataset.field=id;b.addEventListener('click',()=>selectField(id));fieldPills.append(b)}
 function selectField(id){if(!layout||!layout.elements[id])return;backgroundEditor?.select(false);selected=id;updateInspector();if(s)stage.paint($('editorStage'),s,layout,editorSelection(),dragging?.id);elementEditor?.sync()}
 function updateInspector(){if(!layout)return;const el=layout.elements[selected];if(!el)return;
  fieldPills.querySelectorAll('button').forEach(b=>b.classList.toggle('selected',b.dataset.field===selected));$('selectedTitle').textContent=names[selected];
  $('elementVisible').checked=el.visible;$('elementX').value=el.x;$('elementY').value=el.y;$('elementFont').value=el.font;$('elementSize').value=el.size;$('elementAlign').value=el.align;$('elementColor').value=el.color;
  $('backgroundName').textContent=layout.background ? 'Image: '+layout.background.slice(0,10)+'…' : 'No background loaded';
  window.refreshTouchOptions?.();
 }
 function change(prop,value){if(!layout)return;const el=layout.elements[selected];el[prop]=value;mark()}
 [['elementX','x',0,1920],['elementY','y',0,1080],['elementSize','size',12,240]].forEach(([id,prop,min,max])=>{
  $(id).addEventListener('change',()=>{const v=Number($(id).value);if(!Number.isFinite(v)){updateInspector();return};const n=Math.round(Math.min(max,Math.max(min,v)));$(id).value=n;change(prop,n)})
 });
 $('elementVisible').addEventListener('change',()=>change('visible',$('elementVisible').checked));
 [['elementFont','font'],['elementAlign','align'],['elementColor','color']].forEach(([id,prop])=>$(id).addEventListener('change',()=>change(prop,$(id).value)));
 // Live appearance updates are serialized and never commit the editor draft.
 function syncDisplay(){
  if(!s)return;
  for(const [id,key] of Object.entries(displayFields)){
   if(id==='foulDotsMax'&&dotsDirty)continue;
   $(id).value=displayDrafts.has(key)?displayDrafts.get(key):s.layout[key];
  }
  $('displayStatus').textContent=displayBusy?'Saving display options…':'';
 }
 function setDisplay(field,value){
  displayDrafts.set(field,value);displayPending.set(field,value);
  if(displayBusy){syncDisplay();return displayWait}
  displayBusy=true;syncDisplay();
  displayWait=(async()=>{
   while(displayPending.size){
    if(opBusy||layoutSaveBusy||ocrPending){await new Promise(resolve=>setTimeout(resolve,30));continue}
    const [key,next]=displayPending.entries().next().value;displayPending.delete(key);
    const ok=await action('/api/display',{field:key,value:next});
    if(!displayPending.has(key)){
     displayDrafts.delete(key);
     if(key==='foul_dots_max'&&ok&&$('foulDotsMax').value===String(next))dotsDirty=false;
    }
    syncDisplay();window.refreshTouchOptions?.();
   }
  })().finally(()=>{displayBusy=false;syncDisplay()});
  return displayWait;
 }
 for(const [id,key] of Object.entries(displayFields))if(id!=='foulDotsMax')$(id).addEventListener('change',()=>setDisplay(key,$(id).value));
 $('foulDotsMax').addEventListener('input',()=>{dotsDirty=true;$('foulDotsMax').removeAttribute('aria-invalid')});
 $('foulDotsMax').addEventListener('change',()=>{
  const n=Number($('foulDotsMax').value);dotsDirty=true;
  if(!Number.isInteger(n)||n<1||n>20){$('foulDotsMax').setAttribute('aria-invalid','true');message('Maximum dots per team must be a whole number from 1 to 20.');return}
  $('foulDotsMax').removeAttribute('aria-invalid');setDisplay('foul_dots_max',n);
 });
 document.querySelectorAll('[data-display-step]').forEach(button=>button.addEventListener('click',()=>{
  const input=$('foulDotsMax'),value=Number(input.value),delta=Number(button.dataset.displayStep.split(':')[1]);
  if(!input.value.trim()||!Number.isInteger(value)){message('Enter a valid maximum dot count first.');return}
  input.value=Math.max(1,Math.min(20,value+delta));input.dispatchEvent(new Event('input'));input.dispatchEvent(new Event('change'));
 }));
 const editor=$('editorStage');
 document.addEventListener('keydown',ev=>{if(tab!=='editor'||!layout||!['ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(ev.key))return;
  if(ev.defaultPrevented||$('touchChoiceDialog').open||['INPUT','SELECT','TEXTAREA','BUTTON'].includes(document.activeElement?.tagName))return;
  ev.preventDefault();const step=ev.shiftKey?10:1;
  if(backgroundEditor.selected){backgroundEditor.nudge(ev.key==='ArrowLeft'?-step:ev.key==='ArrowRight'?step:0,ev.key==='ArrowUp'?-step:ev.key==='ArrowDown'?step:0);return}
  const e=layout.elements[selected];
  if(ev.key==='ArrowUp')e.y=Math.max(0,e.y-step);if(ev.key==='ArrowDown')e.y=Math.min(1080,e.y+step);
  if(ev.key==='ArrowLeft')e.x=Math.max(0,e.x-step);if(ev.key==='ArrowRight')e.x=Math.min(1920,e.x+step);
  updateInspector();mark();
 });
 backgroundEditor=window.createBackgroundEditor({getLayout:()=>layout,mark,message});
 elementEditor=window.createElementEditor({getLayout:()=>layout,getSelected:editorSelection,selectField,mark,updateInspector,message,names});
 editor.addEventListener('backgroundselection',()=>{if(s)stage.paint(editor,s,layout,editorSelection(),dragging?.id);elementEditor.sync()});
 document.querySelector('.inspector').addEventListener('focusin',()=>{if(backgroundEditor.selected)backgroundEditor.select(false)});
 document.addEventListener('keydown',event=>{if(event.key==='Escape'&&tab==='editor'&&!$('touchChoiceDialog').open)backgroundEditor.select(false)});
 async function saveLayout(){
  await displayWait;
  if(!layout||layoutSaveBusy||!backgroundEditor.commitDrafts()||!elementEditor.commitDrafts())return false;
  const revision=layoutRevision,payload=fullLayout();layoutSaveBusy=true;$('saveLayout').disabled=true;
  try{
   const updated=await api('/api/layout?preserve_display=1','PUT',payload);s=updated;
   if(layoutRevision===revision){layout=JSON.parse(JSON.stringify(s.layout));dirty=false;backgroundEditor.resetDrafts();elementEditor.resetDrafts();updateInspector();draw();message('Layout saved for OBS.',true);return true}
   draw();message('Layout saved. Newer edits are still unsaved.',true);return false;
  }catch(err){message(err.message);return false}
  finally{layoutSaveBusy=false;$('saveLayout').disabled=false}
 }
 $('saveLayout').addEventListener('click',saveLayout);
 $('discardLayout').addEventListener('click',()=>{if(dirty&&!confirm('Discard unsaved element positions and appearance?'))return;layout=JSON.parse(JSON.stringify(s.layout));dirty=false;backgroundEditor.resetDrafts();elementEditor.resetDrafts();updateInspector();draw()});
 $('resetPositions').addEventListener('click',()=>{if(!confirm('Restore default positions and font styles? Your imported graphic will be kept.'))return;
  // The defaults are constant and ship embedded as data from the server; do not lose current background or foul/clock settings.
  const defaults={period:[95,62,54],main_clock:[305,52,70],shot_clock:[670,62,54],home_name:[920,74,50],home_score:[1175,49,90],away_score:[1400,49,90],away_name:[1625,74,50],home_fouls:[1135,175,32],away_fouls:[1390,175,32]};
  for(const [id,[x,y,size]] of Object.entries(defaults)){Object.assign(layout.elements[id],{x,y,size});delete layout.elements[id].transform}elementEditor.resetDrafts();updateInspector();mark();
 });
 $('importBackground').addEventListener('click',()=>$('backgroundFile').click());
 $('backgroundFile').addEventListener('change',async ev=>{
  const file=ev.target.files[0];if(!file)return;
  if(file.size>15*1024*1024){message('Background exceeds 15 MB.');ev.target.value='';return}
  $('importBackground').disabled=true;
  try{
   const r=await fetch('/api/background?draft=1',{method:'POST',headers:token?{Authorization:`Bearer ${token}`}:{},body:file});
   const v=await r.json();if(!r.ok)throw Error(v.error||'Upload failed');
   if(!layout)layout=JSON.parse(JSON.stringify(v.state.layout));
   layout.background=v.background;layout.background_transform=v.background_transform;s=v.state;
   backgroundEditor.resetDrafts();backgroundEditor.select(false);mark();draw();
   message('Graphic imported to the editor. Save layout to apply it to OBS.',true);
  }catch(err){message(err.message)}finally{ev.target.value='';$('importBackground').disabled=false}
 });
 $('removeBackground').addEventListener('click',()=>{
  if(!layout?.background||!confirm('Remove the graphic from this layout draft? Save layout to apply.'))return;
  layout.background='';delete layout.background_transform;backgroundEditor.resetDrafts();backgroundEditor.select(false);mark();draw();
 });
 async function refreshProfiles(){try{const x=await api('/api/profiles');const selected=$('profileSelect').value;$('profileSelect').replaceChildren(new Option('Select a saved profile',''));for(const name of x.profiles)$('profileSelect').add(new Option(name,name));$('profileSelect').value=x.profiles.includes(selected)?selected:'';window.refreshTouchOptions?.()}catch(err){message(err.message)}}
 $('saveProfile').addEventListener('click',async()=>{await displayWait;const name=$('profileName').value.trim();if(!name){message('Enter a preset name.');return}if(dirty&&!await saveLayout())return;try{await api('/api/profiles','POST',{name,action:'save'});await refreshProfiles();$('profileSelect').value=name;window.refreshTouchOptions?.();message('Preset saved.',true)}catch(err){message(err.message)}});
 $('loadProfile').addEventListener('click',async()=>{await displayWait;const name=$('profileSelect').value;if(!name)return;if(dirty&&!confirm('Discard unsaved changes and load the preset?'))return;try{s=await api('/api/profiles','POST',{name,action:'load'});layout=JSON.parse(JSON.stringify(s.layout));dirty=false;backgroundEditor.resetDrafts();backgroundEditor.select(false);elementEditor.resetDrafts();updateInspector();draw();message('Preset loaded.',true)}catch(err){message(err.message)}});
 $('deleteProfile').addEventListener('click',async()=>{const name=$('profileSelect').value;if(!name||!confirm(`Delete saved preset “${name}”?`))return;try{await api('/api/profiles','POST',{name,action:'delete'});await refreshProfiles();message('Preset removed.',true)}catch(err){message(err.message)}});
 function overlayUrl(){return $('overlayUrl').textContent}
 $('openOverlay').addEventListener('click',()=>window.open(overlayUrl(),'field_scoreboard_overlay','noopener'));
 $('copyOverlay').addEventListener('click',()=>copyText(overlayUrl(),'Local OBS overlay URL'));
 $('copyNetworkOverlay').addEventListener('click',()=>{
  if($('copyNetworkOverlay').disabled)return;
  copyText($('networkOverlayUrl').textContent,'Network OBS overlay URL');
 });
 // Local API token operations live under the OBS output card for easy discovery.
 $('copyApiToken').addEventListener('click',async()=>{
  try{
   const response=await api('/api/token');
   builderToken=response.token;
   updateBuilder();
   await copyText(response.token,'Local API token');
  }catch(err){message(err.message)}
 });
 $('rotateApiToken').addEventListener('click',async()=>{
  if(!confirm('Regenerate the API token? All existing Companion requests and remote control sessions using the old token will stop working immediately. Continue?'))return;
  try{
   const response=await api('/api/token/rotate','POST');
   builderToken=response.token;
   token=response.token;
   sessionStorage.setItem('field_scoreboard_api_token',token);
   updateBuilder();
   message('API token regenerated. Update the Authorization header in every existing Companion button.',true);
  }catch(err){message(err.message)}
 });
 // The server listens on a wildcard address when LAN is enabled, but remote
 // Companion URLs must always use a real, detected private network address.
 const currentPort=()=>String($('networkPort').value.trim()||'8790');
 const lanHost=()=>selectedIP || '';
 function updateNetworkDisplay(){
  const port=currentPort();
  $('localURL').textContent=`http://127.0.0.1:${port}`;
  $('lanURL').textContent=lanHost()?`http://${lanHost()}:${port}`:'No private IPv4 detected';
  $('copyLanURL').disabled=!lanHost()||!$('networkLan').checked;
  const active=s?.active_listen||s?.listen||'127.0.0.1:8790';
  const activeLAN=active.startsWith('0.0.0.0:');
  const activePort=active.split(':').pop();
  $('networkOverlayUrl').textContent=activeLAN&&lanHost()
    ?`http://${lanHost()}:${activePort}/overlay`
    :'Enable LAN access, save and restart';
  $('copyNetworkOverlay').disabled=!(activeLAN&&lanHost());
  $('remoteOverlayHint').textContent=activeLAN
    ?'Read-only overlay over your trusted LAN; score and clock controls still require an API token.'
    :'Available after enabling LAN access, saving network settings and restarting Field Scoreboard.';
 }
 async function refreshInterfaces(){
  try{
   const r=await api('/api/network-interfaces');
   detectedInterfaces=Array.isArray(r.interfaces)?r.interfaces:[];
   const current=selectedIP;
   const found=detectedInterfaces.find(x=>x.ip===current);
   selectedIP=found?found.ip:(r.preferred_ip||detectedInterfaces[0]?.ip||'');
   const options=detectedInterfaces.length?detectedInterfaces.map(x=>new Option(`${x.name} · ${x.ip}${x.preferred?' (preferred)':''}`,x.ip)):[new Option('No private IPv4 found','')];
   $('adapterSelect').replaceChildren(...options);$('adapterSelect').value=selectedIP;
   if(!builderHostDirty && selectedIP)$('builderHost').value=`${selectedIP}:${(s?.active_listen||s?.listen||'127.0.0.1:8790').split(':').pop()}`;
   updateNetworkDisplay();updateBuilder();
  }catch(err){$('adapterSelect').replaceChildren(new Option('Detection available on the host only',''));selectedIP='';updateNetworkDisplay();message(err.message)}
 }
 $('refreshAdapters').addEventListener('click',refreshInterfaces);
 $('adapterSelect').addEventListener('change',()=>{selectedIP=$('adapterSelect').value;updateNetworkDisplay();if(!builderHostDirty)useSelectedIP()});
 function useSelectedIP(){if(!selectedIP){message('Select a private LAN adapter on the Field Scoreboard computer.');return}
  $('builderHost').value=`${selectedIP}:${(s?.active_listen||s?.listen||'127.0.0.1:8790').split(':').pop()}`;builderHostDirty=false;updateBuilder()}
 $('useAdapterIP').addEventListener('click',useSelectedIP);
 $('networkLan').addEventListener('change',()=>{networkDirty=true;$('saveNetwork').disabled=false;updateNetworkDisplay();$('lanExplanation').textContent=$('networkLan').checked?'ON — save and restart to allow LAN devices':'OFF — save and restart for localhost-only access'});
 $('networkPort').addEventListener('input',()=>{networkDirty=true;$('saveNetwork').disabled=false;updateNetworkDisplay()});
 $('saveNetwork').addEventListener('click',async()=>{
  const port=Number($('networkPort').value);
  if(!Number.isSafeInteger(port)||port<1024||port>65535){message('Port must be between 1024 and 65535.');return}
  const listen=`${$('networkLan').checked?'0.0.0.0':'127.0.0.1'}:${port}`;
  try{
   const next=await api('/api/network','PUT',{listen});s=next;networkDirty=false;draw();
   message(s.restart_required?'Network saved. Exit and restart Field Scoreboard to apply.':'Network settings saved.',true);
  }catch(err){message(err.message)}
 });
 async function copyText(value,description){
  try{
   if(navigator.clipboard?.writeText){await navigator.clipboard.writeText(value);message(`${description} copied.`,true);return}
  }catch(_){/* On HTTP LAN pages, Clipboard API may require HTTPS. */}
  // A user-gesture fallback for browsers on trusted, non-HTTPS LAN origins.
  const field=document.createElement('textarea');field.value=value;
  Object.assign(field.style,{position:'fixed',top:'-9999px',left:'0',opacity:'0'});
  document.body.append(field);field.focus();field.select();
  let worked=false;
  try{worked=document.execCommand('copy')}catch(_){}
  field.remove();
  if(worked)message(`${description} copied.`,true);
  else message('Clipboard blocked by this browser. Copy the displayed value manually.');
 }
 [['copyLanURL','lanURL'],['copyLocalURL','localURL']].forEach(([btn,id])=>$(btn).addEventListener('click',()=>copyText($(id).textContent,id==='lanURL'?'LAN URL':'Local URL')));

 // Generate request fields for Generic HTTP Requests. No separate module.
 const bParams=['builderClockFields','builderDeltaLabel','builderPeriodLabel','builderNameLabel'];
 function requestSpec(){
  const kind=$('builderAction').value;
  const [group,name,part]=kind.split(':');
  let path='',body=null,method='POST';
  if(group==='state'){path='/api/state';method='GET'}
  else if(group==='both'||group==='main'||group==='shot'){
   path=`/api/clock/${group}/${name}`;
   if(name==='set'){
    const m=Number($('builderMinutes').value),seconds=Number($('builderSeconds').value),total=m*60+seconds;
    if(!Number.isSafeInteger(m)||m<0||!Number.isSafeInteger(seconds)||seconds<0||seconds>59||total<1||(group==='shot'&&total>3600)||total>7*86400)throw Error('Enter a valid duration (minimum 1 second).');
    body={seconds:total,direction:group==='shot'?'down':$('builderDirection').value};
   }
   if(name==='adjust'){
    const seconds=Number($('builderDelta').value);
    if(!Number.isSafeInteger(seconds)||seconds===0||Math.abs(seconds)>7*86400)throw Error('Enter a nonzero signed adjustment in seconds.');body={seconds};
   }
  }
  else if(group==='score'||group==='fouls'){
   path='/api/adjust';body={field:`${name}_${group==='score'?'score':'fouls'}`,delta:Number(part)};
  }
  else if(group==='period'){
   if(name==='set'){
    const v=Number($('builderPeriod').value);if(!Number.isSafeInteger(v)||v<1||v>20)throw Error('Period must be 1–20.');
    path='/api/game';body={field:'period',value:v};
   }else{path='/api/adjust';body={field:'period',delta:Number(name)}}
  }
  else if(group==='name'){
   const v=$('builderTeamName').value.trim();if(!v||[...v].length>32)throw Error('Team name must be 1–32 characters.');
   path='/api/game';body={field:`${name}_name`,value:v};
  }
  else if(group==='ot'||group==='shotvisibility'){
   path='/api/game';body={field:group==='ot'?'period_overtime':'shot_auto_hide',value:name==='on'};
  }
  else if(group==='game'&&name==='reset')path='/api/reset-game';
  else throw Error('Unknown Companion command');
  const host=$('builderHost').value.trim().replace(/^https?:\/\//,'').replace(/\/+$/,'');
  if(!host||/[\/\s?#]/.test(host))throw Error('Enter a valid Field Scoreboard host IP and port.');
  const url=`http://${host}${path}`;
  return {method,url,path,body};
 }
 let lastBuilderSpec=null;
 function updateBuilder(){
  const kind=$('builderAction').value,group=kind.split(':')[0],name=kind.split(':')[1];
  const needClock=(group==='main'||group==='shot')&&name==='set';
  const needDelta=(group==='main'||group==='shot')&&name==='adjust';
  const needPeriod=group==='period'&&name==='set';const needName=group==='name';
  $('builderParameters').classList.toggle('hidden',!(needClock||needDelta||needPeriod||needName));
  for(const id of bParams)$(id).classList.toggle('hidden',!(id==='builderClockFields'?needClock:id==='builderDeltaLabel'?needDelta:id==='builderPeriodLabel'?needPeriod:needName));
  $('builderDirectionLabel').classList.toggle('hidden',group==='shot');
  $('builderMethod').textContent='POST';
  $('builderURL').textContent='—';$('builderBody').textContent='(empty)';
  $('builderHeaders').textContent=builderToken?'Authorization: Bearer •••••••• (loaded)':'Load local API token';
  $('tokenStatus').textContent=builderToken?'Token loaded locally':'Token not loaded';
  lastBuilderSpec=null;
  try{const spec=requestSpec();lastBuilderSpec=spec;$('builderMethod').textContent=spec.method;$('builderURL').textContent=spec.url;$('builderBody').textContent=spec.body?JSON.stringify(spec.body):'(empty)';}
  catch(err){$('builderURL').textContent=err.message}
 }
 $('builderHost').addEventListener('input',()=>{builderHostDirty=true;updateBuilder()});
 for(const id of ['builderAction','builderMinutes','builderSeconds','builderDirection','builderDelta','builderPeriod','builderTeamName']){
  $(id).addEventListener(id==='builderAction'?'change':'input',updateBuilder);
 }
 $('loadBuilderToken').addEventListener('click',async()=>{
  try{const v=await api('/api/token');builderToken=v.token;updateBuilder();message('Local API token loaded into Companion Builder.',true)}catch(err){message(err.message)}
 });
 function builderHeaders(){return {'Authorization':`Bearer ${builderToken}`}}
 document.querySelectorAll('[data-builder-copy]').forEach(b=>b.addEventListener('click',()=>{
  if(!lastBuilderSpec){message('Correct the Companion command fields first.');return}
  const key=b.dataset.builderCopy,sp=lastBuilderSpec;
  if(key==='headers'&&!builderToken){message('Load the API token locally first.');return}
  const value={method:sp.method,url:sp.url,body:sp.body?JSON.stringify(sp.body):'',headers:JSON.stringify(builderHeaders())}[key];
  copyText(value,`${key} value`);
 }));
 $('copyBuilderAll').addEventListener('click',()=>{
  if(!lastBuilderSpec||!builderToken){message('Choose a valid action and load the API token first.');return}
  const sp=lastBuilderSpec;
  copyText(`${sp.method} ${sp.url}\nHeaders (JSON): ${JSON.stringify(builderHeaders())}\nBody (JSON): ${sp.body?JSON.stringify(sp.body):'(empty)'}`,'Complete Companion request');
 });
 $('testBuilderRequest').addEventListener('click',async()=>{
  if(!lastBuilderSpec){message('Correct the request before testing.');return}
  const sp=lastBuilderSpec;
  if(sp.method!=='GET'&&!confirm(`Test ${$('builderAction').selectedOptions[0].textContent} on this running Field Scoreboard? This will change live game data.`))return;
  try{const result=await api(sp.path,sp.method,sp.body===null?undefined:sp.body);if(sp.method!=='GET'){s=result;draw()}message('Local API request succeeded.',true)}catch(err){message(err.message)}
 });
 $('authForm').addEventListener('submit',ev=>{ev.preventDefault();token=$('authToken').value.trim();sessionStorage.setItem('field_scoreboard_api_token',token);poll()});
 // One choice dialog at every viewport/pointer size. Native selects retain data
 // binding only; each visible trigger is the single keyboard entry point.
 (function setupTouchPickers(){
  const dialog=$('touchChoiceDialog'),title=$('touchChoiceHeading'),list=$('touchChoiceList');
  let source=null,returnFocus=null,optionSignature='',pointerStart=null,scrolled=false,outsideStart=false;
  let search='',searchTime=0;
  const triggers=new Map();
  const optionLabel=sel=>(sel.selectedOptions[0]?.textContent?.trim()||'Choose…')+(sel.id==='elementFont'?' · '+(layout?.elements[selected]?.bold?'Bold':'Regular'):'');
  const options=()=>[...list.querySelectorAll('button:not(:disabled)')];
  function focusOption(button){
   if(!button)return;
   for(const b of list.querySelectorAll('button'))b.tabIndex=b===button?0:-1;
   button.focus({preventScroll:true});button.scrollIntoView({block:'nearest'});
  }
  function renderChoices(){
   const signature=JSON.stringify([...source.options].map(o=>[o.textContent,o.value,o.selected,o.disabled,o.hidden,o.parentElement.disabled]));
   if(signature===optionSignature)return;
   optionSignature=signature;
   const focused=list.contains(document.activeElement)?document.activeElement.dataset.index:null;
   const scrollTop=list.scrollTop;
   list.replaceChildren();
   for(const [index,opt] of [...source.options].entries()){
    if(opt.hidden)continue;
    const b=document.createElement('button');
    b.type='button';b.className='touch-choice-option';b.dataset.index=String(index);
    b.textContent=opt.textContent.trim();b.disabled=source.disabled||opt.disabled||!!opt.parentElement.disabled;
    b.setAttribute('role','option');b.setAttribute('aria-selected',String(opt.selected));
    b.classList.toggle('selected',opt.selected);b.tabIndex=-1;
    b.addEventListener('click',event=>{
     // Native touch scrolling normally cancels clicks. Also reject drags on
     // browsers that synthesize a click after a moved/cancelled pointer.
     if(event.detail!==0&&scrolled){event.preventDefault();return;}
     source.selectedIndex=index;
     source.dispatchEvent(new Event('input',{bubbles:true}));
     source.dispatchEvent(new Event('change',{bubbles:true}));
     refresh();close();
    });
    list.append(b);
   }
   const next=options().find(b=>b.dataset.index===focused)||options().find(b=>b.getAttribute('aria-selected')==='true')||options()[0];
   if(next)next.tabIndex=0;
   list.scrollTop=scrollTop;
   if(focused!==null){if(next)focusOption(next);else $('touchChoiceClose').focus();}
  }
  function refresh(){
   const bold=!!layout?.elements[selected]?.bold;
   $('elementBold').setAttribute('aria-checked',String(bold));
   $('elementBold').querySelector('.font-weight-state').textContent=bold?'On':'Off';
   for(const [select,{trigger,label}] of triggers){
    const value=optionLabel(select),text=value+'  ▾';
    if(trigger.textContent!==text)trigger.textContent=text;
    trigger.setAttribute('aria-label',`${label}: ${value}`);
    trigger.disabled=select.disabled;
   }
   if(dialog.open&&source){if(source.disabled)close();else renderChoices();}
  }
  function close(){if(dialog.open)dialog.close()}
  $('elementBold').addEventListener('click',()=>{
   if(source?.id!=='elementFont'||!layout?.elements[selected])return;
   change('bold',!layout.elements[selected].bold);refresh();
  });
  $('touchChoiceClose').addEventListener('click',close);
  dialog.addEventListener('close',()=>{
   returnFocus?.setAttribute('aria-expanded','false');
   returnFocus?.focus({preventScroll:true});source=null;
  });
  dialog.addEventListener('keydown',event=>{
   if(event.key!=='Tab')return;
   const stops=[...dialog.querySelectorAll('button:not(:disabled):not([tabindex="-1"])')].filter(button=>button.getClientRects().length);
   const index=stops.indexOf(document.activeElement);
   event.preventDefault();
   stops[(index+(event.shiftKey?-1:1)+stops.length)%stops.length]?.focus();
  });
  const outside=event=>{const r=dialog.getBoundingClientRect();return event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom};
  dialog.addEventListener('pointerdown',event=>{outsideStart=event.target===dialog&&outside(event)});
  dialog.addEventListener('click',event=>{if(outsideStart&&event.target===dialog&&outside(event))close()});
  list.addEventListener('pointerdown',event=>{pointerStart={x:event.clientX,y:event.clientY};scrolled=false});
  list.addEventListener('pointermove',event=>{if(pointerStart&&Math.hypot(event.clientX-pointerStart.x,event.clientY-pointerStart.y)>8)scrolled=true});
  list.addEventListener('pointercancel',()=>{scrolled=true;pointerStart=null});
  list.addEventListener('scroll',()=>{if(pointerStart)scrolled=true});
  list.addEventListener('pointerup',()=>{pointerStart=null});
  list.addEventListener('keydown',event=>{
   const choices=options(),index=choices.indexOf(document.activeElement);
   let next=null;
   if(event.key==='ArrowDown')next=choices[Math.min(index+1,choices.length-1)];
   if(event.key==='ArrowUp')next=choices[Math.max(index-1,0)];
   if(event.key==='Home')next=choices[0];
   if(event.key==='End')next=choices.at(-1);
   if(event.key.length===1&&event.key!==' '&&!event.ctrlKey&&!event.metaKey&&!event.altKey){
    search=performance.now()-searchTime>700?event.key:search+event.key;searchTime=performance.now();
    const ordered=[...choices.slice(index+1),...choices.slice(0,index+1)];
    next=ordered.find(b=>b.textContent.toLocaleLowerCase().startsWith(search.toLocaleLowerCase()));
   }
   if(next){event.preventDefault();event.stopPropagation();focusOption(next);}
  });
  for(const select of document.querySelectorAll('select')){
   const labels=[...select.labels];
   const label=labels.map(el=>{
    const clone=el.cloneNode(true);clone.querySelectorAll('select,button,input').forEach(node=>node.remove());return clone.textContent.trim();
   }).join(' ')||'Choose option';
   select.classList.add('touch-select-native');select.hidden=true;select.tabIndex=-1;select.setAttribute('aria-hidden','true');
   const trigger=document.createElement('button');
   trigger.type='button';trigger.className='touch-select-trigger';trigger.id=select.id+'Choice';
   trigger.setAttribute('aria-haspopup','dialog');trigger.setAttribute('aria-controls',dialog.id);trigger.setAttribute('aria-expanded','false');
   select.after(trigger);
   for(const el of labels)el.htmlFor=trigger.id;
   select.addEventListener('change',refresh);
   new MutationObserver(refresh).observe(select,{childList:true,subtree:true,characterData:true,attributes:true,attributeFilter:['disabled','hidden','selected','label','value']});
   triggers.set(select,{trigger,label});
   trigger.addEventListener('click',event=>{
    event.preventDefault();event.stopPropagation();source=select;returnFocus=trigger;
    title.textContent=label;optionSignature='';search='';scrolled=false;pointerStart=null;
    $('fontWeightRow').hidden=select.id!=='elementFont';
    renderChoices();dialog.showModal();trigger.setAttribute('aria-expanded','true');
    focusOption(list.querySelector('[tabindex="0"]'));
   });
  }
  window.refreshTouchOptions=refresh;refresh();
 })();
 const observer=new ResizeObserver(()=>{stage.scale($('previewStage'));stage.scale($('editorStage'))});observer.observe($('previewStage').parentElement);observer.observe($('editorStage').parentElement);
 stage.initialize($('previewStage'));stage.initialize($('editorStage'));
 setTab('control');poll().then(()=>{refreshProfiles();refreshInterfaces();updateBuilder()});setInterval(poll,250);
})();
