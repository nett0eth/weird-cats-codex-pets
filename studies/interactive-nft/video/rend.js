const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const [,,dir,fmt,mode]=process.argv;const b=await chromium.launch();
const vp=fmt==='h'?{width:1920,height:1080}:{width:1080,height:1920};
const p=await b.newPage({viewport:vp});const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto(`file://${dir}/video.html?f=${fmt}`);await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
if(mode==='preview'){for(const t of [0.1,1.0,2.0,3.0,5,8,10.5,13,15,18]){await p.evaluate(t=>render(t),t);await p.screenshot({path:`${dir}/prev_${fmt}_${t}.png`})}}
else{fs.mkdirSync(`${dir}/frames_${fmt}`,{recursive:true});const N=Math.round(20*30);
 for(let i=0;i<N;i++){await p.evaluate(t=>render(t),i/30);await p.screenshot({path:`${dir}/frames_${fmt}/f${String(i).padStart(4,'0')}.png`})}}
console.log(errs);await b.close()})();
