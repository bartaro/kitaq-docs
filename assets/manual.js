(() => {
  'use strict';
  const lang = document.documentElement.lang;
  const labels = {
    en: ['Reference/examples: {hits} / Text: {prose}', 'Filter by command or feature', 'Copied', 'Select and copy', 'Copy'],
    ja: ['辞典・教材 {hits}件 / 本文 {prose}件', '命令名・機能名で絞り込み', 'コピー済み', '選択してコピー', 'コピー'],
    ko: ['참조·예제: {hits}건 / 본문: {prose}건', '명령이나 기능으로 검색', '복사됨', '선택하여 복사', '복사'],
    'zh-CN': ['参考与示例：{hits} 项 / 正文：{prose} 处', '按命令或功能筛选', '已复制', '请选择后复制', '复制'],
    'zh-TW': ['參考與範例：{hits} 項 / 本文：{prose} 處', '依命令或功能篩選', '已複製', '請選取後複製', '複製'],
    es: ['Referencias y ejemplos: {hits} / Texto: {prose}', 'Buscar por comando o función', 'Copiado', 'Seleccionar y copiar', 'Copiar'],
    'pt-BR': ['Referências e exemplos: {hits} / Texto: {prose}', 'Filtrar por comando ou recurso', 'Copiado', 'Selecione e copie', 'Copiar'],
    fr: ['Références et exemples : {hits} / Texte : {prose}', 'Rechercher une commande ou une fonction', 'Copié', 'Sélectionner et copier', 'Copier'],
    de: ['Referenzen und Beispiele: {hits} / Text: {prose}', 'Nach Befehl oder Funktion suchen', 'Kopiert', 'Auswählen und kopieren', 'Kopieren'],
  };
  const ui = labels[lang] || labels.en;
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
      if(q) document.querySelectorAll('main > p, main > h2, main > h3, .authored > p, .authored > h2, .authored > h3').forEach(el=>{if(el.textContent.toLocaleLowerCase().includes(q)){el.classList.add('hit');prose++;}});
      status.textContent=q?ui[0].replace('{hits}', hits).replace('{prose}', prose):ui[1];
    },100);
  });
  document.addEventListener('click',async e=>{
    if(!(e.target instanceof Element))return;
    const button=e.target.closest('.copy');
    if(button){
      const source=button.dataset.copySource
        ? document.getElementById(button.dataset.copySource)
        : button.parentElement.querySelector('code');
      if(!source)return;
      const text=source.textContent;
      const originalLabel=button.dataset.copyLabel || button.textContent;
      button.dataset.copyLabel=originalLabel;
      try { await navigator.clipboard.writeText(text); button.textContent=ui[2]; }
      catch { const a=document.createElement('textarea');a.value=text;document.body.append(a);a.select();const ok=document.execCommand('copy');a.remove();button.textContent=ok?ui[2]:ui[3]; }
      setTimeout(()=>button.textContent=originalLabel,1800);
    }
    if(e.target.closest('.print'))window.print();
  });
  function reveal(){
    if(!location.hash)return;
    if(document.querySelector('[data-copy-source]') && ['#gb','#fc'].includes(location.hash)){
      document.querySelectorAll('nav.languages a').forEach(a=>{
        a.href=a.href.split('#')[0]+location.hash;
      });
    }
    const el=document.getElementById(decodeURIComponent(location.hash.slice(1)));
    if(el){let p=el;while(p){if(p.tagName==='DETAILS')p.open=true;p=p.parentElement;}el.scrollIntoView();}
  }
  addEventListener('hashchange',reveal);reveal();
  let prior=[];
  addEventListener('beforeprint',()=>{prior=[...document.querySelectorAll('details')].map(e=>[e,e.open]);prior.forEach(([e])=>e.open=true);});
  addEventListener('afterprint',()=>prior.forEach(([e,open])=>e.open=open));
})();
