import '@fontsource-variable/dm-sans';
import './style.css';
import { MAX_BYTES, exportQueue, rankTransactions, sampleCSV } from './core.js';

const icons = {
  chart: '<path d="M4 4v16h16M8 14l4-5 4 2 4-7"/>',
  layers: '<path d="m12 3 9 5-9 5-9-5 9-5Zm-9 9 9 5 9-5M3 16l9 5 9-5"/>',
  book: '<path d="M12 5v15M3 4c4-1 6 0 9 1 3-1 5-2 9-1v15c-4-1-6 0-9 1-3-1-5-2-9-1Z"/>',
  upload: '<path d="M12 16V3m-5 5 5-5 5 5M4 15v6h16v-6"/>',
  arrow: '<path d="M4 12h16m-6-6 6 6-6 6"/>',
  check: '<path d="m5 12 4 4L19 6"/>',
  download: '<path d="M12 3v13m-5-5 5 5 5-5M4 16v5h16v-5"/>',
  lock: '<rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3m-4 5v2"/>',
  external: '<path d="M14 3h7v7m0-7L10 14M9 3H3v18h18v-6"/>',
};
const icon = name => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${icons[name] ?? icons.arrow}</svg>`;
const esc = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const num = n => n == null ? '—' : new Intl.NumberFormat('en-US', { maximumFractionDigits: 1 }).format(n);
const pct = n => n == null ? 'Not available' : `${(n * 100).toFixed(1)}%`;
let benchmark, profile, rows = null, source = 'benchmark', filename = '', capacity = 0.5, strategy, route = 'workbench', queuePage = 0, worker;
const app = document.querySelector('#app');

function shell() {
  app.innerHTML = `<aside class="sidebar" aria-label="Primary navigation">
    <a href="#workbench" class="brand" aria-label="Clearcut home"><img src="./favicon.svg" width="35" height="35" alt=""/>Clearcut<span class="brand-dot">.</span></a>
    <div class="workspace-label">FRAUD REVIEW WORKSPACE</div>
    <nav>${[['workbench','chart','Workbench'],['evidence','layers','The evidence'],['guide','book','How it works']].map(([id,ic,title]) => `<a href="#${id}" data-route="${id}" aria-label="${title}">${icon(ic)}<span>${title}</span></a>`).join('')}</nav>
    <div class="sidebar-bottom"><div class="privacy-mark">${icon('lock')}<span>Your data stays yours.</span></div><p>CSV analysis happens on your device. No accounts. No uploads to a server.</p><a href="https://github.com/brej-29/fraud-anomaly-lab" target="_blank" rel="noopener">View source ${icon('external')}</a><span class="version">CLEARCUT / 1.0</span></div>
  </aside>
  <div class="app-body"><header class="topbar"><div class="breadcrumb">Workspace <span>/</span> <strong id="crumb">Workbench</strong></div><div class="top-actions"><span class="local-status"><i></i><span id="connection-status">Local processing</span></span><button class="button primary" id="import-top">${icon('upload')}Import scored CSV</button></div></header>
  <main id="main" tabindex="-1"></main><footer class="footer"><span>A clearer decision, one review at a time.</span><span>Historical backtesting · No automated payment actions</span></footer></div>
  <input id="file-input" type="file" accept=".csv,text/csv" hidden/><div id="toast" class="toast" role="status" aria-live="polite"></div>`;
  document.querySelector('#import-top').onclick = openImport;
  document.querySelector('#file-input').onchange = async event => {
    const file = event.target.files[0];
    if (!file) return;
    if (file.size > MAX_BYTES) { announce('This file exceeds 12 MB. Split it into smaller batches.', true); return; }
    try { await importCSV(await file.text(), file.name, 'upload'); } catch (error) { announce(error.message, true); }
    event.target.value = '';
  };
  updateConnection();
}
function announce(message, error = false) {
  const el = document.querySelector('#toast');
  el.textContent = message;
  el.className = `toast visible ${error ? 'error' : ''}`;
  el.setAttribute('role', error ? 'alert' : 'status');
  clearTimeout(announce.timer);
  announce.timer = setTimeout(() => el.classList.remove('visible'), error ? 14000 : 6500);
}
function updateConnection() {
  const el = document.querySelector('#connection-status');
  if (el) el.textContent = navigator.onLine ? 'Local processing' : 'Offline · local tools ready';
}
window.addEventListener('online', updateConnection);
window.addEventListener('offline', updateConnection);
function openImport() {
  route = 'import';
  location.hash = 'import';
  render();
  document.querySelector('#import-heading')?.focus();
}
function current() { return profile.strategies.find(s => s.id === strategy) ?? profile.strategies[0]; }
function comparisonBaseline() {
  const chosen = current();
  return profile.strategies.find(s => s.id === (chosen.id === 'isolation' ? benchmark.selected : 'isolation'))
    ?? profile.strategies.find(s => s.id !== chosen.id) ?? chosen;
}
function point(s = current()) { return s.points[Math.round(capacity * 10)]; }
function origin() { return source === 'benchmark' ? 'ULB / Worldline · September 2013' : source === 'sample' ? 'Synthetic tutorial · 2,000 invented transactions' : filename; }
function render() {
  document.querySelectorAll('[data-route]').forEach(a => a.setAttribute('aria-current', a.dataset.route === route ? 'page' : 'false'));
  document.querySelector('#crumb').textContent = ({workbench:'Workbench',evidence:'The evidence',guide:'How it works',import:'Import data'})[route];
  const main = document.querySelector('#main');
  if (route === 'import') { main.innerHTML = importView(); bindImport(); return; }
  if (route === 'evidence') { main.innerHTML = accessibleTables(evidenceView()); return; }
  if (route === 'guide') { main.innerHTML = guideView(); bindGuide(); return; }
  main.innerHTML = accessibleTables(workbenchView());
  bindWorkbench();
}
function accessibleTables(html) { return html.replaceAll('<div class="table-scroll">', '<p class="table-scroll-hint">Scroll sideways to see every column <span aria-hidden="true">→</span></p><div class="table-scroll" tabindex="0" role="region" aria-label="Scrollable data table">'); }
function workbenchView() {
  const p = point(), s = current(), baseline = comparisonBaseline();
  return `<section class="page-heading"><div><h1>Make every review count.</h1><p>You have a limited queue. Find the trade-off you can stand behind.</p></div><button class="button quiet" id="load-sample">Try a sample ${icon('arrow')}</button></section>
  <section class="dataset-bar" aria-label="Active dataset"><div class="dataset-icon">${icon('layers')}</div><div><strong>${esc(origin())}</strong><span>${source === 'benchmark' ? 'Real historical holdout · aggregate results only' : source === 'sample' ? 'Invented data for learning the workflow · not benchmark evidence' : 'Private CSV · held in this tab only'}</span></div><span class="dataset-badge">${source === 'benchmark' ? 'BENCHMARK' : source === 'sample' ? 'SYNTHETIC' : 'YOUR DATA'}</span>${source !== 'benchmark' ? '<button class="text-button" id="reset">Return to benchmark</button>' : '<a href="#evidence" class="dataset-link">View methodology '+icon('arrow')+'</a>'}</section>
  <div class="metrics-strip" aria-label="Batch overview"><div><span>Transactions in batch</span><strong>${num(profile.rows)}</strong><small>${source === 'benchmark' ? 'Final 20% by transaction time' : 'Valid rows in this CSV'}</small></div><div><span>Confirmed fraud</span><strong>${num(profile.fraud)}<em>${profile.fraud == null ? 'unlabeled' : pct(profile.fraud/profile.rows)+' of batch'}</em></strong><small>${profile.fraud === null ? 'Labels needed to measure outcomes' : 'Historical labels, not predictions'}</small></div><div><span>Selected for review</span><strong id="metric-k">${num(p.k)}<em>${capacity.toFixed(1)}% capacity</em></strong><small>Highest-ranked transactions</small></div><div><span>Fraud captured</span><strong class="green" id="metric-recall">${pct(p.recall)}</strong><small id="metric-caught">${p.caught == null ? 'Add labels to measure capture' : `${num(p.caught)} of ${num(profile.fraud)} confirmed cases`}</small></div></div>
  <div class="workspace-grid"><section class="chart-panel panel" aria-labelledby="capture-heading"><div class="section-top"><div><h2 id="capture-heading">The capacity trade-off</h2><p>More reviews catch more fraud. At what cost?</p></div><span class="small-badge">${profile.fraud == null ? 'LABELS NEEDED' : 'OBSERVED RECALL'}</span></div><div id="capture-chart">${chartView()}</div><div class="chart-legend"><span><i style="--legend:#24745e"></i>${esc(s.name)}</span><span><i class="dashed" style="--legend:#a26c25"></i>${esc(baseline.name)}</span><span><i class="dashed" style="--legend:#78847f"></i>Random selection (expected)</span></div><div class="chart-note">${icon('book')}<span>${source === 'benchmark' ? 'Read this as a historical experiment, not a promise about your payments.' : profile.fraud == null ? 'Without labels, review counts are known; fraud outcomes are not.' : 'Labels are used for evaluation only. Ranking uses scores or amounts.'}</span></div></section>
  <section class="capacity-panel panel" aria-labelledby="capacity-heading"><h2 id="capacity-heading">Set your review budget</h2><p>Share of this batch you can review</p><div class="capacity-number"><output for="capacity" id="capacity-value">${capacity.toFixed(1)}<span>%</span></output><span>of transactions</span></div><label class="sr-only" for="capacity">Review capacity percent</label><input id="capacity" type="range" min="0" max="5" step="0.1" value="${capacity}"/><div class="range-labels"><span>0% · no reviews</span><span>5%</span></div><div class="budget-presets">${[.1,.5,1,2,5].map(v=>`<button data-budget="${v}" aria-pressed="${capacity===v}">${v}%</button>`).join('')}</div><label class="select-label" for="strategy">Ranking strategy</label><select id="strategy">${profile.strategies.map(x=>`<option value="${x.id}" ${s.id===x.id?'selected':''}>${esc(x.name)}</option>`).join('')}</select><div id="budget-outcome">${outcomeView()}</div><button class="button export-button" id="export">${icon('download')}${rows ? 'Export review queue' : 'Export budget report'}</button><p class="export-hint">${rows ? 'Ranked CSV · chosen strategy · this budget' : 'JSON · aggregate evidence · no transaction rows'}</p></section></div>
  <section class="comparison panel" aria-labelledby="comparison-heading"><div class="section-top"><div><h2 id="comparison-heading">Same budget. Different decisions.</h2><p>Every strategy gets exactly <span id="compare-k">${num(p.k)}</span> reviews. Nothing hidden in the denominator.</p></div><span class="small-badge">AT <span id="compare-percent">${capacity.toFixed(1)}</span>% CAPACITY</span></div><div class="table-scroll"><table><caption class="sr-only">Ranking performance at the selected review budget</caption><thead><tr><th scope="col">Ranking strategy</th><th scope="col">Fraud captured</th><th scope="col">Recall</th><th scope="col">Precision</th><th scope="col">Legitimate reviews</th></tr></thead><tbody id="comparison-rows">${comparisonRows()}</tbody></table></div></section>
  ${rows ? queueView() : `<section class="insight"><div class="insight-symbol">${icon('chart')}</div><div><h2>A good AUC doesn’t staff your queue.</h2><p>The original anomaly models missed every acceptance constraint. Clearcut makes the review cost visible before a threshold becomes a policy.</p></div><a href="#evidence">See what the numbers say ${icon('arrow')}</a></section>`}
  <section class="bottom-story"><div><h2>Why this exists</h2><p>Fraud teams don’t have unlimited attention. A model score becomes useful when you can see the cases it catches, the fraud it misses, and the legitimate payments it sends to review.</p></div><a class="button quiet" href="#guide">Understand the workflow ${icon('arrow')}</a></section>`;
}
function outcomeView() {
  const p = point();
  return `<div class="outcome-line"><span>Confirmed fraud in queue</span><strong>${num(p.caught)}</strong></div><div class="outcome-line"><span>Legitimate payments in queue</span><strong>${num(p.legitimate)}</strong></div><div class="outcome-bar" role="img" aria-label="${p.caught == null ? 'Outcomes unavailable without labels' : `${num(p.caught)} fraud, ${num(p.legitimate)} legitimate reviews`}"><span style="width:${p.precision == null ? 0 : p.precision*100}%"></span></div><div class="outcome-line muted"><span>Fraud left outside queue</span><strong>${num(p.missed)}</strong></div><p class="uncertainty">${p.interval ? `Recall interval: ${pct(p.interval[0])}–${pct(p.interval[1])}<br/>95% Wilson · historical sample uncertainty` : profile.fraud === 0 ? 'No fraud labels in this batch. Recall is undefined.' : 'No fraud outcomes claimed without labels.'}</p>`;
}
function chartView() {
  if (profile.fraud === null || profile.fraud === 0) return `<div class="chart-empty">${icon('chart')}<h3>${profile.fraud === 0 ? 'No confirmed fraud in this batch' : 'Scores can rank. Labels measure.'}</h3><p>${profile.fraud === 0 ? 'Recall is undefined when there are no positive labels. You can still inspect and export a queue.' : 'Add a label column with 0 for legitimate and 1 for confirmed fraud to see the capture curve. Your ranked queue is ready below.'}</p></div>`;
  const narrow = window.matchMedia('(max-width:700px)').matches;
  const w=narrow?360:740,h=narrow?270:300,left=narrow?43:48,right=narrow?14:22,top=22,bottom=44;
  const x=v=>left+v/5*(w-left-right), y=v=>h-bottom-v*(h-top-bottom);
  const s=current(), p=point(), baseline=comparisonBaseline();
  const path = a=>a.map((q,i)=>`${i?'L':'M'}${x(q.percent).toFixed(2)},${y(q.recall??0).toFixed(2)}`).join(' ');
  return `<svg class="capture-svg" viewBox="0 0 ${w} ${h}" role="img" aria-labelledby="chart-title chart-desc"><title id="chart-title">Fraud capture against review capacity</title><desc id="chart-desc">At ${capacity.toFixed(1)} percent capacity, ${esc(s.name)} captures ${pct(p.recall)} of confirmed fraud. Exact counts are in the comparison table.</desc><defs><linearGradient id="capture-fill" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#b9d6c0" stop-opacity=".44"/><stop offset="1" stop-color="#b9d6c0" stop-opacity=".03"/></linearGradient></defs>
  ${[0,.25,.5,.75,1].map(v=>`<line x1="${left}" x2="${w-right}" y1="${y(v)}" y2="${y(v)}" class="grid-line"/><text x="${left-12}" y="${y(v)+4}" text-anchor="end" class="axis">${v*100}%</text>`).join('')}
  ${[0,1,2,3,4,5].map(v=>`<text x="${x(v)}" y="${h-18}" text-anchor="middle" class="axis">${v}%</text>`).join('')}
  <path d="${path(s.points)} L${x(5)},${y(0)} L${x(0)},${y(0)}Z" fill="url(#capture-fill)"/>
  <path d="M${x(0)},${y(0)} L${x(5)},${y(.05)}" fill="none" stroke="#78847f" stroke-width="1.4" stroke-dasharray="3 5"/>
  <path d="${path(baseline.points)}" fill="none" stroke="#a26c25" stroke-width="2" stroke-dasharray="6 5" stroke-linejoin="round"/>
  <path d="${path(s.points)}" fill="none" stroke="#24745e" stroke-width="3" stroke-linejoin="round"/>
  <line x1="${x(capacity)}" x2="${x(capacity)}" y1="${top}" y2="${y(0)}" stroke="#2e614f" stroke-dasharray="3 5" opacity=".7"/>
  <circle cx="${x(capacity)}" cy="${y(p.recall??0)}" r="6" fill="#24745e" stroke="#fff" stroke-width="3"/>
  <rect x="${Math.min(w-110,Math.max(left,x(capacity)-40))}" y="${Math.max(2,y(p.recall??0)-34)}" width="84" height="23" rx="4" fill="#173c35"/><text x="${Math.min(w-110,Math.max(left,x(capacity)-40))+42}" y="${Math.max(2,y(p.recall??0)-34)+16}" text-anchor="middle" fill="#fff" font-size="11" font-weight="600">${pct(p.recall)} captured</text>
  </svg><div class="axis-label">Review capacity · share of batch</div>`;
}
function comparisonRows() {
  const strategies = [...profile.strategies];
  const random = {id:'random',name:'Random selection',points:Array.from({length:51},(_,i)=>{const k=Math.floor(profile.rows*i/1000+1e-9),c=profile.fraud==null?null:k*profile.fraud/profile.rows;return {k,caught:c,recall:profile.fraud? k/profile.rows:null,precision:profile.fraud==null||!k?null:profile.fraud/profile.rows,legitimate:c==null?null:k-c};})};
  return [...strategies,random].map(s=>{const p=point(s);return `<tr class="${strategy===s.id?'selected-row':''}"><th scope="row"><span class="strategy-dot ${s.id==='isolation'?'ochre':s.id==='amount'?'gray':''}"></span>${esc(s.name)}${strategy===s.id?'<span class="selected-label">Selected</span>':''}${s.id==='random'?'<small>Expected, not an actual queue</small>':''}</th><td>${num(p.caught)}${s.id==='random'&&p.caught!=null?'<span class="expected"> expected</span>':''}</td><td><span class="recall-cell">${pct(p.recall)}</span></td><td>${pct(p.precision)}</td><td>${num(p.legitimate)}</td></tr>`;}).join('');
}
function queueView() {
  const k=point().k, selected=rankTransactions(rows,strategy).slice(0,k), visible=selected.slice(queuePage*10,queuePage*10+10);
  return `<section class="panel queue"><div class="section-top"><div><h2 tabindex="-1" id="queue-heading">Your review queue</h2><p>${source==='sample'?'Synthetic tutorial rows':'Your private rows'} · ${strategy==='amount'?'larger amounts':'larger scores'} rank first · ${strategy==='amount'?'amount':'score'} ties preserve file order</p></div><span>${num(k)} selected</span></div>${k?`<div class="table-scroll"><table><caption class="sr-only">Selected transactions in descending ranking order</caption><thead><tr><th scope="col">Rank</th><th scope="col">Transaction</th><th scope="col">Score</th><th scope="col">Amount*</th><th scope="col">Known outcome</th></tr></thead><tbody>${visible.map((r,i)=>`<tr><td>${queuePage*10+i+1}</td><th scope="row">${esc(r.id)}</th><td>${num(r.score)}</td><td>${num(r.amount)}</td><td><span class="outcome-tag ${r.label===1?'fraud':''}">${r.label===null?'Unlabeled':r.label===1?'Confirmed fraud':'Legitimate'}</span></td></tr>`).join('')}</tbody></table></div><div class="queue-footer"><span>*Original amount units; no currency conversion.</span><div><button class="button quiet" id="prev-page" ${queuePage===0?'disabled':''}>Previous</button><span>Page ${queuePage+1} of ${Math.max(1,Math.ceil(k/10))}</span><button class="button quiet" id="next-page" ${(queuePage+1)*10>=k?'disabled':''}>Next</button></div></div>`:'<div class="queue-empty"><h3>No reviews at this budget</h3><p>Increase review capacity to select the highest-ranked transactions.</p></div>'}</section>`;
}
function bindWorkbench() {
  document.querySelector('#load-sample').onclick=()=>importCSV(sampleCSV(),'Synthetic tutorial','sample');
  document.querySelector('#reset')?.addEventListener('click',reset);
  document.querySelector('#capacity').oninput=e=>setCapacity(Number(e.target.value));
  document.querySelectorAll('[data-budget]').forEach(b=>b.onclick=()=>setCapacity(Number(b.dataset.budget)));
  document.querySelector('#strategy').onchange=e=>{strategy=e.target.value;queuePage=0;render();document.querySelector('#strategy').focus();};
  document.querySelector('#export').onclick=()=>{
    if(rows) download(exportQueue(rows,point().k,strategy),'clearcut-review-queue.csv','text/csv');
    else download(JSON.stringify({source:benchmark.source,dataset_sha256:benchmark.dataset_sha256,capacity_percent:capacity,strategy:current().name,metrics:point(),limits:'Historical ULB aggregate holdout. No live payment action or future performance guarantee.'},null,2),'clearcut-budget-report.json','application/json');
    announce(rows?'Review queue exported. Keep the file private.':'Budget report exported with source and uncertainty.');
  };
  document.querySelector('#prev-page')?.addEventListener('click',()=>{queuePage--;refreshQueue('prev-page');});
  document.querySelector('#next-page')?.addEventListener('click',()=>{queuePage++;refreshQueue('next-page');});
}
function refreshQueue(focusId) { const el=document.querySelector('.queue'); if(el){el.outerHTML=accessibleTables(queueView());bindWorkbench();if(focusId){const target=document.getElementById(focusId);(target&&!target.disabled?target:document.querySelector('#queue-heading')).focus({preventScroll:true});}} }
function setCapacity(value) {
  capacity=value;queuePage=0;
  const p=point();
  document.querySelector('#capacity').value=value;
  document.querySelector('#capacity-value').innerHTML=`${value.toFixed(1)}<span>%</span>`;
  document.querySelector('#metric-k').innerHTML=`${num(p.k)}<em>${value.toFixed(1)}% capacity</em>`;
  document.querySelector('#metric-recall').textContent=pct(p.recall);
  document.querySelector('#metric-caught').textContent=p.caught==null?'Add labels to measure capture':`${num(p.caught)} of ${num(profile.fraud)} confirmed cases`;
  document.querySelector('#capture-chart').innerHTML=chartView();
  document.querySelector('#budget-outcome').innerHTML=outcomeView();
  document.querySelector('#compare-k').textContent=num(p.k);
  document.querySelector('#compare-percent').textContent=value.toFixed(1);
  document.querySelector('#comparison-rows').innerHTML=comparisonRows();
  document.querySelectorAll('[data-budget]').forEach(b=>b.setAttribute('aria-pressed',Number(b.dataset.budget)===value));
  refreshQueue();
}
function importView() {
  return `<section class="page-heading"><div><h1 id="import-heading" tabindex="-1">Bring your scores. Keep your data.</h1><p>Find the right review budget for your own batch, entirely on your device.</p></div></section><div class="import-grid"><section class="upload-panel panel" id="drop-zone"><div class="upload-symbol">${icon('upload')}</div><h2>Open a scored CSV</h2><p>Drop a file here, or choose it from your device.<br/>Up to 100,000 rows · 12 MB maximum</p><button class="button primary" id="choose-file">Choose CSV file</button><span class="privacy-caption">${icon('lock')}Processed in this tab. Never sent to a server.</span><div id="import-status" role="status" aria-live="polite"></div></section><section class="schema-panel"><h2>A small file. A clear contract.</h2><dl><div><dt>score <span>required</span></dt><dd>Any finite number. Higher means more suspicious. Scores do not need to be probabilities.</dd></div><div><dt>amount <span>required</span></dt><dd>Non-negative transaction value, in one consistent unit. Used by the amount baseline.</dd></div><div><dt>label <span>optional</span></dt><dd>0 = legitimate, 1 = confirmed fraud. Include matured labels to measure recall and precision.</dd></div><div><dt>id <span>optional</span></dt><dd>A unique transaction reference. Use pseudonymous identifiers; avoid personal information.</dd></div></dl></section></div><section class="sample-panel panel"><div><h2>Just looking around?</h2><p>Learn the import → budget → export workflow with an explicitly synthetic 2,000-row sample.</p></div><div class="sample-actions"><button class="button quiet" id="download-sample">${icon('download')}Download sample CSV</button><button class="button primary" id="try-sample">Use synthetic sample ${icon('arrow')}</button></div></section><p class="fine-print">Files are held in memory until you close or reload this tab. All rows must be valid; we reject the whole batch rather than silently dropping errors. Rankings do not use the label column. A top-k batch is retrospective, not a live approval threshold.</p>`;
}
function bindImport() {
  document.querySelector('#choose-file').onclick=()=>document.querySelector('#file-input').click();
  document.querySelector('#try-sample').onclick=()=>importCSV(sampleCSV(),'Synthetic tutorial','sample');
  document.querySelector('#download-sample').onclick=()=>download(sampleCSV(),'clearcut-synthetic-sample.csv','text/csv');
  const zone=document.querySelector('#drop-zone');
  zone.ondragover=e=>{e.preventDefault();zone.classList.add('drag-over');};
  zone.ondragleave=()=>zone.classList.remove('drag-over');
  zone.ondrop=async e=>{e.preventDefault();zone.classList.remove('drag-over');const f=e.dataTransfer.files[0];if(!f)return;if(f.size>MAX_BYTES){announce('This file exceeds 12 MB. Split it into smaller batches.',true);return;}try{await importCSV(await f.text(),f.name,'upload');}catch(error){announce(error.message,true);}};
}
async function importCSV(text,name,type) {
  if(worker) return;
  const status=document.querySelector('#import-status');
  if(status) status.innerHTML='<div class="skeleton"></div><p>Validating every row and calculating the trade-off…</p>';
  const slow=setTimeout(()=>{if(status)status.innerHTML='<p>Still working locally. Large batches can take a moment; your file stays on this device.</p>';},1800);
  worker=new Worker(new URL('./worker.js',import.meta.url),{type:'module'});
  try {
    const result=await new Promise((resolve,reject)=>{worker.onmessage=e=>e.data.error?reject(new Error(e.data.error)):resolve(e.data);worker.onerror=()=>reject(new Error('The local processor could not start. Reload this page and try again.'));worker.postMessage(text);});
    rows=result.rows;profile=result.profile;strategy='score';source=type;filename=name;queuePage=0;route='workbench';
    if(location.hash!=='#workbench')location.hash='workbench';else render();
    announce(type==='sample'?'Synthetic sample loaded. These outcomes are invented for the tutorial.':`${num(rows.length)} valid rows loaded privately. Nothing was uploaded.`);
  } catch(error) { if(status){status.innerHTML='';status.textContent=error.message;status.setAttribute('role','alert');}announce(error.message,true); }
  finally {clearTimeout(slow);worker.terminate();worker=null;}
}
function reset(){rows=null;profile=benchmark;source='benchmark';strategy=benchmark.selected;queuePage=0;render();announce('Returned to the real historical benchmark.');}
function download(content,name,type){const url=URL.createObjectURL(new Blob([content],{type})),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
function evidenceView(){
  const selected=benchmark.strategies.find(s=>s.id===benchmark.selected), base=benchmark.strategies.find(s=>s.id==='isolation'),p=selected.primary;
  return `<section class="page-heading"><div><h1>Evidence, with the edges left in.</h1><p>A reproducible experiment. Useful results. Explicit limits.</p></div><a class="button quiet" href="https://github.com/brej-29/fraud-anomaly-lab/blob/main/docs/WHY.md" target="_blank" rel="noopener">Read the full case study ${icon('external')}</a></section>
  <section class="evidence-hero"><div><h2>${pct(p.recall)} of confirmed fraud.<br/>${num(p.k)} reviews.</h2><p>At 0.5% capacity, ${esc(selected.name)} finds ${p.caught} of ${benchmark.fraud} known fraud cases in ${num(benchmark.rows)} historical test transactions. ${p.legitimate} legitimate payments enter the same queue.</p><span class="result-label">${benchmark.primary_success?'Predeclared target met':'Predeclared target not met'} · retrospective experiment</span></div><div class="evidence-note"><h3>The target, set first</h3><p>At 0.5% review capacity: ≥60% recall, ≥15% precision, and ≥10 percentage points of recall above Isolation Forest.</p><p>Observed lift: <strong>${((p.recall-base.primary.recall)*100).toFixed(1)} points</strong>. Paired bootstrap 95% interval: ${benchmark.recall_difference_interval.map(v=>(v*100).toFixed(1)).join('–')} points.</p></div></section>
  <section class="panel evidence-section"><h2>Every candidate, at the same operating point</h2><div class="table-scroll"><table><thead><tr><th scope="col">Strategy</th><th scope="col">Average precision</th><th scope="col">ROC-AUC</th><th scope="col">Recall @ 0.5%</th><th scope="col">Precision @ 0.5%</th></tr></thead><tbody>${benchmark.strategies.map(s=>`<tr><th scope="row">${esc(s.name)}</th><td>${s.average_precision.toFixed(4)}</td><td>${s.roc_auc.toFixed(4)}</td><td>${pct(s.primary.recall)}</td><td>${pct(s.primary.precision)}</td></tr>`).join('')}</tbody></table></div><p>Average precision is the step-integral AP metric, not trapezoidal PR-AUC. The no-amount model is an ablation. Selection uses validation AP only, before comparing test results.</p></section>
  <div class="evidence-columns"><section><h2>Time moves forward. So does the split.</h2><div class="split-bar"><span>Train 60%</span><span>Validate 20%</span><span>Test 20%</span></div><p>Stable chronological sorting. Boundary ties stay in the later split. Scaling is fitted only on training rows. Models use V1–V28 and, where included, log-transformed amount.</p><p>The supervised model has fraud labels; Isolation Forest sees only normal training examples. This compares two operating regimes, not two equally informed algorithms.</p></section><section><h2>What the benchmark cannot tell you</h2><p>These are two days of European payments from 2013. There is no merchant context, card identity, production drift, review time, or downstream recovery outcome. Capture is not money saved.</p><p>Intervals describe sampling uncertainty in historical labels. Temporal dependence, delayed labels, and selection bias make production uncertainty larger.</p></section></div>
  <section class="panel evidence-section"><h2>Where the selected model misses</h2><div class="table-scroll"><table><thead><tr><th scope="col">Test segment</th><th scope="col">Confirmed fraud</th><th scope="col">Caught</th><th scope="col">Missed</th><th scope="col">Recall</th></tr></thead><tbody>${benchmark.error_analysis.map(e=>`<tr><th scope="row">${esc(e.segment)}</th><td>${e.fraud}</td><td>${e.caught}</td><td>${e.missed}</td><td>${pct(e.recall)}</td></tr>`).join('')}</tbody></table></div><p>Segment rows overlap: amount buckets and chronological halves are two separate analyses. Duplicate-feature overlap audit: train→test ${benchmark.duplicate_feature_overlap.train_to_test}; validation→test ${benchmark.duplicate_feature_overlap.val_to_test}. Removing earlier-seen feature rows leaves ${num(benchmark.novel_test.rows)} test rows and ${pct(benchmark.novel_test.recall)} recall.</p></section>
  <section class="bottom-story"><div><h2>Reproduce it. Challenge it.</h2><p>Three seeds, fixed configuration, a dataset checksum, uncertainty, and negative results are all in the repository. The live app publishes aggregate statistics only.</p><a href="${benchmark.source}" target="_blank" rel="noopener">Dataset: Worldline / ULB, September 2013 ${icon('external')}</a></div><a class="button primary" href="https://github.com/brej-29/fraud-anomaly-lab/blob/main/docs/EVALUATION_PLAN.md" target="_blank" rel="noopener">Read the evaluation plan ${icon('external')}</a></section>`;
}
function guideView(){return `<section class="page-heading"><div><h1>A threshold is a decision.</h1><p>Make it with a denominator, a review budget, and a clear view of the misses.</p></div></section><div class="guide-intro"><h2>Why Clearcut exists</h2><p>The original project compared anomaly detectors. Its models could rank fraud above ordinary transactions and still flood a small review queue with legitimate payments. That gap is the useful problem: translate model quality into the workload a team can actually handle.</p><p><a href="https://docs.stripe.com/radar/transaction-reviews" target="_blank" rel="noopener">Stripe’s review guidance</a> describes the same operational tension: human review can add value, while slow review can delay legitimate customers. Clearcut helps examine the trade-off in historical scored batches.</p></div><section class="workflow"><article><span class="step-number">1</span><h2>Start with scores</h2><p>Use the built-in real benchmark or open a CSV with scores from your existing model. Higher scores must mean greater suspicion. Clearcut does not create fraud scores.</p></article><article><span class="step-number">2</span><h2>Put a limit on attention</h2><p>Choose the share of a batch your team can review. We rank descending and take exactly floor(batch size × capacity). Tied scores keep their original file order.</p></article><article><span class="step-number">3</span><h2>See the cost. Take the queue.</h2><p>With matured fraud labels, inspect captured fraud, misses, and legitimate reviews. Compare amount ranking at the same budget, then export the rows for your review process.</p></article></section><section class="definitions panel"><h2>Three numbers worth separating</h2><dl><div><dt>Recall</dt><dd>Captured fraud ÷ all confirmed fraud. How much known fraud made it into the queue?</dd></div><div><dt>Precision</dt><dd>Captured fraud ÷ selected reviews. How often does a review encounter confirmed fraud?</dd></div><div><dt>Review capacity</dt><dd>Selected reviews ÷ all transactions. What share of the batch can your team inspect?</dd></div></dl></section><section class="guide-bottom"><div><h2>Private by architecture</h2><p>No sign-in, analytics, remote model, or upload endpoint. Parsing happens in a web worker on your device; files are held in memory. Close this tab to clear them. First load needs internet; the current loaded tab can calculate while offline.</p></div><div><h2>A sandbox for policy, not payment actions</h2><p>This is a retrospective batch tool. It does not block, approve, refund, or investigate transactions. Scores are not treated as calibrated probabilities. A prospective threshold must be validated on your own recent, matured labels.</p></div></section><button class="button primary" id="guide-import">Explore your own scores ${icon('arrow')}</button>`;}
function bindGuide(){document.querySelector('#guide-import').onclick=openImport;}

async function start(){
  try {
    const response=await fetch('./benchmark.json');
    if(!response.ok)throw new Error('The benchmark could not be loaded.');
    benchmark=await response.json();profile=benchmark;strategy=benchmark.selected;
    shell();
    const navigate=()=>{route=['workbench','evidence','guide','import'].includes(location.hash.slice(1))?location.hash.slice(1):'workbench';render();};
    window.addEventListener('hashchange',()=>{navigate();document.querySelector('#main').focus({preventScroll:true});window.scrollTo(0,0);});
    navigate();
  }catch(error){app.innerHTML=`<main class="boot"><h1>The workbench couldn’t load.</h1><p>Check your connection and reload to retrieve the benchmark. Your private files have not been sent anywhere.</p><button class="button primary" id="retry">Reload workbench</button></main>`;document.querySelector('#retry').onclick=()=>location.reload();}
}
start();
