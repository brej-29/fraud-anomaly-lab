import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('real benchmark budget, evidence, sample import, queue and export work',async({page},testInfo)=>{
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto('./');
  await expect(page.getByRole('heading',{name:'Make every review count.'})).toBeVisible();
  await expect(page.getByText(/Real historical holdout.*aggregate results only/)).toBeVisible();
  const initial=await page.locator('#metric-k').textContent();
  await page.getByRole('button',{name:'2%',exact:true}).click();
  expect(await page.locator('#metric-k').textContent()).not.toBe(initial);
  await page.screenshot({path:`.local/test-screenshots/${testInfo.project.name}-benchmark.png`,fullPage:true});
  await page.getByRole('link',{name:'The evidence',exact:true}).click();
  await expect(page.getByRole('heading',{name:'Evidence, with the edges left in.'})).toBeVisible();
  await page.getByRole('button',{name:'Import scored CSV'}).click();
  await page.getByRole('button',{name:'Use synthetic sample'}).click();
  await expect(page.getByText('SYNTHETIC',{exact:true})).toBeVisible();
  await expect(page.getByRole('heading',{name:'Your review queue',exact:true})).toBeVisible();
  await page.getByRole('button',{name:'Next',exact:true}).focus();
  await page.keyboard.press('Enter');
  await expect(page.locator('#next-page')).toBeFocused();
  await page.locator('#strategy').selectOption('amount');
  await expect(page.locator('.queue .section-top')).toContainText('larger amounts rank first');
  await expect(page.locator('.chart-legend')).toContainText('Your risk scores');
  const download=page.waitForEvent('download');
  await page.getByRole('button',{name:'Export review queue',exact:true}).click();
  expect((await download).suggestedFilename()).toBe('clearcut-review-queue.csv');
  await page.screenshot({path:`.local/test-screenshots/${testInfo.project.name}-queue.png`,fullPage:true});
  expect(errors).toEqual([]);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
});

test('private CSV import rejects errors; unknown labels stay unknown; HTML identifiers stay inert',async({page})=>{
  await page.goto('./#import');
  await page.locator('#file-input').setInputFiles({name:'invalid.csv',mimeType:'text/csv',buffer:Buffer.from('score,amount\nNaN,3')});
  await expect(page.locator('#import-status')).toContainText('score must be finite');
  const requests=[];page.on('request',r=>{if(r.method()!=='GET')requests.push(r.url());});
  const csv='id,score,amount\n<img src=x onerror=alert(1)>,9,5\n'+Array.from({length:39},(_,i)=>`safe-${i},${8-i},2`).join('\n');
  await page.locator('#file-input').setInputFiles({name:'private.csv',mimeType:'text/csv',buffer:Buffer.from(csv)});
  await expect(page.getByText('YOUR DATA',{exact:true})).toBeVisible();
  await expect(page.locator('#metric-recall')).toHaveText('Not available');
  await expect(page.getByRole('heading',{name:'Scores can rank. Labels measure.'})).toBeVisible();
  await page.getByRole('button',{name:'5%',exact:true}).click();
  await expect(page.locator('.queue')).toContainText('<img src=x onerror=alert(1)>');
  expect(await page.locator('.queue img').count()).toBe(0);
  await page.locator('#capacity').fill('0');
  await expect(page.getByRole('heading',{name:'No reviews at this budget'})).toBeVisible();
  expect(requests).toEqual([]);
});

test('all main surfaces pass automated accessibility checks and reduced motion',async({page})=>{
  await page.emulateMedia({reducedMotion:'reduce'});
  for(const route of ['workbench','evidence','guide','import']){
    await page.goto(`./#${route}`);
    await expect(page.locator('.page-heading h1')).toBeVisible();
    const scan=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();
    expect(scan.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)}))).toEqual([]);
  }
});

test('loaded workspace calculates offline, and missing benchmark has recovery',async({page,context})=>{
  await page.goto('./');await expect(page.locator('#capacity')).toBeVisible();
  await context.setOffline(true);
  await page.getByRole('button',{name:'1%',exact:true}).click();
  await expect(page.locator('#capacity-value')).toContainText('1.0');
  await context.setOffline(false);
  await page.route('**/benchmark.json',route=>route.fulfill({status:503,body:'unavailable'}));
  await page.reload();
  await expect(page.getByRole('button',{name:'Reload workbench'})).toBeVisible();
});
