import {execFileSync} from 'node:child_process';
import {readFileSync} from 'node:fs';
const phrases=['Clau'+'de','Anth'+'ropic','Co'+'dex','Open'+'AI','Generated'+' with','Co-'+'Authored-By','Ses'+'sion'];
const pattern=new RegExp(phrases.join('|'),'i');
const git=(...args)=>execFileSync('git',args,{encoding:'utf8',maxBuffer:20*1024*1024});
let failures=[];
function inspect(label,text){if(pattern.test(text))failures.push(label);}
if(process.argv[2]==='--commit')inspect('Commit message',readFileSync(process.argv[3],'utf8'));
else{
  const base=process.env.SCAN_BASE||'origin/main';
  inspect('New commit messages',git('log',`${base}..HEAD`,'--format=%B'));
  const paths=git('diff','--name-only','--diff-filter=ACMRT',base,'--').trim().split('\n').filter(Boolean);
  const untracked=git('ls-files','--others','--exclude-standard').trim().split('\n').filter(Boolean);
  for(const path of new Set([...paths,...untracked])){
    if(/\.(png|jpg|webp|woff2|ico|zip)$/.test(path))continue;
    try{inspect(path,readFileSync(path,'utf8'));}catch{}
  }
  if(process.argv[2]==='--body')inspect('Pull request body',readFileSync(process.argv[3],'utf8'));
}
if(failures.length){console.error('Disallowed attribution text found in: '+failures.join(', '));process.exit(1);}
console.log('Attribution scan clean.');
