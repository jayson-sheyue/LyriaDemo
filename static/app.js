'use strict';
const GLOBAL = new Set(['guide-content','source-content','source-links','show-guide','show-readme','model-rules','compare-models','compare-methods','compare-api','compare-why','compare-fit','session-limits','feature-value','api-out-of-demo','workspaces']);
let catalog, active='clip', busy=false, controller, objectUrl=null, savedConfig=null;
const primed=new Set();
const pageImages=new Map();
const $ = id => {
  if(GLOBAL.has(id)) return document.getElementById(id);
  const page=document.getElementById('page-'+active);
  if(page){const el=page.querySelector(`[data-id="${id}"]`); if(el) return el;}
  return document.getElementById(id);
};
function workspace(id){return (catalog.workspaces||[]).find(item=>item.id===id)||catalog.workspaces[0];}
function has(feature, spec){return ((spec||workspace(active)).features||[]).includes(feature);}
function val(id, fallback=''){const el=$(id); return el?el.value:fallback;}
function isOn(id){const el=$(id); return !!(el&&el.checked);}
function options(select,entries){if(!select)return; select.replaceChildren(); entries.forEach(([value,label])=>select.add(new Option(label,value)));}
function escapeHtml(value){return String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function featureNote(id){
  const b=(catalog&&catalog.feature_blurbs||{})[id];
  if(!b) return '';
  return `<div class="feature-note"><p><strong>开了会怎样</strong> ${escapeHtml(b.effect)}</p><p><strong>业务价值</strong> ${escapeHtml(b.value)}</p><p class="caution"><strong>不要用来</strong> ${escapeHtml(b.caution)}</p></div>`;
}
function featureBlock(id, controlHtml){
  return `<div class="feature-block">${controlHtml}${featureNote(id)}</div>`;
}
function report(state, summary, detail=''){
  const box=$('log-box'); if(!box) return;
  box.className='log-box '+state;
  $('log-state').textContent={idle:'待命',loading:'进行中',ok:'成功',error:'失败'}[state]||state;
  $('log-summary').textContent=summary;
  $('log-spinner').hidden=state!=='loading';
  const pre=$('log-detail');
  if(detail){pre.hidden=false;pre.textContent=detail;}else{pre.hidden=true;pre.textContent='';}
  if(state!=='idle') box.scrollIntoView({behavior:'smooth',block:'nearest'});
}
function fail(error, fallback){
  const summary=error&&error.name==='AbortError'?'已停止。已提交的请求仍可能计费。':((error&&error.message)||fallback||'操作失败');
  report('error', summary, error&&error.detail||'');
}
function currentImages(){return pageImages.get(active)||[];}
function setImages(list){pageImages.set(active, list); renderImageThumbs();}
function renderImageThumbs(){
  const root=$('image-thumbs'); if(!root) return;
  const list=currentImages();
  root.replaceChildren();
  list.forEach((item,index)=>{
    const fig=document.createElement('figure');
    const img=document.createElement('img'); img.src=`data:${item.mime_type};base64,${item.data}`; img.alt='参考图';
    const btn=document.createElement('button'); btn.type='button'; btn.className='text-button'; btn.textContent='去掉';
    btn.onclick=()=>setImages(list.filter((_,i)=>i!==index));
    fig.append(img, btn); root.append(fig);
  });
  const status=$('image-status');
  if(status) status.textContent=list.length?`已选 ${list.length} 张，会和文字一起发给模型。`:'还没有选图。点「看图」样例后也要在这里上传。';
}
function config(){
  const spec=workspace(active);
  return {
    engine: spec.id,
    model: val('model', spec.model),
    prompt: val('prompt'),
    lyrics: has('lyrics')?val('lyrics'):'',
    instrumental: has('instrumental')&&isOn('instrumental'),
    negative_prompt: has('negative')?val('negative_prompt'):'',
    seed: has('seed')?val('seed'):'',
    sample_count: has('seed')?Number(val('sample_count','1'))||1:1,
    images: has('image')?currentImages():[],
  };
}
function fillModels(){
  const spec=workspace(active);
  const sel=$('model'); if(!sel) return;
  options(sel, [[spec.model, spec.model]]);
  sel.value=spec.model;
  const card=catalog.model_cards&&catalog.model_cards[spec.model];
  if($('capability')) $('capability').textContent=card||'';
}
function applySample(sample, button, quiet=false){
  if(busy) return;
  const c=sample.config||{};
  fillModels();
  if($('prompt')) $('prompt').value=c.prompt||'';
  if($('lyrics')) $('lyrics').value=c.lyrics||'';
  if($('instrumental')) $('instrumental').checked=!!c.instrumental;
  if($('negative_prompt')) $('negative_prompt').value=c.negative_prompt||'';
  if($('seed')) $('seed').value=c.seed||'';
  if($('sample_count')) $('sample_count').value=String(c.sample_count||1);
  setImages([]);
  if($('expected')) $('expected').textContent=sample.expected?('样例预期：'+sample.expected):'';
  if($('sample-note')) $('sample-note').textContent=sample.note||'';
  document.querySelectorAll(`#page-${active} [data-id="samples"] button`).forEach(item=>item.classList.toggle('selected',item===button));
  if(!quiet){
    const needsImage=/看图|image/i.test(sample.id||'')||/看图|上传/.test(sample.note||'');
    report('ok',`已导入「${sample.title}」。这是 ${workspace(active).nav} 页的样例。`,
      needsImage?'这一条要看图：请到第 02 步点「选择参考图」上传 JPEG/PNG，再生成。':(sample.note||''));
  }
}
function renderSamples(){
  const root=$('samples'); if(!root) return;
  root.replaceChildren();
  const mine=(catalog.samples||[]).filter(sample=>sample.engine===active);
  const groups=new Map();
  mine.forEach(sample=>{const name=sample.group||'本页样例'; if(!groups.has(name)) groups.set(name,[]); groups.get(name).push(sample);});
  groups.forEach((items,name)=>{
    const block=document.createElement('div'); block.className='sample-group';
    const heading=document.createElement('small'); heading.textContent=name; block.append(heading);
    const chips=document.createElement('div'); chips.className='examples';
    items.forEach(sample=>{
      const button=document.createElement('button'); button.type='button'; button.textContent=sample.title;
      button.onclick=()=>applySample(sample,button); chips.append(button);
    });
    block.append(chips); root.append(block);
  });
  if(!mine.length){const p=document.createElement('p'); p.className='hint'; p.textContent='这一页还没有样例。'; root.append(p); return;}
  applySample(mine[0], root.querySelector('button'), true);
}
function htmlTable(rows){
  if(!rows||!rows.length) return '';
  const head=rows[0].map(cell=>`<th>${escapeHtml(String(cell))}</th>`).join('');
  const body=rows.slice(1).map(row=>'<tr>'+row.map(cell=>`<td>${cellHtml(cell)}</td>`).join('')+'</tr>').join('');
  return `<div class="compare-wrap"><table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table></div>`;
}
function cellHtml(value){
  return String(value).split(/(https:\/\/[^\s]+)/).map((part,i)=>i%2?`<a href="${escapeHtml(part)}" target="_blank" rel="noopener noreferrer">${escapeHtml(part)}</a>`:escapeHtml(part).replace(/\n/g,'<br>')).join('');
}
function pageIntro(spec){
  const pos=spec.positioning||{};
  const banner=pos.official?`<div class="mandate"><strong>${escapeHtml(pos.official)}</strong>${pos.this_page?`<p>${escapeHtml(pos.this_page)}</p>`:''}${pos.not_this?`<p class="not-for">${escapeHtml(pos.not_this)}</p>`:''}</div>`:'';
  const fit=(spec.fit||[]).map(item=>`<article class="fit-item"><strong>${escapeHtml(item.title)}</strong><p>${escapeHtml(item.body)}</p></article>`).join('');
  const surface=(spec.surface||[]).map(item=>`<li>${escapeHtml(item)}</li>`).join('');
  const impact=spec.limit_impact;
  const impactBox=impact?`<div class="limit-impact"><strong>${escapeHtml(impact.title||'这一页能撑多久')}</strong>${impact.lede?`<p>${escapeHtml(impact.lede)}</p>`:''}${(impact.items||[]).map(item=>`<article><strong>${escapeHtml(item.when||'')}</strong><p>${escapeHtml(item.impact||'')}</p><p class="do">${escapeHtml(item.do||'')}</p></article>`).join('')}<p class="hint">三页对照总表只在入门指南。</p></div>`:'';
  return `<section class="card page-intro">${banner}${impactBox}<div class="fit-row">${fit}</div>${spec.coverage?`<p class="hint coverage">${escapeHtml(spec.coverage)}</p>`:''}${spec.limit_note?`<p class="hint">${escapeHtml(spec.limit_note)}</p>`:''}${surface?`<div class="surface"><small>本页可试的 API 能力</small><ul>${surface}</ul></div>`:''}</section>`;
}
function pageDocs(spec){
  const docs=spec.docs||[];
  if(!docs.length) return '';
  const items=docs.map(d=>`<a class="doc-link" href="${escapeHtml(d.url)}" target="_blank" rel="noopener noreferrer"><strong>${escapeHtml(d.title)}</strong><small>${escapeHtml(d.why||'')}</small></a>`).join('');
  return `<section class="card docs-footer"><div class="card-heading"><h2>测通以后：接入你们系统</h2><span class="muted">官方文档</span></div><p class="hint">效果满意后再打开这些链接。本 Demo 不是 Google 产品；请求字段以对应页面为准。</p><div class="doc-grid">${items}</div></section>`;
}
function languageChips(spec){
  if(spec.id==='score') return '';
  const langs=catalog.vocal_languages||[];
  const buttons=langs.map(item=>`<button type="button" class="chip" data-lang="${escapeHtml(item.code)}">${escapeHtml(item.label)}</button>`).join('');
  return `<div class="lang-chips"><small>歌声语言写进提示词（不是请求字段）</small><div class="examples">${buttons}</div></div>`;
}
function workspaceHTML(spec){
  const ok=feature=>has(feature, spec);
  const advList=(spec.advantages||[]).map(item=>`<li>${item}</li>`).join('');
  const advBox=advList?`<ul class="advantage-list">${advList}</ul>`:'';
  const actionLabel={clip:'▶ 生成短片',song:'▶ 生成成曲',score:'▶ 生成配乐'}[spec.id]||'▶ 生成';
  const sourceCard = `
<section class="card">
<div class="card-heading"><h2><span class="step">01</span> 写这段音乐</h2><span class="muted">${spec.nav}</span></div>
<div class="sample-panel"><div class="sample-head"><strong>本页场景样例</strong><span class="muted">只导入 ${spec.nav}</span></div><div data-id="samples"></div><p data-id="sample-note" class="hint sample-note">样例不会跨页共用。</p></div>
<p data-id="expected" class="expected"></p>
<label>音乐描述<textarea data-id="prompt" placeholder="${spec.id==='score'?'An uplifting orchestral piece with soaring strings.':'A short instrumental acoustic guitar piece.'}"></textarea></label>
${languageChips(spec)}
<p class="hint">${spec.id==='score'?'官方要求美式英语。没有人声，也没有看图。':'描述用英文最稳。歌声语言点上面的芯片，会写进提示词。没有普通话。'}</p>
</section>`;
  const featureCard = `
<section class="card">
<div class="card-heading"><h2><span class="step">02</span> 本页相对别的工作台多出来的</h2><span class="muted">请求字段</span></div>
<p class="hint">每个开关下面写了开了会怎样、业务价值和不要用来。Lyria 3 没有 negative_prompt。</p>
${ok('instrumental')?featureBlock('instrumental', `<label class="check"><input data-id="instrumental" type="checkbox"> 只要器乐（提示词加 Instrumental. No vocals.）</label>`):''}
${ok('lyrics')?featureBlock('lyrics', `<label>歌词或主题<textarea data-id="lyrics" rows="5" placeholder="Lyrics: 或 [Verse] / [Chorus]。也可以只写主题。"></textarea></label>`):''}
${ok('timestamps')?featureBlock('timestamps', `<p class="hint">时间戳直接写在上面的描述里，例如 [0:00 - 0:12]。没有 duration 滑杆。</p>`):''}
${ok('image')?featureBlock('image', `<div class="image-upload"><strong>看图成曲：先选图，再生成</strong><p class="hint">JPEG / PNG，最多 10 张（官方上限）。内联合计约 100 MB。配乐页没有这个能力。</p><label class="secondary file-upload-btn">选择参考图<input data-id="image-file" type="file" accept="image/jpeg,image/png" multiple></label><div data-id="image-thumbs" class="image-thumbs"></div><p data-id="image-status" class="hint">还没有选图。点「看图」样例后也要在这里上传。</p></div>`):''}
${ok('negative')?featureBlock('negative', `<label>不要出现<textarea data-id="negative_prompt" rows="2" placeholder="vocals, sudden changes"></textarea></label>`):''}
${ok('seed')?featureBlock('seed', `<div class="grid2"><label>seed（留空则不用）<input data-id="seed" inputmode="numeric" placeholder="98765"></label><label>一次出几条<select data-id="sample_count"><option value="1">1</option><option value="2">2</option></select></label></div>`):''}
<p class="hint">${spec.id==='clip'?'固定大约 30 秒。要主歌副歌换成曲页。':spec.id==='song'?'最多大约 184 秒。生成常要等一两分钟。':'seed 和一次出几条不能一起用。'}</p>
</section>`;
  return `<section class="engine-page" id="page-${spec.id}" ${spec.id==='clip'?'':'hidden'}>
<div class="hero"><div><div class="eyebrow">${spec.eyebrow}</div><h1>${spec.title}</h1><p>${spec.lead}</p></div><div class="hero-wave" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div></div>
<div class="notice" data-id="connection">正在读取配置…</div>${advBox}${pageIntro(spec)}
<div class="workspace">
<div class="editor-col">${sourceCard}${featureCard}</div>
<aside>
<section class="card">
<div class="card-heading"><h2><span class="step">03</span> ${spec.nav}</h2><span class="pill">LYRIA</span></div>
<label>模型<select data-id="model"></select></label>
<p data-id="capability" class="hint"></p>
${spec.language_hint?`<p class="hint">${escapeHtml(spec.language_hint)}</p>`:''}
<button class="primary" data-id="primary" type="button"><span class="spinner" aria-hidden="true"></span><span class="btn-text">${actionLabel}</span></button>
<div class="button-row">
<button class="secondary" data-id="preview" type="button">预览请求 · 不收费</button>
<button class="secondary" data-id="stop" type="button" disabled>停止</button>
</div>
<div class="log-box idle" data-id="log-box">
<div class="log-head"><span class="spinner" data-id="log-spinner" hidden></span><strong data-id="log-state">待命</strong></div>
<p data-id="log-summary">预览不调用 Google。点生成才会计费。</p>
<pre data-id="log-detail" hidden></pre>
</div>
</section>
<section class="card output">
<div class="card-heading"><h2>听到什么</h2><span class="muted" data-id="status">还没有生成</span></div>
<div data-id="empty-output" class="empty"><span>♪ ♪ ♪</span><p>先预览，再生成。</p></div>
<div data-id="result" hidden>
<audio data-id="audio" controls></audio>
<a class="secondary" data-id="download">下载音频</a>
<p data-id="metrics" class="hint"></p>
<pre data-id="lyrics-out" hidden></pre>
</div>
</section>
<details>
<summary>请求预览</summary>
<p data-id="plan-info" class="hint"></p>
<pre data-id="request-preview"></pre>
</details>
</aside>
</div>
${pageDocs(spec)}
</section>`;
}
function connectionText(){
  const spec=workspace(active);
  const loc=(catalog.engine_locations||{})[spec.id]||'';
  const adc=catalog.adc_configured?'ADC 已检测到':'还没有 ADC';
  const project=catalog.project_configured?'项目 ID 已填写':'请填写 GOOGLE_CLOUD_PROJECT';
  return `${spec.nav} · ${spec.model} · ${loc} · ${adc} · ${project}。预览不收费。`;
}
function setBusy(value){
  busy=value;
  const primary=$('primary'), preview=$('preview'), stop=$('stop');
  if(primary){primary.disabled=value; primary.classList.toggle('busy',value);}
  if(preview) preview.disabled=value;
  if(stop) stop.disabled=!value;
}
async function post(url, body, signal){
  const response=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body),signal});
  if(!response.ok){
    let detail='';
    try{const data=await response.json(); detail=typeof data.detail==='string'?data.detail:(data.detail&&data.detail.message)||JSON.stringify(data.detail||data);}catch{detail=await response.text();}
    const err=Error(detail||('HTTP '+response.status)); err.detail=detail; throw err;
  }
  return response;
}
async function preview(){
  if(busy) return; setBusy(true); report('loading','正在预览请求，不会调用 Lyria…');
  try{
    const p=await(await post('/api/preview',config())).json();
    if($('plan-info')) $('plan-info').textContent=`${p.api} · ${p.model} · ${p.location}。${(p.warnings||[]).join(' ')}`;
    if($('request-preview')) $('request-preview').textContent=JSON.stringify({page:active,endpoint:p.endpoint,request:p.request,prompt:p.prompt},null,2);
    report('ok','预览成功。点生成才会计费。', (p.warnings||[]).join('\n'));
  }catch(e){fail(e,'预览失败');}
  finally{setBusy(false);}
}
async function generate(){
  if(busy) return;
  const r=config();
  if(has('image') && /this image|these images|in this image/i.test(r.prompt) && !(r.images||[]).length){
    report('error','提示词里提到了画面，但还没上传参考图。','到第 02 步点「选择参考图」。配乐页没有看图能力。');
    return;
  }
  controller=new AbortController();
  setBusy(true);
  report('loading', active==='song'?'正在生成成曲，可能要等一两分钟…':'正在生成…');
  if($('status')) $('status').textContent='已提交';
  if($('result')) $('result').hidden=true;
  if($('empty-output')) $('empty-output').hidden=false;
  if($('audio')) $('audio').pause();
  try{
    const response=await post('/api/generate', r, controller.signal);
    const reader=response.body.getReader(); const decoder=new TextDecoder();
    let pending='', done=false;
    function handle(line){
      if(!line.trim()) return;
      let e; try{e=JSON.parse(line);}catch{const err=Error('服务器返回无法解析的数据。'); err.detail=line.slice(0,4000); throw err;}
      if(e.type==='error'){const err=Error(e.message||'生成失败'); err.detail=e.detail||''; throw err;}
      if(e.type==='start') report('loading',`已连接 ${e.model} · ${e.location}…`,(e.warnings||[]).join('\n'));
      if(e.type==='done'){
        if(!e.audio) throw Error('没有收到音频。');
        done=true;
        const binary=Uint8Array.from(atob(e.audio),c=>c.charCodeAt(0));
        const blob=new Blob([binary],{type:e.mime||'audio/mpeg'});
        if(objectUrl) URL.revokeObjectURL(objectUrl); objectUrl=URL.createObjectURL(blob);
        if($('audio')) $('audio').src=objectUrl;
        if($('download')){
          const ext=(e.mime||'').includes('wav')?'wav':'mp3';
          $('download').href=objectUrl; $('download').download=`${active}-${Date.now()}.${ext}`;
        }
        savedConfig=Object.assign({page:active}, r);
        if($('result')) $('result').hidden=false;
        if($('empty-output')) $('empty-output').hidden=true;
        if($('status')) $('status').textContent='生成完成 · 请试听';
        const metrics=`耗时 ${e.seconds} 秒 · ${(e.bytes/1024).toFixed(1)} KB`;
        if($('metrics')) $('metrics').textContent=metrics;
        const lyrics=$('lyrics-out');
        if(lyrics){
          if(e.text){lyrics.hidden=false; lyrics.textContent=e.text;}
          else {lyrics.hidden=true; lyrics.textContent='';}
        }
        report('ok','生成成功。请试听。', metrics+(e.text?'\n'+e.text.slice(0,1200):''));
      }
    }
    while(true){
      const {value,done:ended}=await reader.read();
      if(ended) break;
      pending+=decoder.decode(value,{stream:true});
      const lines=pending.split('\n'); pending=lines.pop();
      for(const line of lines) handle(line);
    }
    pending+=decoder.decode();
    if(pending.trim()) handle(pending);
    if(!done) throw Error('连接提前结束，没有收到完成标记。请重新生成。');
  }catch(e){
    if($('result')) $('result').hidden=true;
    if($('empty-output')) $('empty-output').hidden=false;
    if($('status')) $('status').textContent=e.name==='AbortError'?'已停止':'未完成';
    fail(e,'生成失败');
  }finally{setBusy(false);}
}
function stopAll(){
  if(controller) controller.abort();
}
function bindWorkspace(root, spec){
  const click=(id, fn)=>{const el=root.querySelector(`[data-id="${id}"]`); if(el) el.addEventListener('click', fn);};
  click('primary', generate);
  click('preview', preview);
  click('stop', stopAll);
  root.querySelectorAll('[data-lang]').forEach(btn=>{
    btn.onclick=()=>{
      const box=root.querySelector('[data-id="prompt"]');
      if(!box) return;
      const phrase=` singing in ${btn.textContent}.`;
      if(!box.value.includes(phrase.trim())) box.value=(box.value.trim()+' '+phrase).trim();
    };
  });
  const file=root.querySelector('[data-id="image-file"]');
  if(file) file.onchange=async()=>{
    const MAX_IMAGES=10;
    const MAX_INLINE=100*1024*1024;
    const next=[...currentImages()];
    let total=next.reduce((n,item)=>{
      try{return n+Math.floor((item.data.length*3)/4);}catch{return n;}
    },0);
    for(const item of file.files||[]){
      if(next.length>=MAX_IMAGES){fail(Error(`最多 ${MAX_IMAGES} 张参考图（官方上限）。`),'张数超了'); break;}
      const mime=item.type==='image/jpg'?'image/jpeg':item.type;
      if(mime!=='image/jpeg'&&mime!=='image/png'){fail(Error('只要 JPEG 或 PNG。'),'图片格式'); continue;}
      if(total+item.size>MAX_INLINE){fail(Error('参考图合计超过 100 MB（Interactions 内联官方上限）。'),'体积超了'); continue;}
      const data=await new Promise((resolve,reject)=>{const reader=new FileReader(); reader.onload=()=>resolve(String(reader.result).split(',')[1]||''); reader.onerror=reject; reader.readAsDataURL(item);});
      next.push({mime_type:mime, data});
      total+=item.size;
    }
    file.value='';
    setImages(next);
  };
}
function page(name){
  if(!catalog) return;
  const engines=(catalog.workspaces||[]).map(item=>item.id);
  const isEngine=engines.includes(name);
  document.querySelectorAll('.engine-page').forEach(el=>el.hidden=el.id!=='page-'+name);
  ['learn','sources'].forEach(id=>{const el=document.getElementById(id); if(el) el.hidden=name!==id;});
  document.querySelectorAll('.nav').forEach(b=>b.classList.toggle('active',b.dataset.page===name));
  if(isEngine){
    active=name;
    if(!primed.has(name)){
      primed.add(name);
      fillModels(); renderSamples();
      const notice=$('connection'); if(notice) notice.textContent=connectionText();
    }
    renderImageThumbs();
  }
}
function inlineMarkdown(text){
  return escapeHtml(text)
    .replace(/`([^`]+)`/g,'<code>$1</code>')
    .replace(/\[([^\]]+)\]\((https:\/\/[^)]+)\)/g,'<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>')
    .replace(/\*\*([^*]+)\*\*/g,'<strong>$1</strong>');
}
function renderMarkdown(src){
  const lines=String(src||'').replace(/\r\n/g,'\n').split('\n');
  const out=[]; let i=0;
  while(i<lines.length){
    const line=lines[i];
    if(line.startsWith('```')){
      const buf=[]; i++; while(i<lines.length&&!lines[i].startsWith('```')) buf.push(lines[i++]); i++;
      out.push('<pre><code>'+escapeHtml(buf.join('\n'))+'</code></pre>'); continue;
    }
    if(line.startsWith('|')){
      const rows=[]; while(i<lines.length&&lines[i].startsWith('|')){if(!/^\|?\s*-+/.test(lines[i])) rows.push(lines[i]); i++;}
      out.push('<table>'+rows.map((row,index)=>{const cells=row.split('|').slice(1,-1).map(cell=>inlineMarkdown(cell.trim())); const tag=index?'td':'th'; return '<tr>'+cells.map(cell=>`<${tag}>${cell}</${tag}>`).join('')+'</tr>';}).join('')+'</table>'); continue;
    }
    if(/^---+$/.test(line.trim())){out.push('<hr>'); i++; continue;}
    const heading=line.match(/^(#{1,3})\s+(.*)$/); if(heading){out.push(`<h${heading[1].length}>${inlineMarkdown(heading[2])}</h${heading[1].length}>`); i++; continue;}
    if(/^\s*[-*]\s+/.test(line)){const items=[]; while(i<lines.length&&/^\s*[-*]\s+/.test(lines[i])){items.push('<li>'+inlineMarkdown(lines[i].replace(/^\s*[-*]\s+/,''))+'</li>'); i++;} out.push('<ul>'+items.join('')+'</ul>'); continue;}
    if(/^\s*\d+\.\s+/.test(line)){const items=[]; while(i<lines.length&&/^\s*\d+\.\s+/.test(lines[i])){items.push('<li>'+inlineMarkdown(lines[i].replace(/^\s*\d+\.\s+/,''))+'</li>'); i++;} out.push('<ol>'+items.join('')+'</ol>'); continue;}
    if(!line.trim()){i++; continue;}
    const buf=[line]; i++; while(i<lines.length&&lines[i].trim()&&!/^(#{1,3}\s|```|\||---|[-*]\s|\d+\.\s)/.test(lines[i])) buf.push(lines[i++]);
    out.push('<p>'+inlineMarkdown(buf.join(' '))+'</p>');
  }
  return out.join('');
}
async function loadDoc(kind,target){const response=await fetch('/api/doc/'+kind); if(!response.ok) throw Error('文档加载失败'); const data=await response.json(); $(target).innerHTML=renderMarkdown(data.text); return data.text;}
async function init(){
  try{
    catalog=await(await fetch('/api/catalog')).json();
    const host=$('workspaces');
    (catalog.workspaces||[]).forEach(spec=>{
      host.insertAdjacentHTML('beforeend', workspaceHTML(spec));
      bindWorkspace(document.getElementById('page-'+spec.id), spec);
    });
    $('model-rules').innerHTML=htmlTable(catalog.model_rules);
    $('compare-models').innerHTML=htmlTable(catalog.compare_models);
    $('compare-methods').innerHTML=htmlTable(catalog.compare_methods);
    $('compare-api').innerHTML=htmlTable(catalog.compare_api);
    $('compare-why').innerHTML=htmlTable(catalog.why_not_lyria);
    $('compare-fit').innerHTML=htmlTable(catalog.fit_guide);
    if($('session-limits')) $('session-limits').innerHTML=htmlTable(catalog.session_limits);
    if($('feature-value')) $('feature-value').innerHTML=htmlTable(catalog.feature_value);
    $('api-out-of-demo').innerHTML=htmlTable(catalog.api_out_of_demo);
    page('clip');
    try{await loadDoc('guide','guide-content');}catch(e){$('guide-content').textContent='学习指南加载失败：'+e.message;}
    try{
      const text=await loadDoc('sources','source-content'); const seen=new Set();
      for(const match of text.matchAll(/\[([^\]]+)\]\((https:\/\/[^)]+)\)/g)){
        if(seen.has(match[2])) continue; seen.add(match[2]);
        const a=document.createElement('a'); a.className='source-link'; a.href=match[2]; a.target='_blank'; a.rel='noopener noreferrer'; a.textContent=match[1]+' ↗';
        const sub=document.createElement('small'); sub.textContent=new URL(match[2]).hostname; a.append(sub); $('source-links').append(a);
      }
    }catch(e){$('source-content').textContent='官方资料加载失败：'+e.message;}
  }catch(e){fail(e,'初始化失败');}
}
document.querySelectorAll('[data-page]').forEach(b=>b.onclick=()=>page(b.dataset.page));
$('show-guide').onclick=()=>loadDoc('guide','guide-content').catch(e=>fail(e,'文档加载失败'));
$('show-readme').onclick=()=>loadDoc('readme','guide-content').catch(e=>fail(e,'文档加载失败'));
window.addEventListener('beforeunload',()=>{controller?.abort(); if(objectUrl) URL.revokeObjectURL(objectUrl);});
init();
