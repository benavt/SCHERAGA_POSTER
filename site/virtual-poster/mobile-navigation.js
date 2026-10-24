/* Presentation controls delegate to the original validated scientific handlers. */
(()=>{
 'use strict';
 const index=document.querySelector('.poster-index'),navigation=document.querySelector('.poster-navigation');
 const phone=matchMedia('(max-width:600px)'),compact=matchMedia('(max-width:1200px)');
 const authors=document.querySelector('.author-details'),options=document.querySelector('.playback-options');
 if(authors){authors.open=!phone.matches;phone.addEventListener('change',e=>authors.open=!e.matches);}
 if(options){options.open=!compact.matches;compact.addEventListener('change',e=>options.open=!e.matches);}
 const overview=[['Abstract','working-abstract-title'],['Reference states','abstract-section-experimental'],['Downloads','abstract-section-downloads'],['Guide','abstract-section-guide'],['References','abstract-section-references'],['Acknowledgments','abstract-section-acknowledgments']];
 let observer;
 function currentLinks(){const view=document.body.dataset.focus;return view==='overview'?overview:[['Movie','movie-'+view],['Distance variance','figure-'+view+'-1'],['TM-score','figure-'+view+'-2'],['Bonsai','figure-'+view+'-3']];}
 function mark(id){for(const a of index.querySelectorAll('[data-section-link]')){const active=a.dataset.sectionLink===id;a.classList.toggle('current-section',active);if(active)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current');}const select=index.querySelector('select');if(select&&[...select.options].some(o=>o.value===id))select.value=id;}
 function scrollToElement(target){if(!target)return;const offset=navigation.getBoundingClientRect().height;window.scrollTo({top:Math.max(0,target.getBoundingClientRect().top+scrollY-offset-3),behavior:'auto'});}
 function afterLayout(fn){requestAnimationFrame(()=>requestAnimationFrame(()=>requestAnimationFrame(fn)));}
 function jump(id){const target=document.getElementById(id);if(!target)return;if(target.matches('details'))target.open=true;afterLayout(()=>scrollToElement(target));mark(id);}
 function refresh(){
  const links=currentLinks();index.replaceChildren();
  const label=document.createElement('label');label.className='section-picker-label';const text=document.createElement('span');text.textContent='Jump to';const select=document.createElement('select');select.className='section-picker';select.setAttribute('aria-label','Sections on this poster page');for(const[name,id]of links){const o=document.createElement('option');o.textContent=name;o.value=id;select.appendChild(o);}select.addEventListener('change',()=>jump(select.value));label.append(text,select);index.appendChild(label);
  const desktopLabel=document.createElement('span');desktopLabel.className='index-label';desktopLabel.textContent='On this page';index.appendChild(desktopLabel);
  for(const[name,id]of links){const a=document.createElement('a');a.href='#'+id;a.textContent=name;a.dataset.sectionLink=id;a.addEventListener('click',e=>{e.preventDefault();jump(id);});index.appendChild(a);}
  const top=document.createElement('a');top.className='poster-top';top.href='#poster-top';top.textContent='Top ↑';top.setAttribute('aria-label','Back to poster title');top.addEventListener('click',e=>{e.preventDefault();scrollToElement(document.getElementById('poster-top'));});index.appendChild(top);
  mark(links[0][1]);observer?.disconnect();if('IntersectionObserver'in window){observer=new IntersectionObserver(entries=>{const visible=entries.filter(e=>e.isIntersecting).sort((a,b)=>a.boundingClientRect.top-b.boundingClientRect.top);if(visible.length)mark(visible[0].target.id);},{rootMargin:'-48px 0px -55% 0px',threshold:0});for(const[,id]of links){const t=document.getElementById(id);if(t)observer.observe(t);}}
 }
 function activeViewer(){return document.querySelector('.target[data-view="'+document.body.dataset.focus+'"]');}
 for(const b of document.querySelectorAll('[data-target]'))b.addEventListener('click',()=>{refresh();afterLayout(()=>{if(b.dataset.target==='overview')scrollToElement(document.getElementById('working-abstract-title'));else{const movie=document.querySelector('.movie-entry[data-view="'+b.dataset.target+'"]');if(movie)movie.open=true;scrollToElement(activeViewer());}});});
 for(const toolbar of document.querySelectorAll('[data-color-toolbar]')){
  const buttons=[...toolbar.querySelectorAll('[data-color-mode]')];if(!buttons.length)continue;
  const label=document.createElement('label');label.className='mobile-projection-control';const title=document.createElement('span');title.textContent='Plot';const select=document.createElement('select');select.setAttribute('aria-label','Projection colors for '+(toolbar.dataset.view==='Mad2'?'Mad2':'adenylate kinase'));
  for(const b of buttons){const o=document.createElement('option');o.value=b.dataset.colorMode;o.textContent=b.textContent.trim();select.appendChild(o);}
  function sync(){const selected=buttons.find(b=>b.getAttribute('aria-pressed')==='true');if(selected)select.value=selected.dataset.colorMode;}
  select.addEventListener('change',()=>{buttons.find(b=>b.dataset.colorMode===select.value)?.click();sync();});
  for(const b of buttons)new MutationObserver(sync).observe(b,{attributes:true,attributeFilter:['aria-pressed']});
  label.append(title,select);toolbar.classList.add('has-mobile-selector');document.querySelector('[data-viewer-tools="'+toolbar.dataset.view+'"]').appendChild(label);sync();
 }
 for(const toolbar of document.querySelectorAll('.structure-color-menu')){
  const buttons=[...toolbar.querySelectorAll('[data-structure-mode]')];if(!buttons.length)continue;const view=buttons[0].dataset.structureView;
  const label=document.createElement('label');label.className='viewer-palette';const title=document.createElement('span');title.textContent='Structure';const select=document.createElement('select');select.setAttribute('aria-label','Structure palette for '+(view==='Mad2'?'Mad2':'adenylate kinase'));
  for(const b of buttons){const o=document.createElement('option');o.value=b.dataset.structureMode;o.textContent=b.textContent.trim();select.appendChild(o);}
  function sync(){for(const o of select.options)o.disabled=!!buttons.find(b=>b.dataset.structureMode===o.value)?.disabled;const selected=buttons.find(b=>b.getAttribute('aria-pressed')==='true');if(selected)select.value=selected.dataset.structureMode;}
  select.addEventListener('change',()=>{buttons.find(b=>b.dataset.structureMode===select.value)?.click();sync();});for(const b of buttons)new MutationObserver(sync).observe(b,{attributes:true,attributeFilter:['aria-pressed','disabled']});
  label.append(title,select);toolbar.classList.add('has-viewer-selector');const tools=document.querySelector('[data-viewer-tools="'+view+'"]');tools.prepend(label);sync();
 }
 for(const caption of document.querySelectorAll('.frame-caption')){function describe(){caption.title=[caption.querySelector('.model-id')?.textContent,caption.querySelector('[id$="-group"]')?.textContent].filter(Boolean).join(' · ');}new MutationObserver(describe).observe(caption,{subtree:true,childList:true,characterData:true});describe();}
 for(const button of document.querySelectorAll('.figure-zoom'))button.addEventListener('click',()=>document.querySelector('#support-dialog>img')?.classList.toggle('matrix-zoom',!!button.closest('.tm-comparison')));
 // The original presentation listener scrolls to its legend. Keep the viewer
 // pair stable after featuring a different plot, without changing its handler.
 for(const button of document.querySelectorAll('.plot .expand'))button.addEventListener('click',()=>{if(compact.matches)afterLayout(()=>scrollToElement(activeViewer()));});
 let wasLandscape=matchMedia('(orientation:landscape) and (max-height:550px)').matches;
 addEventListener('resize',()=>{const now=matchMedia('(orientation:landscape) and (max-height:550px)').matches;if(now!==wasLandscape&&document.body.dataset.focus!=='overview')afterLayout(()=>scrollToElement(activeViewer()));wasLandscape=now;});
 refresh();
})();
