'use strict';
// Editor gestures produce optional scale factors; the shared renderer owns pixels.
window.createElementEditor=({getLayout,getSelected,selectField,mark,updateInspector,message,names})=>{
 const $=id=>document.getElementById(id),canvas=$('editorStage'),frame=$('editorFrame');
 const minimum=.05,maximum=20,fields={elementWidth:'width',elementHeight:'height'},drafts=new Map();
 let gesture=null,freeTransform=false,previousSelection=null;
 function stopGesture(){if(gesture&&frame.hasPointerCapture(gesture.pointer))frame.releasePointerCapture(gesture.pointer);gesture=null}
 function exitTransform(){freeTransform=false;stopGesture();sync()}
 const border=document.createElement('div');border.className='element-selection-border';border.setAttribute('aria-hidden','true');
 const guide=document.createElement('div');guide.className='element-handle-guide';guide.setAttribute('aria-hidden','true');
 const handles=['nw','n','ne','e','se','s','sw','w'].map(edge=>{
  const button=document.createElement('button');button.type='button';button.className='element-resize-handle';button.dataset.edge=edge;
  button.setAttribute('aria-label','Resize selected element from '+({nw:'top left',n:'top',ne:'top right',e:'right',se:'bottom right',s:'bottom',sw:'bottom left',w:'left'}[edge]));
  button.textContent=edge.length===2?(edge==='nw'||edge==='se'?'⤡':'⤢'):(edge==='n'||edge==='s'?'↕':'↔');return button;
 });
 for(const node of [guide,border,...handles])node.hidden=true;
 frame.append(guide,border,...handles);
 const item=()=>getLayout()?.elements[getSelected()];
 const transform=el=>el.transform||{scale_x:1,scale_y:1,lock_aspect:true};
 const anchor=el=>el.align==='right'?1:el.align==='center'?.5:0;
 function pending(id=getSelected()){if(!drafts.has(id))drafts.set(id,new Map());return drafts.get(id)}
 function sync(){
  const id=getSelected(),el=item(),box=el&&FieldStage.elementBox(canvas,id),active=!!box&&el.visible;
  if(id!==previousSelection){freeTransform=false;stopGesture();previousSelection=id}
  const transforming=active&&freeTransform;
  $('freeTransform').disabled=!el;
  $('freeTransform').textContent=freeTransform?'Done transforming':'Free transform';
  $('freeTransform').setAttribute('aria-pressed',String(freeTransform));
  frame.classList.toggle('free-transform',!!transforming);
  $('editorSelectionLabel').textContent='Editing: '+(id==='background'?'Background graphic':names[id]||'Select an element');
  $('selectedTitle').textContent=id==='background'?'Background graphic':names[id]||'Select an element';
  document.querySelectorAll('[data-field]').forEach(b=>b.classList.toggle('selected',b.dataset.field===id));
  for(const node of [border,guide,...handles])node.hidden=!transforming;
  for(const control of ['elementWidth','elementHeight','elementAspect','resetElementSize'])$(control).disabled=!active;
  document.querySelectorAll('[data-transform-step]').forEach(b=>b.disabled=!active);
  if(!active)return;
  const t=transform(el);$('elementAspect').checked=t.lock_aspect;
  for(const [field,dimension] of Object.entries(fields)){
   const draft=pending().get(field);$(field).value=draft?.raw??String(Math.round(box[dimension]*1000)/1000);
   $(field).toggleAttribute('aria-invalid',!!draft&&!draft.valid);
   if(draft&&!draft.valid)$(field).setAttribute('aria-invalid','true');
  }
  const r=canvas.getBoundingClientRect(),f=frame.getBoundingClientRect(),ratio=r.width/1920;
  const x=r.left-f.left-frame.clientLeft+box.left*ratio,y=r.top-f.top-frame.clientTop+box.top*ratio,w=box.width*ratio,h=box.height*ratio;
  Object.assign(border.style,{left:x+'px',top:y+'px',width:w+'px',height:h+'px'});
  // Small logical fields still need distinct 56px touch handles. A dotted guide
  // expands their spacing; the solid inner border always shows actual bounds.
  function span(start,size,limit){
   const extent=Math.min(Math.max(size,112),Math.max(0,limit-56));
   const center=Math.max(28+extent/2,Math.min(limit-28-extent/2,start+size/2));
   return [center-extent/2,center+extent/2];
  }
  const [left,right]=span(x,w,frame.clientWidth),[top,bottom]=span(y,h,frame.clientHeight);
  Object.assign(guide.style,{left:left+'px',top:top+'px',width:right-left+'px',height:bottom-top+'px'});
  for(const b of handles){const edge=b.dataset.edge;
   b.hidden=!transforming||(t.lock_aspect&&edge.length===1);
   b.style.left=(edge.includes('w')?left:edge.includes('e')?right:(left+right)/2)+'px';
   b.style.top=(edge.includes('n')?top:edge.includes('s')?bottom:(top+bottom)/2)+'px';
  }
 }
 $('freeTransform').addEventListener('click',()=>{if(item()){freeTransform=!freeTransform;stopGesture();sync()}});
 function applyField(id){
  const el=item(),box=el&&FieldStage.elementBox(canvas,getSelected());if(!box)return false;
  const raw=$(id).value,value=raw.trim()===''?NaN:Number(raw),t={...transform(el)},dimension=fields[id];
  const factor=value/box[dimension];
  if(dimension==='width')t.scale_x*=factor;else t.scale_y*=factor;
  if(t.lock_aspect){if(dimension==='width')t.scale_y*=factor;else t.scale_x*=factor}
  const valid=Number.isFinite(value)&&value>0&&[t.scale_x,t.scale_y].every(v=>Number.isFinite(v)&&v>=minimum&&v<=maximum);
  pending().set(id,{raw,valid});if(valid){el.transform=t;if(t.lock_aspect)pending().delete(id==='elementWidth'?'elementHeight':'elementWidth')}
  mark();sync();return valid;
 }
 for(const id of Object.keys(fields)){
  $(id).addEventListener('input',()=>applyField(id));
  $(id).addEventListener('change',()=>{if(applyField(id)){pending().delete(id);sync()}});
 }
 document.querySelectorAll('[data-transform-step]').forEach(b=>b.addEventListener('click',()=>{
  const [id,step]=b.dataset.transformStep.split(':'),raw=$(id).value,value=Number(raw);
  if(!raw.trim()||!Number.isFinite(value)){message('Enter a valid element size first.');return}
  $(id).value=String(Math.round((value+Number(step))*1000)/1000);if(applyField(id)){pending().delete(id);sync()}
 }));
 function commitDrafts(){
  for(const [target,values] of drafts)for(const [id,value] of values)if(!value.valid){selectField(target);message('Enter a valid '+names[target]+' size (5%–2000% scale) before saving.');$(id).focus();return false}
  return true;
 }
 function resetDrafts(){drafts.clear();sync()}
 $('elementAspect').addEventListener('change',()=>{const el=item();if(el){el.transform={...transform(el),lock_aspect:$('elementAspect').checked};mark()}});
 $('resetElementSize').addEventListener('click',()=>{const el=item();if(el){delete el.transform;drafts.delete(getSelected());mark()}});
 function begin(event){
  if(event.button!==0)return;
  const node=event.target.closest('.stage-element'),edge=event.target.dataset.edge||'';
  if(edge&&!freeTransform)return;
  if(!node&&!edge)return;if(node)selectField(node.dataset.id);
  const el=item(),box=el&&FieldStage.elementBox(canvas,getSelected());if(!box||!commitDrafts())return;
  event.preventDefault();event.stopPropagation();canvas.focus({preventScroll:true});drafts.delete(getSelected());
  gesture={id:getSelected(),pointer:event.pointerId,x:event.clientX,y:event.clientY,ratio:canvas.getBoundingClientRect().width/1920,box,base:{...el,transform:{...transform(el)}},edge};
  frame.setPointerCapture(event.pointerId);
 }
 canvas.addEventListener('pointerdown',begin);handles.forEach(b=>b.addEventListener('pointerdown',begin));
 const clamp=(v,min,max)=>Math.max(min,Math.min(max,v));
 function move(g,dx,dy){
  const el=getLayout().elements[g.id],base=g.base,t={...base.transform},box=g.box,edge=g.edge;
  if(!edge){el.x=clamp(Math.round(base.x+dx),0,1920);el.y=clamp(Math.round(base.y+dy),0,1080)}
  else{
   const west=edge.includes('w'),north=edge.includes('n'),horizontal=west||edge.includes('e'),vertical=north||edge.includes('s');
   let fx=horizontal?1+(west?-dx:dx)/box.width:1,fy=vertical?1+(north?-dy:dy)/box.height:1;
   if(t.lock_aspect){const factor=Math.abs(fx-1)>=Math.abs(fy-1)?fx:fy;fx=fy=clamp(factor,Math.max(minimum/t.scale_x,minimum/t.scale_y),Math.min(maximum/t.scale_x,maximum/t.scale_y))}
   else{fx=clamp(fx,minimum/t.scale_x,maximum/t.scale_x);fy=clamp(fy,minimum/t.scale_y,maximum/t.scale_y)}
   const width=box.width*fx,height=box.height*fy;
   t.scale_x*=fx;t.scale_y*=fy;el.transform=t;
   const left=west?box.left+box.width-width:box.left,top=north?box.top+box.height-height:box.top;
   el.x=clamp(Math.round(left+anchor(base)*width),0,1920);el.y=clamp(Math.round(top),0,1080);
  }
  updateInspector();mark();
 }
 frame.addEventListener('pointermove',event=>{if(gesture&&event.pointerId===gesture.pointer)move(gesture,(event.clientX-gesture.x)/gesture.ratio,(event.clientY-gesture.y)/gesture.ratio)});
 function end(event){if(!gesture||event.pointerId!==gesture.pointer)return;gesture=null;if(frame.hasPointerCapture(event.pointerId))frame.releasePointerCapture(event.pointerId);sync()}
 frame.addEventListener('pointerup',end);frame.addEventListener('pointercancel',end);frame.addEventListener('lostpointercapture',()=>{gesture=null});
 for(const handle of handles)handle.addEventListener('keydown',event=>{
  if(!freeTransform||!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(event.key)||!commitDrafts())return;
  event.preventDefault();event.stopPropagation();const el=item(),box=FieldStage.elementBox(canvas,getSelected()),step=event.shiftKey?10:1;if(!el||!box)return;
  drafts.delete(getSelected());move({id:getSelected(),base:{...el,transform:{...transform(el)}},box,edge:handle.dataset.edge},event.key==='ArrowLeft'?-step:event.key==='ArrowRight'?step:0,event.key==='ArrowUp'?-step:event.key==='ArrowDown'?step:0);
 });
 new ResizeObserver(sync).observe(frame);
 return {sync,commitDrafts,resetDrafts,exitTransform};
};
