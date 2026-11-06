'use strict';
// Editor-only interactions. The shared renderer consumes the resulting logical
// rectangle unchanged in preview and OBS. Nothing here changes the image file.
window.createBackgroundEditor=({getLayout,mark,message})=>{
 const $=id=>document.getElementById(id),canvas=$('editorStage'),frame=$('editorFrame');
 const fields={backgroundWidth:'width',backgroundHeight:'height',backgroundX:'x',backgroundY:'y'};
 const max=1920*8192,drafts=new Set();
 let selected=false,gesture=null,lastImage='',natural=null;
 const surface=document.createElement('div');surface.className='background-drag-surface';surface.tabIndex=0;
 surface.setAttribute('role','group');surface.setAttribute('aria-label','Selected background. Drag or use arrow keys to move.');
 const border=document.createElement('div');border.className='background-selection-border';border.setAttribute('aria-hidden','true');
 const handles=['nw','ne','sw','se'].map(corner=>{
  const b=document.createElement('button');b.type='button';b.className='background-resize-handle';b.dataset.corner=corner;
  b.setAttribute('aria-label','Resize background from '+({nw:'top left',ne:'top right',sw:'bottom left',se:'bottom right'}[corner]));
  b.textContent=(corner==='nw'||corner==='se')?'⤡':'⤢';return b;
 });
 frame.append(surface,border,...handles);
 function metadata(){
  const l=getLayout(),t=l?.background_transform;
  if(t)return {width:t.original_width,height:t.original_height};
  const img=canvas.querySelector('.stage-bg');
  if(l?.background&&img?.dataset.path==='/background/'+encodeURIComponent(l.background)&&img.complete&&img.naturalWidth){return {width:img.naturalWidth,height:img.naturalHeight}}
  return natural;
 }
 function transform(){
  const l=getLayout(),size=metadata();
  return l?.background_transform||(size?{...FieldStage.backgroundPreset('stretch',size.width,size.height),lock_aspect:true}:null);
 }
 function setTransform(t){getLayout().background_transform=t;mark();sync()}
 function select(value){selected=!!value&&!!getLayout()?.background;updateSelection();$('selectBackground').setAttribute('aria-pressed',String(selected));$('selectBackground').textContent=selected?'Finish editing background':'Edit background — move & resize';markSelection()}
 function markSelection(){canvas.dispatchEvent(new Event('backgroundselection'))}
 function updateSelection(){
  const l=getLayout(),active=selected&&!!l?.background;
  for(const node of [surface,border,...handles])node.hidden=!active;
  frame.classList.toggle('background-selected',active);
  if(!active)return;
  FieldStage.scale(canvas);
  const t=FieldStage.backgroundBox(l),r=canvas.getBoundingClientRect(),f=frame.getBoundingClientRect(),scale=r.width/1920;
  const left=r.left-f.left-frame.clientLeft,top=r.top-f.top-frame.clientTop;
  Object.assign(border.style,{left:left+t.x*scale+'px',top:top+t.y*scale+'px',width:t.width*scale+'px',height:t.height*scale+'px'});
  const x=Math.max(0,t.x),y=Math.max(0,t.y),right=Math.min(1920,t.x+t.width),bottom=Math.min(1080,t.y+t.height);
  Object.assign(surface.style,{left:left+x*scale+'px',top:top+y*scale+'px',width:Math.max(0,right-x)*scale+'px',height:Math.max(0,bottom-y)*scale+'px'});
  for(const b of handles){
   const x=t.x+(b.dataset.corner.endsWith('e')?t.width:0),y=t.y+(b.dataset.corner.startsWith('s')?t.height:0);
   // Cropped corners stay reachable at the canvas edge. Their opposite logical
   // corner remains the resize anchor, including for Fill and large originals.
   const px=Math.max(28,Math.min(frame.clientWidth-28,left+x*scale)),py=Math.max(28,Math.min(frame.clientHeight-28,top+y*scale));
   b.style.left=px+'px';b.style.top=py+'px';
  }
 }
 function sync(){
  const l=getLayout();if(!l)return;
  if(lastImage!==l.background){lastImage=l.background;natural=null;drafts.clear();gesture=null;selected=false;}
  natural=metadata();const t=transform(),ready=!!l.background&&!!t;
  for(const [id,key] of Object.entries(fields)){
   $(id).disabled=!ready;
   if(!drafts.has(id))$(id).value=t?String(Math.round(t[key]*1000)/1000):'';
  }
  for(const b of document.querySelectorAll('[data-background-step]'))b.disabled=!ready;
  for(const id of ['backgroundSizing','backgroundLock','centerBackground','fitBackground'])$(id).disabled=!ready;
  $('selectBackground').disabled=!ready;$('removeBackground').disabled=!l.background;
  $('backgroundSizing').value=t?.mode||'fit';$('backgroundLock').checked=t?.lock_aspect??true;
  const custom=$('backgroundSizing').querySelector('[value="custom"]');
  if(custom.hidden!==(t?.mode!=='custom'))custom.hidden=t?.mode!=='custom';
  $('backgroundOriginal').textContent=natural?`Original: ${natural.width} × ${natural.height} px`:(l.background?'Loading original dimensions…':'No background imported');
  $('backgroundName').textContent=l.background?'Image: '+l.background.slice(0,10)+'…':'';
  $('selectBackground').setAttribute('aria-pressed',String(selected));$('selectBackground').textContent=selected?'Finish editing background':'Edit background — move & resize';
  window.refreshTouchOptions?.();updateSelection();
 }
 const valueOf=id=>{const value=$(id).value.trim();return value===''?NaN:Number(value)};
 function valid(id){const value=valueOf(id),dimension=fields[id]==='width'||fields[id]==='height';return Number.isFinite(value)&&Math.abs(value)<=max&&(!dimension||value>=.01)}
 function applyField(id){
  if(!valid(id)){$(id).setAttribute('aria-invalid','true');mark();return false}
  let t=transform();if(!t)return false;t={...t,[fields[id]]:valueOf(id),mode:'custom'};
  if(t.lock_aspect&&(fields[id]==='width'||fields[id]==='height')){
   const ratio=t.original_width/t.original_height;
   if(fields[id]==='width')t.height=t.width/ratio;else t.width=t.height*ratio;
   if(Math.max(t.width,t.height)>max||Math.min(t.width,t.height)<.01){$(id).setAttribute('aria-invalid','true');mark();return false}
   const other=id==='backgroundWidth'?'backgroundHeight':'backgroundWidth';drafts.delete(other);$(other).removeAttribute('aria-invalid');
  }
  $(id).removeAttribute('aria-invalid');setTransform(t);return true;
 }
 function commitDrafts(){
  for(const id of drafts){if(!valid(id)||$(id).getAttribute('aria-invalid')==='true'){message('Enter valid background dimensions (positive) and positions in pixels before saving.');$(id).focus();return false}}
  return true;
 }
 function resetDrafts(){drafts.clear();for(const id of Object.keys(fields))$(id).removeAttribute('aria-invalid');sync()}
 for(const id of Object.keys(fields)){
  $(id).addEventListener('input',()=>{drafts.add(id);applyField(id)});
  $(id).addEventListener('change',()=>{drafts.add(id);applyField(id)});
 }
 for(const b of document.querySelectorAll('[data-background-step]'))b.addEventListener('click',()=>{
  const [id,delta]=b.dataset.backgroundStep.split(':');
  if(!valid(id)){message('Enter a valid number before using its step buttons.');$(id).focus();return}
  const minimum=['width','height'].includes(fields[id]) ? .01 : -max;
  $(id).value=String(Math.min(max,Math.max(minimum,valueOf(id)+Number(delta))));drafts.add(id);applyField(id);
 });
 function preset(mode){
  const t=transform();if(!t)return;
  resetDrafts();setTransform(FieldStage.backgroundPreset(mode,t.original_width,t.original_height,mode==='fit'?true:t.lock_aspect));
 }
 $('backgroundSizing').addEventListener('change',()=>{if($('backgroundSizing').value!=='custom')preset($('backgroundSizing').value)});
 $('fitBackground').addEventListener('click',()=>preset('fit'));
 $('centerBackground').addEventListener('click',()=>{if(!commitDrafts())return;const t=transform();setTransform({...t,x:(1920-t.width)/2,y:(1080-t.height)/2,mode:'custom'});drafts.delete('backgroundX');drafts.delete('backgroundY');sync()});
 $('backgroundLock').addEventListener('change',()=>{const t=transform();setTransform({...t,lock_aspect:$('backgroundLock').checked})});
 $('selectBackground').addEventListener('click',()=>select(!selected));
 canvas.addEventListener('backgroundload',sync);
 new ResizeObserver(updateSelection).observe(frame);
 function begin(event){
  if(!selected||!commitDrafts()||event.button!==0)return;
  event.preventDefault();event.stopPropagation();surface.focus({preventScroll:true});
  gesture={pointer:event.pointerId,x:event.clientX,y:event.clientY,scale:canvas.getBoundingClientRect().width/1920,base:{...transform()},corner:event.target.dataset.corner||''};
  frame.setPointerCapture(event.pointerId);resetDrafts();
 }
 surface.addEventListener('pointerdown',begin);handles.forEach(b=>b.addEventListener('pointerdown',begin));
 function move(base,corner,dx,dy){
  const clamp=v=>Math.max(-max,Math.min(max,v));let t={...base,mode:'custom'};
  if(!corner){t.x=clamp(base.x+dx);t.y=clamp(base.y+dy)}
  else{
   const west=corner.endsWith('w'),north=corner.startsWith('n');
   let w=base.width+(west?-dx:dx),h=base.height+(north?-dy:dy);
   if(base.lock_aspect){
    const ratio=base.original_width/base.original_height;
    if(Math.abs(dx/base.width)>=Math.abs(dy/base.height))h=w/ratio;else w=h*ratio;
    const widthMin=Math.max(.01,.01*ratio),widthMax=Math.min(max,max*ratio);
    w=Math.max(widthMin,Math.min(widthMax,w));h=w/ratio;
   }else{w=Math.max(.01,Math.min(max,w));h=Math.max(.01,Math.min(max,h))}
   t.width=w;t.height=h;t.x=clamp(west?base.x+base.width-w:base.x);t.y=clamp(north?base.y+base.height-h:base.y);
  }
  setTransform(t);
 }
 frame.addEventListener('pointermove',event=>{if(gesture&&event.pointerId===gesture.pointer)move(gesture.base,gesture.corner,(event.clientX-gesture.x)/gesture.scale,(event.clientY-gesture.y)/gesture.scale)});
 function end(event){if(!gesture||event.pointerId!==gesture.pointer)return;gesture=null;if(frame.hasPointerCapture(event.pointerId))frame.releasePointerCapture(event.pointerId)}
 frame.addEventListener('pointerup',end);frame.addEventListener('pointercancel',end);frame.addEventListener('lostpointercapture',()=>{gesture=null});
 for(const handle of handles)handle.addEventListener('keydown',event=>{
  if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(event.key))return;
  event.preventDefault();event.stopPropagation();const delta=event.shiftKey?10:1;
  if(!commitDrafts())return;resetDrafts();
  move(transform(),handle.dataset.corner,event.key==='ArrowLeft'?-delta:event.key==='ArrowRight'?delta:0,event.key==='ArrowUp'?-delta:event.key==='ArrowDown'?delta:0);
 });
 function nudge(dx,dy){if(!commitDrafts())return;resetDrafts();move(transform(),'',dx,dy)}
 return {sync,select,commitDrafts,resetDrafts,nudge,get selected(){return selected}};
};
