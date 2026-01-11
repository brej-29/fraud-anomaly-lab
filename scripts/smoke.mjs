import { chromium } from '@playwright/test';
const url=process.env.LIVE_URL||'http://127.0.0.1:4173/';
const browser=await chromium.launch({headless:true});
try{
  const page=await browser.newPage();
  const response=await page.goto(url);
  if(!response.ok())throw new Error(`HTTP ${response.status()}`);
  await page.getByRole('heading',{name:'Make every review count.'}).waitFor();
  await page.getByRole('button',{name:'Try a sample'}).click();
  await page.getByText('SYNTHETIC',{exact:true}).waitFor();
  const download=page.waitForEvent('download');
  await page.getByRole('button',{name:'Export review queue',exact:true}).click();
  const file=await download;
  if(file.suggestedFilename()!=='clearcut-review-queue.csv')throw new Error('Export did not complete');
  console.log(JSON.stringify({url,http:response.status(),benchmark:true,localSample:true,queueExport:true}));
}finally{await browser.close();}
