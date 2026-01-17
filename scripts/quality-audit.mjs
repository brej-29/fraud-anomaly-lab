import { spawnSync } from 'node:child_process';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
mkdirSync('.local', { recursive: true });
const runs = [];
for (let run = 1; run <= 3; run++) {
  const path = `.local/quality-audit-${run}.json`;
  const result = spawnSync(process.execPath, ['scripts/lighthouse.mjs'], {
    env: { ...process.env, LIGHTHOUSE_REPORT_PATH: path },
    stdio: 'inherit',
  });
  if (result.error) throw result.error;
  runs.push({ run, exit: result.status, ...JSON.parse(readFileSync(path, 'utf8')) });
}
const minimum = Object.fromEntries(Object.keys(runs[0].scores).map(key => [key, Math.min(...runs.map(run => run.scores[key]))]));
const passed = runs.every(run => run.exit === 0) && Object.values(minimum).every(score => score >= 90);
const report = {
  url: runs[0].url,
  runner: { platform: process.platform, node: process.version, ci: Boolean(process.env.CI) },
  method: 'Three fresh Chrome profiles; mobile Lighthouse default simulated throttling. Every category in every run must reach 90.',
  audited_at: new Date().toISOString(),
  threshold: 90,
  minimum,
  passed,
  runs,
};
writeFileSync('reports/lighthouse-live-ci.json', JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({ minimum, passed }));
if (!passed) process.exitCode = 1;
