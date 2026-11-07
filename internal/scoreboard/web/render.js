'use strict';
(function(){
 const fieldIDs=['period','main_clock','shot_clock','home_name','home_score','home_fouls','away_score','away_fouls','away_name'];
 const families={sans:'Arial, "Liberation Sans", sans-serif',mono:'Consolas, "DejaVu Sans Mono", monospace',serif:'Georgia, "DejaVu Serif", serif',heavy:'"Arial Black", "DejaVu Sans", sans-serif'};
 const entries=new WeakMap();
 function initialize(stage){
  if(entries.has(stage))return entries.get(stage);
  const bg=document.createElement('img');bg.className='stage-bg';bg.alt='';bg.draggable=false;bg.hidden=true;stage.append(bg);
  bg.addEventListener('load',()=>stage.dispatchEvent(new Event('backgroundload')));
  const nodes={};for(const id of fieldIDs){const div=document.createElement('div');div.dataset.id=id;div.className='stage-element';stage.append(div);nodes[id]=div}
  const entry={bg,nodes};entries.set(stage,entry);return entry;
 }
 function fieldValue(id,s){switch(id){case 'period':return s.period_label || String(s.period);case 'main_clock':return s.main.display;case 'shot_clock':return s.shot.display;case 'home_name':return s.home_name;case 'away_name':return s.away_name;case 'home_score':return String(s.home_score);case 'away_score':return String(s.away_score);case 'home_fouls':return s.home_fouls;case 'away_fouls':return s.away_fouls;default:return ''}}
 function dots(node,count,max){
  const key=`dot-${count}/${max}`;if(node.dataset.value===key)return;
  node.dataset.value=key;node.replaceChildren();const bar=document.createElement('span');bar.className='foul-dots';bar.setAttribute('aria-label',`${count} fouls`);
  for(let i=0;i<max;i++){const d=document.createElement('span');d.className='foul-dot '+(i<count?'filled':'empty');bar.append(d)}
  if(count>max){const more=document.createElement('span');more.textContent=`+${count-max}`;bar.append(more)}
  node.append(bar);
 }
 function paint(stage,s,layout,selected,skipDrag){
  if(!stage||!s||!layout)return;const e=initialize(stage);
  const bg=layout.background?'/background/'+encodeURIComponent(layout.background):'';
  if(e.bg.dataset.path!==bg){e.bg.dataset.path=bg;e.bg.hidden=!bg;if(bg)e.bg.src=bg;else e.bg.removeAttribute('src')}
  const transform=backgroundBox(layout);
  Object.assign(e.bg.style,{left:transform.x+'px',top:transform.y+'px',width:transform.width+'px',height:transform.height+'px'});
  for(const id of fieldIDs){const node=e.nodes[id];const item=layout.elements[id];if(!item)continue;
   if(!(skipDrag===id)){node.style.left=item.x+'px';node.style.top=item.y+'px'}
   node.style.fontSize=item.size+'px';node.style.fontWeight=item.bold?'800':'400';node.style.fontFamily=families[item.font]||families.sans;
   node.style.color=item.color;node.dataset.align=item.align;node.style.display=(item.visible && !(id==='shot_clock' && s.shot_visible===false && !stage.classList.contains('stage-editor')))?'':'none';
   // Scale content (including foul dots), with the text anchor fixed at X/Y.
   // Natural width can grow as digits/names change; there is no clipping box.
   const t=item.transform,anchor=item.align==='right'?100:item.align==='center'?50:0;
   node.style.transform=t?`scale(${t.scale_x},${t.scale_y}) translateX(-${anchor}%)`:'';
   node.classList.toggle('selected',selected===id);
   node.style.zIndex=(selected===id?'2':'1');
   const isHome=id==='home_fouls';const isAway=id==='away_fouls';
   if((isHome&&layout.foul_style_home==='dots')||(isAway&&layout.foul_style_away==='dots')){dots(node,isHome?s.home_fouls:s.away_fouls,layout.foul_dots_max)}
   else{const value=fieldValue(id,s);if(node.dataset.value!==value){node.dataset.value=value;node.textContent=value}}
  }
 }
 function scale(stage){if(!stage||!stage.parentElement)return 1;const box=stage.parentElement;const w=box.clientWidth,h=box.clientHeight;const ratio=Math.min(w/1920,h/1080);stage.style.transform=`translate(${(w-1920*ratio)/2}px,${(h-1080*ratio)/2}px) scale(${ratio})`;return ratio}
 function backgroundBox(layout){return layout.background_transform||{x:0,y:0,width:1920,height:1080}}
 function backgroundPreset(mode,width,height,lock=true){
  let w=width,h=height;
  if(mode==='stretch'){w=1920;h=1080}
  else if(mode==='fit'||mode==='fill'){const factor=Math[mode==='fit'?'min':'max'](1920/width,1080/height);w*=factor;h*=factor}
  return {mode,width:w,height:h,x:(1920-w)/2,y:(1080-h)/2,original_width:width,original_height:height,lock_aspect:lock};
 }
 function elementBox(stage,id){
  const node=initialize(stage).nodes[id],canvas=stage.getBoundingClientRect(),ratio=canvas.width/1920;
  if(!node||ratio<=0||getComputedStyle(node).display==='none')return null;
  const box=node.getBoundingClientRect();
  return {left:(box.left-canvas.left)/ratio,top:(box.top-canvas.top)/ratio,width:box.width/ratio,height:box.height/ratio};
 }
 window.FieldStage={fieldIDs,paint,scale,initialize,backgroundBox,backgroundPreset,elementBox};
})();
