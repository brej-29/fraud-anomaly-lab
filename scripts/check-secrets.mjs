import {execFileSync} from 'node:child_process';
import {readFileSync} from 'node:fs';
const paths=new Set([...execFileSync('git',['ls-files'],{encoding:'utf8'}).trim().split('\n'),...execFileSync('git',['ls-files','--others','--exclude-standard'],{encoding:'utf8'}).trim().split('\n')]);
const rules=[['private key',/-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----/],['cloud access id',/\bAKIA[0-9A-Z]{16}\b/],['repository token',/\bgh[pousr]_[A-Za-z0-9]{30,}\b/],['provider key',/\bsk-[A-Za-z0-9_-]{32,}\b/]];
const matches=[];
for(const p of paths){try{const text=readFileSync(p,'utf8');for(const [name,re] of rules)if(re.test(text))matches.push({file:p,name});}catch{}}
if(matches.length){console.error(JSON.stringify(matches));process.exit(1);}console.log('No matching secret signatures in tracked or publishable files.');
