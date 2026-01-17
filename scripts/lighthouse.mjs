import lighthouse from 'lighthouse';
import {launch} from 'chrome-launcher';
import {chromium} from '@playwright/test';
import {writeFileSync,mkdirSync} from 'node:fs';
mkdirSync('.local',{recursive:true});
const url=process.env.LIVE_URL||'http://127.0.0.1:4173/';
const chrome=await launch({chromePath:chromium.executablePath(),chromeFlags:['--headless','--no-sandbox']});
try{
  const result=await lighthouse(url,{port:chrome.port,output:'json',onlyCategories:['performance','accessibility','best-practices','seo'],logLevel:'error'});
  writeFileSync('.local/lighthouse-full.json',JSON.stringify(result.lhr,null,2));
  const report={url,tool:'Lighthouse',version:result.lhr.lighthouseVersion,formFactor:result.lhr.configSettings.formFactor,scores:Object.fromEntries(Object.entries(result.lhr.categories).map(([k,v])=>[k,Math.round(v.score*100)])),metrics:{fcp:result.lhr.audits['first-contentful-paint'].numericValue,lcp:result.lhr.audits['largest-contentful-paint'].numericValue,cls:result.lhr.audits['cumulative-layout-shift'].numericValue,tbt:result.lhr.audits['total-blocking-time'].numericValue}};
  writeFileSync(process.env.LIGHTHOUSE_REPORT_PATH || (process.env.LIVE_URL?'reports/lighthouse-live.json':'reports/lighthouse-local.json'),JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify(report,null,2));
  console.log(JSON.stringify({failed:Object.entries(result.lhr.audits).filter(([,a])=>a.score!==null&&a.score<1&&a.scoreDisplayMode==='binary').map(([k,a])=>({id:k,title:a.title}))}));
  if(Object.values(report.scores).some(s=>s<90))process.exitCode=1;
}finally{await chrome.kill();}
