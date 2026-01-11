import { defineConfig } from '@playwright/test';
export default defineConfig({
  testDir:'./tests/e2e',fullyParallel:true,retries:process.env.CI?1:0,
  reporter: [['list'],['html',{open:'never'}]],
  use:{baseURL:process.env.LIVE_URL||'http://127.0.0.1:4173',trace:'retain-on-failure'},
  webServer:process.env.LIVE_URL?undefined:{command:'npm run preview -- --port 4173',port:4173,reuseExistingServer:!process.env.CI},
  projects:[{name:'desktop',use:{viewport:{width:1440,height:1000}}},{name:'tablet',use:{viewport:{width:834,height:1112}}},{name:'phone',use:{viewport:{width:390,height:844},isMobile:true,hasTouch:true}}]
});
