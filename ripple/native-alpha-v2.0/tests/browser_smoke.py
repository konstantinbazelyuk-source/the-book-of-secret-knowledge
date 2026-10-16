"""Optional dashboard UI test: Chromium inlined HTML, mocked HTTP only. Not a Windows verification."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent.parent
html=(ROOT/'bin/dashboard.html').read_text()
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':420,'height':830},device_scale_factor=1)
 page.set_content(html,wait_until='load')
 page.evaluate("""() => {window.fetch=async (path,opts)=>({ok:true,json:async()=>path==='/v1/status'?{running:2,budget:{maximum_workers:4},network:'localhost API only'}:path==='/v1/jobs'&&opts?.method!=='POST'?{jobs:[]}:{id:'test-job-id',status:'queued'}})}""")
 page.locator('#token').fill('only-a-smoke-test-token')
 page.locator('#refresh').click()
 page.wait_for_function("document.querySelector('#notice').textContent.includes('Connected')")
 page.locator('#kind').select_option('prime_count')
 if '100000' not in page.locator('#params').input_value():raise AssertionError('task default missing')
 page.locator('#submit').click()
 page.wait_for_function("document.querySelector('#submit_result').textContent.includes('test-job-id')")
 assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth+2')
 out=ROOT/'benchmarks'/'dashboard_mobile_smoke.png';page.screenshot(path=str(out),full_page=True)
 print(json.dumps({'browser':'Chromium headless','viewport':'420x830','ui_logic':'PASSED','backend':'MOCKED; real localhost backend separately tested','screenshot':out.name}))
 browser.close()
