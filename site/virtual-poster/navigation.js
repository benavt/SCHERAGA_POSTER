/* Editorial navigation only. Original scientific scripts and state are untouched. */
(()=>{
 'use strict';
 const index=document.querySelector('.poster-index');
 const overview=[['Abstract','working-abstract-title'],['Reference states','abstract-section-experimental'],['Downloads','abstract-section-physical'],['Guide','abstract-section-guide'],['References','abstract-section-references'],['Acknowledgments','abstract-section-acknowledgments']];
 function refresh(){
  const view=document.body.dataset.focus;
  const links=view==='overview'?overview:[['Movie','movie-'+view],['Distance variance','figure-'+view+'-1'],['TM-score','figure-'+view+'-2'],['Bonsai','figure-'+view+'-3']];
  index.replaceChildren();
  const label=document.createElement('span');label.className='index-label';label.textContent='On this page';index.appendChild(label);
  for(const[text,id]of links){const a=document.createElement('a');a.href='#'+id;a.textContent=text;index.appendChild(a);}
 }
 index.addEventListener('click',event=>{
  const a=event.target.closest('a');if(!a)return;
  const target=document.getElementById(a.getAttribute('href').slice(1));
  if(target?.matches('details'))target.open=true;
 });
 for(const b of document.querySelectorAll('[data-target]'))b.addEventListener('click',()=>{
  refresh();
  if(b.dataset.target!=='overview')requestAnimationFrame(()=>document.querySelector('.target-page[data-view="'+b.dataset.target+'"]').scrollIntoView({block:'start'}));
 });
 refresh();
})();
