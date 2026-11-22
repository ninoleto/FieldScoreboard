'use strict';
// Browser-only viewing preferences. No API writes, clock actions or editor
// selection handlers: the single read-only stage uses the existing renderer.
window.FieldFloatingPreview={create({getView}){
 const $=id=>document.getElementById(id),storageKey='field_scoreboard_floating_preview_v1';
 const defaults=()=>({enabled:false,width:320,x:1,y:1});
 const clamp=(n,min,max)=>Math.max(min,Math.min(max,n));
 let prefs={control:defaults(),editor:defaults()},frame=0,gesture=null,previousFocus=null;
 try{
  const saved=JSON.parse(localStorage.getItem(storageKey)||'{}');
  for(const tab of ['control','editor']){
   const p=saved?.[tab];if(!p||typeof p!=='object')continue;
   prefs[tab].enabled=p.enabled===true;
   for(const key of ['width','x','y'])if(typeof p[key]==='number'&&Number.isFinite(p[key]))prefs[tab][key]=clamp(p[key],key==='width'?160:0,key==='width'?640:1);
  }
 }catch(_){/* Storage may be disabled, full or contain an older invalid value. */}
 const box=document.createElement('aside');box.id='floatingPreview';box.hidden=true;box.setAttribute('aria-label','Floating scoreboard preview');
 box.innerHTML=`<div class="floating-heading"><button id="floatingMove" type="button" aria-describedby="floatingMoveHelp"><span id="floatingTitle">Live preview</span> <span aria-hidden="true">✥</span></button><button id="floatingClose" type="button" aria-label="Disable floating preview">×</button></div>
 <div id="floatingFrame" class="stage-frame"><div id="floatingStage" class="stage" role="img" aria-label="Read-only scoreboard preview"></div></div>
 <div class="floating-toolbar" role="group" aria-label="Preview size"><button type="button" data-floating-size="320" aria-label="Preview 320 by 180">320</button><button type="button" data-floating-size="480" aria-label="Preview 480 by 270">480</button><button type="button" data-floating-size="640" aria-label="Preview 640 by 360">640</button><button id="floatingResize" type="button" aria-label="Resize preview" aria-describedby="floatingResizeHelp">↘</button></div>
 <span id="floatingMoveHelp" class="floating-help">Drag to move. Arrow keys move 10 pixels; Shift moves 1 pixel. Home returns to the bottom right.</span>
 <span id="floatingResizeHelp" class="floating-help">Drag to resize at 16:9. Right or Down grows; Left or Up shrinks. Shift changes by 1 pixel. Home selects 320 by 180.</span>`;
 document.body.append(box);
 const stage=$('floatingStage'),move=$('floatingMove'),resize=$('floatingResize');
 window.FieldStage.initialize(stage);
 const viewport=()=>{const v=window.visualViewport;return {left:v?.offsetLeft||0,top:v?.offsetTop||0,width:v?.width||innerWidth,height:v?.height||innerHeight}};
 function store(){try{localStorage.setItem(storageKey,JSON.stringify(prefs))}catch(_){}}
 function syncSwitches(){for(const tab of ['control','editor'])$('floating-'+tab+'-enabled').checked=prefs[tab].enabled}
 function inView(node){const r=node?.getBoundingClientRect(),v=viewport();return r&&r.width>0&&r.height>0&&r.bottom>v.top&&r.top<v.top+v.height&&r.right>v.left&&r.left<v.left+v.width}
 function restoreFocus(){
  if(!box.contains(document.activeElement))return;
  const target=inView(previousFocus)&&!previousFocus.disabled?previousFocus:[...document.querySelectorAll('.view:not(.hidden) button,.view:not(.hidden) input')].find(e=>!e.disabled&&inView(e));
  target?.focus({preventScroll:true});
 }
 function hide(){restoreFocus();box.hidden=true;gesture=null}
 function geometry(p){
  const v=viewport(),margin=8;
  // Measure chrome at the desired width, including its narrow-window wrapping.
  box.style.width=Math.min(p.width,Math.max(1,v.width-2*margin))+'px';
  const chrome=box.querySelector('.floating-heading').offsetHeight+box.querySelector('.floating-toolbar').offsetHeight;
  const maxWidth=Math.max(1,Math.min(640,v.width-2*margin,(v.height-2*margin-chrome)*16/9));
  const width=Math.min(p.width,maxWidth),height=width*9/16+chrome;
  const spanX=Math.max(0,v.width-2*margin-width),spanY=Math.max(0,v.height-2*margin-height);
  return {width,height,left:v.left+margin+spanX*p.x,top:v.top+margin+spanY*p.y,spanX,spanY,maxWidth,v,margin};
 }
 function place(p){
  const g=geometry(p);Object.assign(box.style,{width:g.width+'px',left:g.left+'px',top:g.top+'px'});
  window.FieldStage.scale(stage);
  for(const b of box.querySelectorAll('[data-floating-size]'))b.setAttribute('aria-pressed',String(Number(b.dataset.floatingSize)===p.width));
  resize.setAttribute('aria-label',`Resize preview, ${Math.round(g.width)} by ${Math.round(g.width*9/16)}`);
  return g;
 }
 function refresh(){
  frame=0;const {tab,state,layout}=getView(),p=prefs[tab];
  if(!p?.enabled||!state||!layout||!$('authGate').classList.contains('hidden')){hide();return}
  // Keep page navigation accessible even when browser zoom leaves very little
  // vertical space. Scrolling down to the controls restores the preview.
  if(inView($('sectionNavigation'))||$('sectionNavigation').classList.contains('menu-open')){hide();return}
  const main=$(tab==='editor'?'editorFrame':'previewStage')?.closest('.stage-frame');
  const r=main?.getBoundingClientRect(),v=viewport();
  const visible=r&&r.width>0&&r.height>0?Math.max(0,Math.min(r.bottom,v.top+v.height)-Math.max(r.top,v.top)):0;
  // If a page has no main preview, fall back to scrolling one viewport down.
  if(main?visible>=Math.min(48,r.height):scrollY<v.height*.6){hide();return}
  box.hidden=false;box.dataset.previewView=tab;$('floatingTitle').textContent=tab==='editor'?'Layout draft':'Live preview';
  window.FieldStage.paint(stage,state,layout,null);place(p);
 }
 function schedule(){if(!frame)frame=requestAnimationFrame(refresh)}
 for(const tab of ['control','editor'])$('floating-'+tab+'-enabled').addEventListener('change',event=>{prefs[tab].enabled=event.target.checked;store();schedule()});
 $('floatingClose').addEventListener('click',()=>{const p=prefs[getView().tab];if(p){p.enabled=false;store();syncSwitches()}hide()});
 for(const b of box.querySelectorAll('[data-floating-size]'))b.addEventListener('click',()=>{const p=prefs[getView().tab];if(!p)return;p.width=Number(b.dataset.floatingSize);store();place(p)});
 document.addEventListener('focusin',event=>{if(!box.contains(event.target))previousFocus=event.target});
 function position(p,g,left,top){p.x=g.spanX?clamp((left-g.v.left-g.margin)/g.spanX,0,1):0;p.y=g.spanY?clamp((top-g.v.top-g.margin)/g.spanY,0,1):0}
 for(const [button,kind] of [[move,'move'],[resize,'resize']]){
  button.addEventListener('pointerdown',event=>{
   if(event.button!==0||gesture)return;
   const tab=getView().tab,p=prefs[tab];if(!p)return;
   event.preventDefault();button.focus({preventScroll:true});button.setPointerCapture(event.pointerId);
   gesture={tab,kind,id:event.pointerId,startX:event.clientX,startY:event.clientY,p:{...p},g:place(p)};
  });
  button.addEventListener('pointermove',event=>{
   if(!gesture||gesture.id!==event.pointerId)return;
   const {tab,kind,startX,startY,g}=gesture,p=prefs[tab],dx=event.clientX-startX,dy=event.clientY-startY;
   if(kind==='move')position(p,g,g.left+dx,g.top+dy);
   else{
    const change=Math.abs(dx)>=Math.abs(dy*16/9)?dx:dy*16/9;
    p.width=clamp(g.width+change,Math.min(214,g.maxWidth),g.maxWidth);
    // Resize from the top left, instead of drifting around a relative anchor.
    position(p,geometry(p),g.left,g.top);
   }
   place(p);
  });
  function finish(event){if(!gesture||gesture.id!==event.pointerId)return;if(event.type==='pointercancel')prefs[gesture.tab]=gesture.p;gesture=null;store();schedule()}
  button.addEventListener('pointerup',finish);button.addEventListener('pointercancel',finish);button.addEventListener('lostpointercapture',finish);
  button.addEventListener('keydown',event=>{
   const p=prefs[getView().tab];if(!p)return;
   if(event.key==='Escape'&&gesture){prefs[gesture.tab]=gesture.p;gesture=null;store();schedule();event.preventDefault();event.stopPropagation();return}
   if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','Home'].includes(event.key))return;
   event.preventDefault();event.stopPropagation();const g=place(p),step=event.shiftKey?1:10;
   if(event.key==='Home'){if(kind==='move'){p.x=1;p.y=1}else p.width=320}
   else if(kind==='move')position(p,g,g.left+(event.key==='ArrowRight'?step:event.key==='ArrowLeft'?-step:0),g.top+(event.key==='ArrowDown'?step:event.key==='ArrowUp'?-step:0));
   else{p.width=clamp(g.width+(['ArrowRight','ArrowDown'].includes(event.key)?step:-step),Math.min(214,g.maxWidth),g.maxWidth);position(p,geometry(p),g.left,g.top)}
   store();place(p);
  });
 }
 window.addEventListener('scroll',schedule,{passive:true});window.addEventListener('resize',schedule);
 window.visualViewport?.addEventListener('resize',schedule);window.visualViewport?.addEventListener('scroll',schedule);
 if(window.ResizeObserver){const observer=new ResizeObserver(schedule);for(const id of ['editorFrame','livePreview'])if($(id))observer.observe($(id))}
 new MutationObserver(schedule).observe($('sectionNavigation'),{attributes:true,attributeFilter:['class']});
 syncSwitches();return {update:schedule};
}};
