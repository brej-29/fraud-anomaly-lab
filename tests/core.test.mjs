import test from 'node:test';
import assert from 'node:assert/strict';
import {parseTransactions, rankTransactions, summarize, profileRows, exportQueue, wilson, sampleCSV} from '../src/core.js';

test('known confusion counts, tied scores preserve row order and labels never rank',()=>{
  const rows=parseTransactions('id,score,amount,label\na,5,10,0\nb,5,20,1\nc,2,30,1\nd,-3,2,0');
  assert.deepEqual(rankTransactions(rows).map(r=>r.id),['a','b','c','d']);
  const p=summarize(rankTransactions(rows),2);
  assert.equal(p.caught,1);assert.equal(p.legitimate,1);assert.equal(p.missed,1);assert.equal(p.precision,.5);assert.equal(p.recall,.5);
  assert.equal(summarize(rankTransactions(rows,'amount'),2).caught,2);
});
test('missing outcomes are unknown, not zero, and zero positives give undefined recall',()=>{
  const u=parseTransactions('score,amount\n.9,10\n.2,20');
  assert.equal(summarize(u,1).caught,null);assert.equal(profileRows(u).strategies[0].points[5].recall,null);
  const z=parseTransactions('score,amount,label\n.9,10,0');
  assert.equal(summarize(z,1).recall,null);assert.equal(summarize(z,0).precision,null);
  assert.equal(summarize(z,1).precision,0);
});
test('strict CSV validation rejects ambiguous or incomplete files atomically',()=>{
  for(const csv of ['score,amount\nNaN,2','score,amount\nInfinity,2','score,amount\n,2','score,amount\n1,-2','score,amount,label\n1,2,','score,amount,label\n1,2,2','score,amount\n','id,score,amount\na,1,2\na,2,4','score,score,amount\n1,2,3','amount\n2','score,amount\n1,2,3','score,amount\n"1,2'])assert.throws(()=>parseTransactions(csv),undefined,csv);
});
test('quoted fields, BOM, CRLF and trimmed headers are supported; HTML remains data',()=>{
  const rows=parseTransactions('\uFEFF id , score ,amount,label\r\n"<img src=x>,ref",0.4,2,1\r\n');
  assert.equal(rows[0].id,'<img src=x>,ref');assert.equal(rows[0].label,1);
});
test('queue export preserves ranking and neutralizes spreadsheet formula identifiers',()=>{
  const rows=parseTransactions('id,score,amount,label\n=2+2,9,10,1\nplain,2,12,0');
  const csv=exportQueue(rows,1,'score');
  assert.ok(csv.includes("'=2+2"));assert.ok(!csv.includes('plain'));assert.ok(csv.includes('rank,id,score,amount,label'));
});
test('profile curve matches direct confusion counts at every capacity including zero',()=>{
  const rows=parseTransactions(sampleCSV()),profile=profileRows(rows);
  for(const s of profile.strategies)for(const p of s.points){const direct=summarize(rankTransactions(rows,s.id),p.k);assert.equal(p.caught,direct.caught);assert.equal(p.recall,direct.recall);assert.equal(p.legitimate,direct.legitimate);}
});
test('Wilson uncertainty behaves at boundaries; review count is guarded',()=>{
  assert.equal(wilson(0,0),null);assert.ok(wilson(0,10)[1]>0);assert.ok(wilson(10,10)[0]<1);
  assert.throws(()=>summarize([],1));assert.throws(()=>summarize([],0.5));assert.throws(()=>rankTransactions([],'label'));
});
