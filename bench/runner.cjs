const fs=require('fs'),path=require('path');
const {pathToFileURL}=require('url');
const {chromium}=require('<PLAYWRIGHT_MODULE>');
(async()=>{
 const folder=process.argv[2]||'original', out=process.argv[3]||'app.json';
 const corpus=JSON.parse(fs.readFileSync('corpus.json','utf8'));
 const browser=await chromium.launch({channel:'chrome',headless:true});
 const page=await browser.newPage(); const errors=[];
 page.on('pageerror',e=>errors.push(String(e)));
 await page.goto(pathToFileURL(path.resolve(folder,'influence/index.html')).href);
 const results={};
 for(const [id,c] of Object.entries(corpus)){
  try {
   results[id]=await page.evaluate(c=>{
    const ta=document.querySelector('#src');
    ta.value=c.yi.map((y,i)=>`${y}, ${Math.sqrt(c.vi[i])}, row${c.rows[i]}`).join('\n');
    document.querySelector('#btn-run').click();
    const full=window._almLastInfluence(),diag=window._almLastDiag();
    if(!full||diag.length!==c.yi.length) throw Error('stale or missing result');
    return {full,diag,baujat:window.__almBaujat,radial:window.__almRadial,
      flags:[...document.querySelectorAll('#body tr')].slice(0,-1).map(r=>r.classList.contains('flag')),
      ui:{tableRows:document.querySelectorAll('#body tr').length,
       plots:['loo-plot','influence-plot','baujat-plot','radial-plot'].map(id=>document.getElementById(id).children.length)}};
   },c);
  }catch(e){results[id]={error:String(e)}}
  fs.writeFileSync(out,JSON.stringify(results));
  console.log(id,c.yi.length);
 }
 fs.writeFileSync(out+'.errors.json',JSON.stringify(errors));
 await browser.close();
 console.log(`APP ${Object.keys(results).length} configurations; ${errors.length} page errors`);
})().catch(e=>{console.error(e);process.exit(1)});
