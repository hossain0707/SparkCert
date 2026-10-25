"""Offline, mock-data browser smoke test; not a live DGX Spark validation."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
html=(ROOT/'web/index.html').read_text().replace('__SPARKCERT_TOKEN__','ui-smoke-token')
css=(ROOT/'web/styles.css').read_text()
js=(ROOT/'web/app.js').read_text()
html=html.replace('<link rel="stylesheet" href="/assets/styles.css" />', f'<style>{css}</style>')
html=html.replace('<script src="/assets/app.js" defer></script>','')
mock=r'''
const previewDevice={id:'demo-dgx-1', name:'DGX Spark (demo data)', host:'192.0.2.10',username:'operator',port:22,ssh_alias:'', identity_file:''};
const previewRun={id:'demo-evidence-1',kind:'infrastructure',device_name:'DGX Spark (demo data)',created_at:'2026-10-25T04:00:00Z',score:85,status:'completed',integrity:'verified', result_sha256:'demo-only',result:{score:85,summary:'6/7 demo checks passed',scope:'Illustrative preview only; no real device connected.',checks:[{name:'SSH',passed:true,detail:'Demonstration data'}]}};
const responseMap={
'/api/overview':{version:'0.2.0',platform:'posix',ssh_available:true,device_count:1,run_count:1,devices:[previewDevice],recent_runs:[previewRun]},
'/api/reports':[previewRun],'/api/tunnels':[ {id:'demo-tunnel-1',device_id:'demo-dgx-1',device_name:'DGX Spark (demo data)',local_port:8176,remote_port:8000,endpoint:'http://127.0.0.1:8176/v1'} ],
'/api/audit':[{id:1,event:'assessment_saved',created_at:'2026-10-25T04:00:00Z'}],
'/api/ssh/aliases':{aliases:[{alias:'dgx-spark'}]},
'/api/evaluation/cases':[{name:'Instruction following',category:'Demo',system:'',prompt:'Say ready',expected:'ready',rule:'exact'}]
};
window.fetch=async (url, options={})=>{
 const clean=String(url).split('?')[0];
 if(clean in responseMap)return new Response(JSON.stringify(responseMap[clean]),{status:200,headers:{'Content-Type':'application/json'}});
 return new Response(JSON.stringify({detail:'Preview-only stub'}),{status:404,headers:{'Content-Type':'application/json'}});
};
window.confirm=()=>false;
'''

with sync_playwright() as playwright:
    browser=playwright.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
    for width,height,label in [(1440,900,'desktop'),(390,844,'mobile')]:
        page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
        errors=[]
        page.on('pageerror',lambda e: errors.append(str(e)))
        page.set_content(html,wait_until='domcontentloaded')
        page.evaluate(mock)
        page.add_script_tag(content=js)
        page.get_by_text('Your AI infrastructure, under control.').wait_for(timeout=10000)
        if width<500:page.locator('#menu-button').click()
        page.locator('[data-page="connections"]').click()
        page.get_by_text('Private model API tunnels').wait_for(timeout=10000)
        assert page.locator('#tunnel-form').is_visible()
        if width<500:page.locator('#menu-button').click()
        page.locator('[data-page="evaluations"]').click()
        page.locator('#eval-concurrency').wait_for(timeout=10000)
        assert page.locator('#eval-repetitions').is_visible()
        if width<500:page.locator('#menu-button').click()
        page.locator('[data-page="about"]').click()
        page.get_by_text('Evidence retention').wait_for(timeout=10000)
        assert page.locator('#retention-form').is_visible()
        assert not errors, errors
        page.wait_for_timeout(400) # allow sidebar closing transition to finish
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth+1'), 'Unexpected horizontal page overflow'
        page.screenshot(path=str(ROOT/'docs/assets'/f'v02-{label}-settings-preview.png'),full_page=True)
        print(f'{label}: connections, tunnel UI, evaluation controls, retention and audit panel passed (mock-only)')
        page.close()
    browser.close()
