(() => {
  'use strict';
  const en = document.documentElement.lang === 'en';
  const search = document.querySelector('#search');
  const status = document.querySelector('#search-status');
  const items = [...document.querySelectorAll('.searchable')];
  let timer;
  search?.addEventListener('input', () => {
    clearTimeout(timer);
    timer=setTimeout(() => {
      const q=search.value.trim().toLocaleLowerCase();
      let hits=0;
      items.forEach(el=>{const ok=!q||el.textContent.toLocaleLowerCase().includes(q);el.hidden=!ok;if(ok&&q)hits++;});
      document.querySelectorAll('.hit').forEach(x=>x.classList.remove('hit'));
      let prose=0;
      if(q) document.querySelectorAll('main > p, main > h2, main > h3').forEach(el=>{if(el.textContent.toLocaleLowerCase().includes(q)){el.classList.add('hit');prose++;}});
      status.textContent=q?(en?`Reference/examples: ${hits} / Text: ${prose}`:`辞典・教材 ${hits}件 / 本文 ${prose}件`):(en?'Filter by command or feature':'命令名・機能名で絞り込み');
    },100);
  });
  document.addEventListener('click',async e=>{
    if(!(e.target instanceof Element))return;
    const button=e.target.closest('.copy');
    if(button){
      const text=button.parentElement.querySelector('code').textContent;
      try { await navigator.clipboard.writeText(text); button.textContent=en?'Copied':'コピー済み'; }
      catch { const a=document.createElement('textarea');a.value=text;document.body.append(a);a.select();const ok=document.execCommand('copy');a.remove();button.textContent=ok?(en?'Copied':'コピー済み'):(en?'Select and copy':'選択してコピー'); }
      setTimeout(()=>button.textContent=en?'Copy':'コピー',1800);
    }
    if(e.target.closest('.print'))window.print();
  });
  function reveal(){
    if(!location.hash)return;
    const el=document.getElementById(decodeURIComponent(location.hash.slice(1)));
    if(el){let p=el;while(p){if(p.tagName==='DETAILS')p.open=true;p=p.parentElement;}el.scrollIntoView();}
  }
  addEventListener('hashchange',reveal);reveal();
  let prior=[];
  addEventListener('beforeprint',()=>{prior=[...document.querySelectorAll('details')].map(e=>[e,e.open]);prior.forEach(([e])=>e.open=true);});
  addEventListener('afterprint',()=>prior.forEach(([e,open])=>e.open=open));
})();
