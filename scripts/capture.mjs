import {chromium} from '@playwright/test';
import {mkdirSync} from 'node:fs';
const browser=await chromium.launch({headless:true});
mkdirSync('.local/screenshots',{recursive:true});
try{
  for(const [name,width,height] of [['desktop',1440,1000],['tablet',834,1112],['phone',390,844]]){
    const page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1,reducedMotion:'reduce'});
    for(const route of ['workbench','evidence','guide','import']){
      await page.goto(`http://127.0.0.1:4173/#${route}`);
      await page.locator('.page-heading h1').waitFor();
      await page.evaluate(()=>document.fonts.ready);
      await page.screenshot({path:`.local/screenshots/${name}-${route}.png`,fullPage:true});
    }
    await page.getByRole('button',{name:'Use synthetic sample'}).click();
    await page.getByRole('heading',{name:'Your review queue',exact:true}).waitFor();
    await page.screenshot({path:`.local/screenshots/${name}-queue.png`,fullPage:true});
    await page.close();
  }
}finally{await browser.close();}
console.log('Captured all four routes and sample queue at three viewport widths.');
