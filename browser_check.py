from playwright.sync_api import sync_playwright
from pathlib import Path
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':1440,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:8000');page.get_by_role('button',name='Wczytaj przykład').click();page.get_by_role('button',name='+ Zaplanuj').first.wait_for()
 page.get_by_role('button',name='+ Zaplanuj').first.click();page.locator('[name=qty]').fill('6');page.get_by_role('button',name='Zapisz',exact=True).click();page.locator('dialog').wait_for(state='hidden')
 page.get_by_role('button',name='Opublikuj plan').click();page.get_by_role('button',name='Zapisz',exact=True).click();page.locator('dialog').wait_for(state='hidden')
 page.get_by_role('button',name='Panel stanowiska').click();page.get_by_role('button',name='Rozpocznij').click();page.get_by_role('button',name='Zgłoś ilość').click();page.locator('[name=qty]').fill('2');page.get_by_role('button',name='Zapisz',exact=True).click();page.locator('dialog').wait_for(state='hidden');assert '4' in page.locator('.job-metrics').inner_text()
 page.get_by_role('button',name='Wstrzymaj').click();page.locator('[name=note]').fill('Test: sprawdzenie panelu');page.get_by_role('button',name='Zapisz',exact=True).click();page.locator('dialog').wait_for(state='hidden');page.get_by_role('button',name='Wznów pracę').wait_for()
 page.screenshot(path='/workspace/production-planner/panel-stanowiska.png',full_page=True)
 page.set_viewport_size({'width':390,'height':844});page.screenshot(path='/workspace/production-planner/panel-mobile.png',full_page=True)
 assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'Mobile horizontal overflow'
 page.set_viewport_size({'width':1440,'height':1000});page.get_by_role('button',name='Planowanie zamówień').click();page.screenshot(path='/workspace/production-planner/planowanie.png',full_page=False)
 assert not errors,errors
 print('Browser passed: demo, allocation, publication, start, partial quantity, pause, mobile layout; no JS errors.')
 browser.close()
