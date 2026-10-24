/* SparkCert UI — dependency-free, local-only SPA. No analytics or third-party assets. */
'use strict';
const TOKEN = document.querySelector('meta[name="sparkcert-token"]').content;
const $ = selector => document.querySelector(selector);
const icon = (name, extra = '') => `<svg class="${extra}" aria-hidden="true"><use href="#i-${name}"/></svg>`;
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt = value => value == null ? '—' : String(value);
const when = iso => { try { return new Date(iso).toLocaleString([], {dateStyle:'medium',timeStyle:'short'}); } catch {return iso;} };
const state = {page:'overview',overview:{devices:[],recent_runs:[],device_count:0,run_count:0},devices:[],reports:[],aliases:[],cases:[], mode:'manual',selectedId:'',lastProbe:null,lastRun:null,filter:'all',fileView:null,working:false};

async function api(path, options={}) {
  const headers = {'X-SparkCert-Token':TOKEN, ...(options.body && !(options.body instanceof FormData) ? {'Content-Type':'application/json'}:{}),...options.headers};
  let response;
  try { response=await fetch('/api'+path,{...options,headers}); }
  catch {throw new Error('SparkCert service is unreachable. Restart the local application.');}
  if (!response.ok) {
    let err;
    try {const x=await response.json(); err=typeof x.detail === 'string' ? x.detail : JSON.stringify(x.detail);} catch {err=await response.text();}
    throw new Error(err || `Request failed (${response.status})`);
  }
  if(options.raw) return response;
  return response.json();
}
function toast(message,error=false) {
  const el=document.createElement('div');el.className='toast'+(error?' error':'');el.textContent=message;
  $('#toast-region').appendChild(el);setTimeout(()=>el.remove(),5700);
}
function handleError(error) {console.error(error);toast(error.message||String(error),true);}
function head(kicker,title,sub,actions='') {return `<div class="heading-row"><div><p class="eyebrow">${esc(kicker)}</p><h1>${esc(title)}</h1><p>${esc(sub)}</p></div><div class="heading-actions">${actions}</div></div>`;}
const button=(label,action,variant='')=>`<button class="btn ${variant}" data-action="${action}">${label}</button>`;
const empty=(sym,title,desc,action='')=>`<div class="empty"><div class="empty-icon">${icon(sym)}</div><h3>${esc(title)}</h3><p>${esc(desc)}</p>${action}</div>`;
function scoreTag(score) {return `<span class="tag ${score>=80?'tag-good':score>=50?'tag-warn':'tag-bad'}">${score==null?'No score':`${Math.round(score)}% checks passed`}</span>`;}
function ring(score) {return `<div class="score-ring" style="--percent:${Math.max(0,Math.min(100,score||0))}%"><strong>${score==null?'—':`${Math.round(score)}%`}</strong></div>`;}
async function loadBase() {
  const [overview,reports]=await Promise.all([api('/overview'),api('/reports')]);
  state.overview=overview;state.devices=overview.devices;state.reports=reports;
  $('#nav-device-count').textContent=state.devices.length;
  $('#side-version').textContent=overview.version;
}
async function navigate(page) {
  state.page=page;
  document.querySelectorAll('[data-page]').forEach(e=>e.classList.toggle('active',e.dataset.page===page));
  $('#breadcrumb-current').textContent=({overview:'Overview',connections:'Connections',evaluations:'AI Evaluations',reports:'Evidence Reports',about:'Settings & Security'})[page]||page;
  $('#sidebar').classList.remove('open');
  if(page==='connections') await getAliases();
  if(page==='evaluations' && !state.cases.length) state.cases=await api('/evaluation/cases');
  render();
}
function render() {
  const content=$('#content');
  if(state.page==='overview') content.innerHTML=overviewPage();
  if(state.page==='connections') content.innerHTML=connectionsPage();
  if(state.page==='evaluations') content.innerHTML=evaluationsPage();
  if(state.page==='reports') content.innerHTML=reportsPage();
  if(state.page==='about') content.innerHTML=aboutPage();
}
function metric(label,value,sub,sym) {return `<div class="card metric"><div class="metric-top"><span>${label}</span><div class="metric-icon">${icon(sym)}</div></div><div class="metric-value">${value}</div><div class="metric-sub">${sub}</div></div>`;}
function deviceRow(d) {return `<div class="device-row"><div class="device-leading"><div class="device-icon">${icon('server')}</div><div><strong>${esc(d.name)}</strong><small>${esc(d.ssh_alias ? 'SSH alias: '+d.ssh_alias : d.username+'@'+d.host+':'+d.port)}</small></div></div><button class="btn btn-small" data-action="select-device" data-id="${esc(d.id)}">Open ${icon('arrow')}</button></div>`;}
function overviewPage() {
  const o=state.overview; const latest=o.recent_runs[0];
  return `${head('Operations center','Your AI infrastructure, under control.','A private workspace for connecting devices, validating AI deployments, and keeping evidence.',
    button(`${icon('plus')} Add device`,'to-connections','btn-primary') + button(`${icon('activity')} New evaluation`,'to-evaluations'))}
    <div class="stats">${metric('Managed devices',o.device_count,'Saved SSH connection profiles','server')}
    ${metric('Completed assessments',o.run_count,'Measured, not simulated','activity')}
    ${metric('Latest pass rate',latest&&latest.score!=null?`${Math.round(latest.score)}%`:'—',latest?'From most recent assessment':'No assessment data yet','shield')}
    ${metric('SSH client',o.ssh_available?'<span style="color:var(--accent)">Ready</span>':'<span style="color:var(--red)">Missing</span>',o.ssh_available?'System OpenSSH detected':'Install OpenSSH client to connect','terminal')}</div>
    <div class="hero-banner"><div><p class="eyebrow">VALIDATION BEFORE DEPLOYMENT</p><h2>Make every AI release a decision backed by evidence.</h2><p>Run real infrastructure checks and controlled model evaluations, retain test outcomes, then generate an auditable PDF. Everything is orchestrated from this machine.</p></div><div class="hero-decoration">SC</div></div>
    <div class="overview-grid"><section class="card"><div class="section-top"><h2 class="section-title">Managed connections</h2><button class="section-link" data-action="to-connections">View all →</button></div>${o.devices.length?`<div class="device-list">${o.devices.slice(0,4).map(deviceRow).join('')}</div>`:empty('server','No DGX Sparks connected yet','Add a device using its IP address or import a familiar VS Code SSH host profile.',button('Connect a device','to-connections','btn-primary'))}</section>
    <section class="card"><div class="section-top"><h2 class="section-title">Getting started</h2><span class="tag">3 STEPS</span></div><div class="workflow">
      <div class="work-step"><span class="step-no">01</span><div><strong>Connect your DGX Spark</strong><p>Import ~/.ssh/config or add an SSH profile using a host and username.</p></div></div>
      <div class="work-step"><span class="step-no">02</span><div><strong>Measure infrastructure readiness</strong><p>Query GPU visibility, host health, memory headroom, storage, and runtime prerequisites.</p></div></div>
      <div class="work-step"><span class="step-no">03</span><div><strong>Validate your AI API</strong><p>Run live deterministic checks against an OpenAI-compatible chat endpoint and export evidence.</p></div></div>
    </div><div class="hr"></div><button class="btn btn-wide" data-action="to-evaluations">Explore evaluation suite ${icon('arrow')}</button></section></div>
    <section class="card"><div class="section-top"><h2 class="section-title">Recent assessments</h2><button class="section-link" data-action="to-reports">All reports →</button></div>
      ${o.recent_runs.length?`<div class="table-wrap"><table class="table"><thead><tr><th>Assessment</th><th>Target</th><th>Executed</th><th>Outcome</th><th></th></tr></thead><tbody>${o.recent_runs.slice(0,5).map(r=>`<tr><td>${esc(r.kind==='infrastructure'?'Infrastructure readiness':'Model behavior evaluation')}</td><td>${esc(r.device_name)}</td><td>${esc(when(r.created_at))}</td><td>${scoreTag(r.score)}</td><td><button class="btn btn-small" data-action="show-report" data-id="${esc(r.id)}">View</button></td></tr>`).join('')}</tbody></table></div>`:empty('file','No assessment history','Your first completed assessment will appear here, with verifiable results and a downloadable PDF.')}
    </section>`;
}
function connectionForm() {
  let aliasOptions=state.aliases.length?state.aliases.map(a=>`<option value="${esc(a.alias)}">${esc(a.alias)}</option>`).join(''):'<option value="" disabled>No SSH aliases discovered</option>';
  return `<form id="device-form"><div class="section-top"><h2 class="section-title">Add SSH connection</h2><span class="tag">OPENSSH</span></div><p class="muted-sm" style="margin-top:-7px">Add a secure connection profile. Credentials are not stored by SparkCert.</p>
    <div class="divider-label">CONNECTION SOURCE</div><div class="segmented"><button type="button" class="${state.mode==='manual'?'selected':''}" data-action="mode-manual">${icon('plus')} Manual</button><button type="button" class="${state.mode==='alias'?'selected':''}" data-action="mode-alias">${icon('terminal')} SSH config import</button></div>
    <div class="top-space form-grid"><div class="field" style="grid-column:1/-1"><label for="conn-name">Display name</label><input id="conn-name" name="name" placeholder="e.g. DGX Spark · AI Lab" maxlength="80" required /></div>
    ${state.mode==='manual'?`<div class="field"><label for="conn-host">Host / IP address</label><input id="conn-host" name="host" placeholder="192.168.1.20" required autocomplete="off" /></div><div class="field"><label for="conn-user">SSH username</label><input id="conn-user" name="username" placeholder="ubuntu" autocomplete="username" /></div><div class="field"><label for="conn-port">SSH port</label><input id="conn-port" name="port" type="number" value="22" min="1" max="65535" /></div><div class="field"><label for="conn-key">Private key path (optional)</label><input id="conn-key" name="identity_file" placeholder="~/.ssh/id_ed25519" /><span class="hint">Leave blank for your SSH agent/default key.</span></div>`:`<div class="field" style="grid-column:1/-1"><label for="conn-alias">Existing SSH profile</label><select name="ssh_alias" id="conn-alias" required><option value="">Choose an alias from ~/.ssh/config</option>${aliasOptions}</select><span class="hint">Uses the same SSH config, key, ProxyJump and known_hosts as your terminal or VS Code.</span></div>`}
    </div><div class="form-divider"></div><div class="info-ribbon">${icon('lock')}<div><strong>SSH security is enforced</strong><p>Strict host-key verification and non-interactive key or SSH-agent authentication. Password-based first-time login is performed in your trusted system terminal.</p></div></div><button class="btn btn-primary btn-wide" type="submit" id="save-device">${icon('plus')} Save connection profile</button></form>`;
}
function connectionsPage() {
  let selected=state.devices.find(d=>d.id===state.selectedId);
  return `${head('Device management','Connections & diagnostics','Use existing OpenSSH/VS Code profiles, direct Ethernet, local network, or VPN hostnames.',button(`${icon('refresh')} Refresh profiles`,'reload-aliases'))}
    <div class="connection-layout"><section class="card">${connectionForm()}</section><section class="card"><div class="section-top"><h2 class="section-title">Saved devices <span class="muted2">(${state.devices.length})</span></h2>${state.devices.length?'<span class="tag tag-good">LOCAL PROFILES</span>':''}</div>
      ${state.devices.length?`<div class="connection-list">${state.devices.map(d=>`<div class="connection-card"><div class="device-leading"><div class="device-icon">${icon('server')}</div><div><h3>${esc(d.name)}</h3><p>${esc(d.ssh_alias||`${d.username||'default user'}@${d.host}:${d.port}`)}</p></div></div><div class="connection-card-actions"><button class="icon-button" aria-label="Open SSH terminal" title="Open interactive SSH terminal" data-action="terminal" data-id="${esc(d.id)}">${icon('terminal')}</button><button class="icon-button" aria-label="Browse files" title="Browse remote home" data-action="browse" data-id="${esc(d.id)}">${icon('file')}</button><button class="icon-button" aria-label="Diagnostics" title="Connect and diagnose" data-action="probe" data-id="${esc(d.id)}">${icon('activity')}</button><button class="icon-button" aria-label="Readiness report" title="Run readiness assessment" data-action="readiness" data-id="${esc(d.id)}">${icon('shield')}</button><button class="icon-button" aria-label="Delete profile" title="Remove saved profile" data-action="delete-device" data-id="${esc(d.id)}">${icon('trash')}</button></div></div>`).join('')}</div>`:empty('server','No saved devices','Add your first Spark on the left. Device profiles never store SSH passwords or private key contents.')}
      <div class="hr"></div><div class="section-top"><h2 class="section-title">Connection inspection</h2>${selected?`<span class="tag tag-good">${esc(selected.name)}</span>`:''}</div>
      ${state.fileView ? fileBrowser(state.fileView) : state.lastProbe ? diagnostics(state.lastProbe) : selected?`<p class="help">Select the diagnostics button beside a device to run read-only health queries over SSH.</p>`: `<div class="info-ribbon">${icon('info')}<div><strong>First connection checklist</strong><p>Make sure SSH works in a terminal, trust the verified host fingerprint, and add your key to the SSH agent. This also works over a direct Ethernet cable when IP routing is configured.</p></div></div>`}
      </section></div>`;
}
function fileBrowser(info) {
 const path=info.path||'.';const files=info.files||[];
 return `<div class="section-top"><h2 class="section-title">${icon('file')} Files in ~/${esc(path==='.'?'':path)}</h2><button class="btn btn-small" data-action="folder-up">Up folder</button></div>
 <p class="note">Read-only browsing of the connected account’s home directory. Maximum 300 entries per folder. File transfers are not included in this release.</p>
 <div class="connection-list" style="margin-top:12px">${files.length?files.map(f=>`<div class="device-row"><div class="device-leading"><div class="device-icon">${icon(f.type==='directory'?'server':'file')}</div><div><strong>${esc(f.name)}</strong><small>${esc(f.type)} · ${f.size==null?'Unknown size':esc(f.size)+' bytes'}</small></div></div>${f.type==='directory'?`<button class="btn btn-small" data-action="folder-enter" data-folder="${esc(f.name)}">Open ${icon('chevron')}</button>`:''}</div>`).join(''):empty('file','Empty folder','No accessible items in this folder.')}</div>`;
}
function diagnostics(probe) {
  const x=probe.health;return `<div class="data-grid"><div class="data-tile"><label>HOSTNAME</label><strong style="font-size:14px;overflow-wrap:anywhere">${esc(x.hostname)}</strong></div><div class="data-tile"><label>GPU UTILIZATION</label><strong>${x.gpu_util_pct==null?'—':esc(x.gpu_util_pct)+'%'}</strong></div><div class="data-tile"><label>GPU TEMP.</label><strong>${x.gpu_temp_c==null?'—':esc(x.gpu_temp_c)+'°C'}</strong></div><div class="data-tile"><label>RAM IN USE</label><strong>${x.memory_used_pct==null?'—':esc(x.memory_used_pct)+'%'}</strong></div><div class="data-tile"><label>DISK IN USE</label><strong>${x.disk_used_pct==null?'—':esc(x.disk_used_pct)+'%'}</strong></div><div class="data-tile"><label>MEMORY</label><strong>${esc(fmt(x.memory_gb))} <span>GiB</span></strong></div></div>
  <div class="divider-label">REMOTE SYSTEM</div><div class="check-row"><div class="check-icon pass">${icon('check')}</div><div><strong>${esc(x.gpu_name||'No NVIDIA GPU detected')}</strong><p>${esc(x.os)} · ${esc(x.architecture)} · ${esc(x.uptime)}<br>Driver: ${esc(x.nvidia_driver||'Unavailable')} · Docker: ${esc(x.docker_version||'Unavailable')}</p></div></div>
  <p class="note">DGX Spark uses unified memory; dedicated framebuffer reporting in nvidia-smi may be unavailable. Memory values are sourced from the Linux host.</p>`;
}
function evaluationsPage() {
  return `${head('Validation workspace','AI model evaluations','Measure live model behavior through an OpenAI-compatible endpoint. Test cases remain transparent.',button(`${icon('file')} View reports`,'to-reports'))}
    <div class="info-ribbon">${icon('info')}<div><strong>Actual inference results — no synthetic grades</strong><p>Connect an endpoint that is reachable from this computer. For private DGX Spark services, use a VPN or an SSH port-forward. Evaluation prompts and responses stay in your local SparkCert database; do not use sensitive prompts unless you trust the model endpoint.</p></div></div>
    <div class="grid-2"><section class="card"><div class="section-top"><h2 class="section-title">Evaluation target</h2><span class="tag">LIVE API</span></div>
    <form id="eval-form"><div class="field"><label for="eval-endpoint">API base URL</label><input id="eval-endpoint" name="endpoint" value="http://127.0.0.1:8000/v1" placeholder="http://127.0.0.1:8000/v1" required /><span class="hint">Example: SSH forward port 8000, then point SparkCert at localhost:8000/v1</span></div>
    <div class="field top-space"><label for="eval-model">Model identifier</label><input id="eval-model" name="model" placeholder="e.g. my-local-model" required /></div>
    <div class="field top-space"><label for="eval-key">API key (optional, never saved)</label><input id="eval-key" name="api_key" type="password" placeholder="Leave blank if endpoint has no key" autocomplete="off" /></div>
    <div class="hr"></div><div class="section-top"><h2 class="section-title">Evaluation configuration</h2><span class="tag tag-good">${state.cases.length} CHECKS</span></div><div class="case-list">${state.cases.map((c,i)=>`<div class="case-card"><span class="case-index">${String(i+1).padStart(2,'0')}</span><div><strong>${esc(c.name)}</strong><small>${esc(c.category)} · ${esc(c.rule.replaceAll('_',' '))}</small></div><button class="icon-button" type="button" title="Remove check" data-action="remove-case" data-index="${i}">${icon('close')}</button></div>`).join('')}</div>
    <div class="top-space"><button type="button" class="btn" data-action="toggle-case">${icon('plus')} Add custom test case</button> <button type="button" class="btn btn-subtle" data-action="reset-cases">Reset checks</button></div>
    <div class="case-form top-space" id="case-form"><div class="form-grid"><div class="field"><label>Case name</label><input id="case-name" placeholder="Privacy constraint"/></div><div class="field"><label>Evaluation rule</label><select id="case-rule"><option value="exact">Exact match</option><option value="contains">Must contain</option><option value="not_contains">Must NOT contain</option><option value="json_key_value">JSON key=value</option></select></div></div><div class="field top-space"><label>System instruction</label><textarea id="case-system" placeholder="How should the model behave?"></textarea></div><div class="field top-space"><label>User prompt</label><textarea id="case-prompt" placeholder="What will you ask the model?"></textarea></div><div class="field top-space"><label>Expected text / JSON key=value</label><input id="case-expected" placeholder="SPARKCERT_READY" /></div><button type="button" class="btn btn-primary top-space" data-action="add-case">Save test case</button></div>
    <div class="hr"></div><button class="btn btn-primary btn-wide" type="submit" id="run-evaluation">${icon('activity')} Run live evaluation</button><p class="note">Tests use temperature 0 (if supported). A low score means test failure, not comprehensive model unsafety. No official certification is issued.</p></form>
    </section><section class="card"><div class="section-top"><h2 class="section-title">Evaluation outcome</h2><span class="tag">EVIDENCE FIRST</span></div>
    ${state.lastRun && state.lastRun.kind==='model_behavior'?resultBlock(state.lastRun):empty('activity','Ready for your first model run','Configure an API endpoint and execute the evaluation suite. Actual responses, latencies, and pass criteria will appear here.')}
    <div class="hr"></div><div class="section-top"><h2 class="section-title">What gets measured</h2></div><div class="feature-grid"><div class="feature">${icon('check')}<h3>Instruction adherence</h3><p>Whether observed output matches the requested formatting and constraints.</p></div><div class="feature">${icon('file')}<h3>JSON structure</h3><p>Parseable output and a required key-value comparison.</p></div><div class="feature">${icon('shield')}<h3>Limited canary check</h3><p>Whether a hidden test canary appears in the model output.</p></div><div class="feature">${icon('activity')}<h3>Observed latency</h3><p>Wall-clock response time recorded for each request.</p></div></div>
    </section></div>`;
}
function resultBlock(run) {
  const r=run.result;const checks=r.checks||r.cases||[];
  return `<div class="result-hero">${ring(r.score)}<div><h3>${esc(r.summary)}</h3><p>${esc(r.scope)}</p><p>${esc(when(run.created_at))}</p></div></div><div class="checks">${checks.map(c=>`<div class="check-row"><div class="check-icon ${c.passed?'pass':'fail'}">${icon(c.passed?'check':'close')}</div><div style="min-width:0"><strong>${esc(c.name)}</strong><p>${esc(c.detail)}${c.latency_ms!=null?' · '+esc(c.latency_ms)+' ms':''}${c.error?' · '+esc(c.error):''}</p>${c.output?`<details style="margin-top:10px"><summary class="muted-sm" style="cursor:pointer">Inspect model response</summary><pre class="scroll-pre">${esc(c.output)}</pre></details>`:''}</div></div>`).join('')}</div><div class="top-space"><button class="btn" data-action="pdf-report" data-id="${esc(run.id)}">${icon('download')} Export PDF evidence</button></div>`;
}
function reportsPage(){let runs=state.reports.filter(r=>state.filter==='all'||r.kind===state.filter);
  return `${head('Evidence library','Assessment reports','Locally stored test results and evidence-backed PDF exports.',button(`${icon('refresh')} Refresh`,'reload-reports'))}
  <div class="toolbar"><div class="segmented"><button class="${state.filter==='all'?'selected':''}" data-action="report-filter" data-filter="all">All</button><button class="${state.filter==='infrastructure'?'selected':''}" data-action="report-filter" data-filter="infrastructure">Infrastructure</button><button class="${state.filter==='model_behavior'?'selected':''}" data-action="report-filter" data-filter="model_behavior">Model evaluations</button></div><span class="muted-sm">${runs.length} assessments</span></div>
  ${runs.length?runs.map(r=>`<div class="report-card"><div class="device-leading"><div class="report-icon">${icon('file')}</div><div><strong>${esc(r.kind==='infrastructure'?'Infrastructure readiness':'AI model behavior')} <span class="muted2"> / ${esc(r.device_name)}</span></strong><p>${esc(when(r.created_at))} · ${esc(r.id.slice(0,8))} · ${esc(r.result.summary||'Completed')}</p></div></div><div class="report-actions"><span class="scores">${esc(r.score)}%</span><button class="btn btn-small" data-action="show-report" data-id="${esc(r.id)}">Details</button><button class="icon-button" data-action="pdf-report" aria-label="Export PDF" title="Export PDF" data-id="${esc(r.id)}">${icon('download')}</button></div></div>`).join(''):empty('file','No matching assessments','Completed tests will be saved here. Run your first infrastructure or model evaluation.',button('New evaluation','to-evaluations','btn-primary'))}`;
}
function aboutPage(){return `${head('Workspace preferences','Settings & security','Local control, reproducible evidence, clear security boundaries.')}
<div class="grid-2"><section class="card"><div class="section-top"><h2 class="section-title">Local runtime</h2><span class="tag tag-good">ACTIVE</span></div><div class="check-row"><div class="check-icon pass">${icon('check')}</div><div><strong>Localhost-only application</strong><p>Backend binds 127.0.0.1. Requests require an ephemeral per-launch session token; no remote accounts or tracking.</p></div></div><div class="check-row top-space"><div class="check-icon pass">${icon('check')}</div><div><strong>SSH host identity verification</strong><p>Existing OpenSSH known_hosts, ssh-agent, Host alias, Include and ProxyJump configuration supported.</p></div></div><div class="check-row top-space"><div class="check-icon pass">${icon('check')}</div><div><strong>No credentials persisted</strong><p>SparkCert stores SSH profiles and results, not SSH passwords, private keys, or API keys.</p></div></div><div class="hr"></div><p class="help">Local history is stored in your user profile directory under <code>~/.sparkcert/sparkcert.db</code>. Model test responses may contain sensitive data: treat your local workspace and PDF exports accordingly.</p></section>
<section class="card"><div class="section-top"><h2 class="section-title">Connection checklist</h2></div><div class="workflow"><div class="work-step"><span class="step-no">01</span><div><strong>Connect securely</strong><p>Set up Ethernet/LAN/VPN routing and confirm SSH access in a trusted terminal.</p></div></div><div class="work-step"><span class="step-no">02</span><div><strong>Verify SSH fingerprint</strong><p>Compare the first-connection host key fingerprint with the target device before accepting it.</p></div></div><div class="work-step"><span class="step-no">03</span><div><strong>Use an SSH agent</strong><p>Load your encrypted key so SparkCert can run non-interactive read-only diagnostics.</p></div></div><div class="work-step"><span class="step-no">04</span><div><strong>Expose model APIs privately</strong><p>Use SSH tunneling rather than making private evaluation services publicly reachable.</p></div></div></div>
<div class="divider-label">EXAMPLE PORT FORWARD</div><div class="code" id="tunnel-command">ssh -L 8000:127.0.0.1:8000 my-dgx-spark</div><div class="top-space"><button class="btn" data-action="copy-tunnel">Copy SSH tunnel command</button></div></section></div>
<div class="card top-space"><h2 class="section-title">Scope & responsible use</h2><p class="help">SparkCert is independent software, not an NVIDIA product and not an accredited certification body. Pass rates reflect only the checks executed. They do not establish cybersecurity compliance, model fairness, clinical safety, regulatory suitability, or absence of hallucinations. This initial release intentionally uses read-only SSH diagnostics; remote factory reset and destructive operations are not included.</p></div>`;}
async function getAliases(){try{const result=await api('/ssh/aliases');state.aliases=result.aliases;}catch(error){state.aliases=[];handleError(error);}}
async function reload(){await loadBase();render();}
async function pdf(id){const response=await api(`/reports/${id}/pdf`,{raw:true});const blob=await response.blob();const url=URL.createObjectURL(blob);const anchor=document.createElement('a');anchor.href=url;anchor.download=`sparkcert-${id.slice(0,8)}.pdf`;document.body.append(anchor);anchor.click();anchor.remove();setTimeout(()=>URL.revokeObjectURL(url),60000);toast('Evidence report downloaded');}
function openModal(title,body){const modal=$('#modal');$('#modal-inner').innerHTML=`<div class="dialog-inner"><div class="dialog-title"><h2>${esc(title)}</h2><button class="icon-button" data-action="close-modal" aria-label="Close">${icon('close')}</button></div>${body}</div>`;modal.showModal();}
async function action(event) {
  const el=event.target.closest('[data-action]');if(!el||state.working)return;
  const kind=el.dataset.action,id=el.dataset.id;
  try {
    if(kind==='to-connections')return navigate('connections');
    if(kind==='to-evaluations')return navigate('evaluations');
    if(kind==='to-reports')return navigate('reports');
    if(kind==='mode-alias'||kind==='mode-manual'){state.mode=kind==='mode-alias'?'alias':'manual';render();return;}
    if(kind==='reload-aliases'){await getAliases();render();return toast('SSH profiles refreshed');}
    if(kind==='reload-reports'){await reload();return toast('Reports updated');}
    if(kind==='select-device'){state.selectedId=id;state.lastProbe=null;state.fileView=null;return navigate('connections');}
    if(kind==='close-modal')return $('#modal').close();
    if(kind==='copy-tunnel'){await navigator.clipboard.writeText('ssh -L 8000:127.0.0.1:8000 my-dgx-spark');return toast('SSH tunnel command copied');}
    if(kind==='toggle-case'){return $('#case-form').classList.toggle('open');}
    if(kind==='reset-cases'){state.cases=await api('/evaluation/cases');return render();}
    if(kind==='remove-case'){state.cases.splice(Number(el.dataset.index),1);return render();}
    if(kind==='add-case'){const c={name:$('#case-name').value.trim(),category:'Custom',system:$('#case-system').value,prompt:$('#case-prompt').value.trim(),expected:$('#case-expected').value,rule:$('#case-rule').value};if(!c.name||!c.prompt)return toast('Case name and prompt are required',true);if(state.cases.length>=25)return toast('Maximum 25 test cases',true);state.cases.push(c);render();return toast('Custom test case added');}
    if(kind==='report-filter'){state.filter=el.dataset.filter;return render();}
    if(kind==='show-report'){const report=state.reports.find(r=>r.id===id)||await api(`/reports/${id}`);return openModal('Assessment evidence',`<p class="muted-sm">${esc(report.device_name)} · ${esc(when(report.created_at))}</p>${resultBlock(report)}`);}
    if(kind==='pdf-report'){await pdf(id);return;}
    if(kind==='terminal'){
      const response=await api(`/devices/${id}/terminal`,{method:'POST'});
      return toast(response.message);
    }
    if(kind==='browse'){
      state.selectedId=id;state.lastProbe=null;
      state.fileView=await api(`/devices/${id}/files?path=.`);
      render();return;
    }
    if(kind==='folder-enter'||kind==='folder-up'){
      if(!state.fileView||!state.selectedId)return;
      let path=state.fileView.path;
      if(kind==='folder-enter')path=(path==='.'?'':path+'/')+el.dataset.folder;
      else path=path==='.'?'.':path.includes('/')?path.slice(0,path.lastIndexOf('/')):'.';
      state.fileView=await api(`/devices/${state.selectedId}/files?path=${encodeURIComponent(path)}`);
      render();return;
    }
    if(kind==='delete-device'){
      const d=state.devices.find(x=>x.id===id);if(!confirm(`Remove saved SSH profile "${d?.name||'device'}"? Existing assessment reports will remain.`))return;
      await api(`/devices/${id}`,{method:'DELETE'});state.lastProbe=null;if(state.selectedId===id)state.selectedId='';await reload();return toast('Connection profile removed');
    }
    if(kind==='probe'||kind==='readiness'){
      state.selectedId=id;state.fileView=null;const d=state.devices.find(x=>x.id===id);
      state.working=true;const original=el.innerHTML;el.innerHTML='<span class="spinner"></span>';
      try {
        if(kind==='probe'){const data=await api(`/devices/${id}/probe`,{method:'POST'});state.lastProbe=data;render();toast(`${d?.name||'Device'} connected; diagnostics collected`);}
        else {const report=await api(`/devices/${id}/readiness`,{method:'POST'});state.lastRun=report;await reload();openModal('Infrastructure readiness result',resultBlock(report));toast('Infrastructure assessment completed');}
      } finally {state.working=false;if(el.isConnected)el.innerHTML=original;}
      return;
    }
  } catch(error){state.working=false;handleError(error);}
}
async function submit(event){
  if(!['device-form','eval-form'].includes(event.target.id))return;
  event.preventDefault();if(state.working)return;
  const form=event.target;const submitBtn=form.querySelector('button[type="submit"]');const original=submitBtn.innerHTML;submitBtn.disabled=true;submitBtn.innerHTML=`<span class="spinner"></span> ${form.id==='eval-form'?'Running real evaluations…':'Saving profile…'}`;state.working=true;
  try{
    if(form.id==='device-form'){
      const data=Object.fromEntries(new FormData(form).entries());data.port=Number(data.port||22);
      const created=await api('/devices',{method:'POST',body:JSON.stringify(data)});
      state.selectedId=created.id;state.lastProbe=null;await reload();toast('Device profile added; select diagnostics to test connectivity');
    } else {
      if(!state.cases.length)throw new Error('Add at least one evaluation case');
      const data=Object.fromEntries(new FormData(form).entries());data.cases=state.cases;
      const report=await api('/evaluation/run',{method:'POST',body:JSON.stringify(data)});
      state.lastRun=report;await reload();toast('Model evaluation completed and evidence saved');
    }
  }catch(err){handleError(err);}finally{state.working=false;submitBtn.disabled=false;submitBtn.innerHTML=original;}
}
document.addEventListener('click',event=>{
  const pageBtn=event.target.closest('[data-page]');if(pageBtn){navigate(pageBtn.dataset.page).catch(handleError);return;}
  action(event);
});
document.addEventListener('submit',submit);
$('#menu-button').addEventListener('click',()=>$('#sidebar').classList.toggle('open'));
$('#modal').addEventListener('click',event=>{if(event.target===$('#modal'))$('#modal').close();});
(async()=>{try{await loadBase();render();}catch(error){handleError(error);$('#content').innerHTML=head('Connection error','Unable to start SparkCert',error.message,button('Retry','reload-reports'));}})();
