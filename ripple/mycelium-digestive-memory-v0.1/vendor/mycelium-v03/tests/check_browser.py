from pathlib import Path
from playwright.sync_api import sync_playwright
D=Path(__file__).resolve().parents[1]
with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  for width,height,tag in [(1280,850,'desktop'),(390,844,'mobile')]:
    page=browser.new_page(viewport={'width':width,'height':height})
    errors=[]
    page.on('pageerror', lambda e:errors.append(str(e)))
    page.set_content((D/'Ripple-Mycelium-Mathematics-Lab-v0.3.html').read_text(),wait_until='load')
    print(tag,'title',page.title())
    print('initial',page.locator('#neuronMetrics').inner_text().replace('\n',' '),page.locator('#colonyMetrics').inner_text().replace('\n',' '))
    assert not errors,errors
    assert 'Original MAE' in page.locator('#neuronMetrics').inner_text()
    assert '111/111' in page.locator('#colonyMetrics').inner_text()
    page.select_option('#profile','dark-interrupt');page.select_option('#method','feedforward-fast');page.click('#simulate')
    assert 'Candidate MAE' in page.locator('#neuronMetrics').inner_text()
    page.select_option('#growth','fixed4')
    page.select_option('#routing','roundrobin')
    page.select_option('#workload','balanced')
    assert 'worker-seconds' in page.locator('#colonyMetrics').inner_text()
    page.locator('#economy').click()
    assert 'worker-seconds' in page.locator('#colonyMetrics').inner_text()
    overflow=page.evaluate('document.documentElement.scrollWidth > window.innerWidth + 1')
    print('overflow',overflow,'errors',errors)
    assert not errors,errors
    assert not overflow
    page.screenshot(path=str(D/'charts'/f'explorer_{tag}_verified.png'),full_page=True)
    page.close()
  browser.close()
print('browser checks passed')
