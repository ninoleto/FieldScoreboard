'use strict';
(() => {
 const canvas=document.getElementById('overlayStage');
 let lastSeen=0,connected=false,source=null;
 function apply(state){if(!state||!state.layout||!state.main||!state.shot)return;lastSeen=Date.now();canvas.style.opacity='1';window.FieldStage.paint(canvas,state,state.layout,null);window.FieldStage.scale(canvas)}
 async function snapshot(){try{const r=await fetch('/api/overlay-state',{cache:'no-store'});if(!r.ok)throw Error('offline');apply(await r.json())}catch(_){if(Date.now()-lastSeen>6000)canvas.style.opacity='0'}}
 function connect(){if(!window.EventSource)return;source=new EventSource('/api/overlay-events');source.onopen=()=>{connected=true};source.onmessage=e=>{try{apply(JSON.parse(e.data))}catch(_){}};source.onerror=()=>{connected=false}}
 window.addEventListener('resize',()=>window.FieldStage.scale(canvas));
 if(window.ResizeObserver)new ResizeObserver(()=>window.FieldStage.scale(canvas)).observe(document.getElementById('overlayFrame'));
 window.FieldStage.initialize(canvas);window.FieldStage.scale(canvas);connect();snapshot();setInterval(()=>{if(!connected||Date.now()-lastSeen>2500)snapshot();if(Date.now()-lastSeen>6000)canvas.style.opacity='0'},1500);
})();
