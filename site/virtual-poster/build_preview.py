#!/usr/bin/env python3
"""Reproduce the compact virtual poster from pinned v025, optionally repairing PSE."""
import argparse
import base64
import hashlib
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from build_editorial import Structure, PINNED, sha, payloads, scripts

HERE=Path(__file__).resolve().parent
def node_html(s,n): return s[n['start']:n.get('end',n['start_end'])]
def replace_nodes(s,edits):
    for start,end,value in sorted(edits,reverse=True):s=s[:start]+value+s[end:]
    return s
def main():
    p=argparse.ArgumentParser();p.add_argument('--source',required=True,type=Path);p.add_argument('--output',required=True,type=Path)
    p.add_argument('--pymol-session',type=Path);p.add_argument('--pymol-guide',type=Path);p.add_argument('--pymol-sha256');p.add_argument('--guide-sha256');p.add_argument('--poster-figures',type=Path);p.add_argument('--design-predecessor',type=Path);a=p.parse_args()
    assert not a.output.exists(),'Immutable output already exists'
    repairing=bool(a.pymol_session or a.pymol_guide)
    if repairing:
        assert all([a.pymol_session,a.pymol_guide,a.pymol_sha256,a.guide_sha256]),'PSE and guide plus both expected hashes required'
        assert sha(a.pymol_session.read_bytes())==a.pymol_sha256
        assert sha(a.pymol_guide.read_bytes())==a.guide_sha256
    with tempfile.TemporaryDirectory(prefix='2026-10-23_poster-editorial-') as tmp:
        intermediate=Path(tmp)/'editorial.html'
        subprocess.run([sys.executable,str(HERE/'build_editorial.py'),'--source',str(a.source),'--output',str(intermediate)],check=True,stdout=subprocess.DEVNULL)
        s=intermediate.read_text()
    tree=Structure(s);edits=[]
    def ident(id):return next(n for n in tree.nodes if n['attrs'].get('id')==id)
    # Short visible labels retain their full accessible names and the same handlers.
    names={'target-guide':('Overview','Abstract and study overview'),'target-AK1':('Adk','E. coli adenylate kinase'),'target-Mad2':('Mad2','MAD2 mitotic spindle checkpoint protein')}
    for id,(short,full) in names.items():
        n=ident(id);start=s[n['start']:n['start_end']][:-1]+f' aria-label="{full}">'
        content=s[n['start_end']:n['end_start']]
        edits.append((n['start'],n['end'],start+f'<span class="desktop-target-label">{content}</span><span class="mobile-target-label" aria-hidden="true">{short}</span></button>'))
    # One download section with the original three anchors and scientific caveat.
    physical=ident('abstract-section-physical');pymol=ident('abstract-section-pymol')
    anchors=[ident(id) for id in ['download-physical-poster','download-pymol-session','download-pymol-guide']]
    download_anchors=[node_html(s,n) for n in anchors]
    if repairing:
        for i,(path,mime) in enumerate([(a.pymol_session,'application/octet-stream'),(a.pymol_guide,'text/plain')],start=1):
            item=download_anchors[i];item=re.sub(r'href="[^"]*"',lambda m:'href="data:'+mime+';base64,'+base64.b64encode(path.read_bytes()).decode()+'"',item,count=1)
            item=re.sub(r'download="[^"]*"',lambda m:'download="'+path.name+'"',item,count=1)
            if i==1:item=re.sub(r'>Download PyMOL session[^<]*<', '>PyMOL session (.pse)<',item)
            download_anchors[i]=item
    note=next((n for n in tree.nodes if 'Adk-session-version-note' in n['attrs'].get('class','').split()),None)
    saved_note='' if repairing or not note else node_html(s,note)
    download='<section class="session-downloads overview-only poster-section" id="abstract-section-downloads" aria-labelledby="downloads-title"><h2 id="downloads-title">Downloads</h2><div class="session-download-actions">'+''.join(download_anchors)+'</div><p class="downloads-note">The structure session requires PyMOL. The HTML and PyMOL session work offline; external links require internet access.</p>'+saved_note+'</section>'
    edits.extend([(physical['start'],physical['end'],download),(pymol['start'],pymol['end'],'')])
    guide=ident('abstract-section-guide')
    guide_html='<section class="usage-guide overview-only poster-section" id="abstract-section-guide" aria-labelledby="webpage-guide-title"><h2 id="webpage-guide-title">Quick guide</h2><ol><li>Use the target tabs and section menu to move between the study overview, movies and supporting figures.</li><li>Tap a representation’s <b>⤢</b> button to feature it. Tap a movie breadcrumb in a projection to seek that observed structure.</li><li><b>Projection colors</b> changes the metric; <b>Structure colors</b> changes the rendering palette. Confidence and structural similarity do not establish equilibrium populations or kinetics.</li></ol></section>'
    edits.append((guide['start'],guide['end'],guide_html))
    # Compact author information, without losing contact or affiliations.
    title=next(n for n in tree.nodes if 'poster-title-copy' in n['attrs'].get('class','').split())
    paras=[n for n in tree.nodes if n['parent'] is title and n['tag']=='p'];assert len(paras)==2
    email=next(n for n in tree.nodes if n['parent'] is paras[0] and n['tag']=='a')
    first=node_html(s,paras[0]);email_html=node_html(s,email);first=first.replace(' · '+email_html,'')
    authors=first+'<details class="author-details" open><summary>Author details and contact</summary><p>'+email_html+'</p>'+node_html(s,paras[1])+'</details>'
    edits.append((paras[0]['start'],paras[1]['end'],authors))
    controls=next(n for n in tree.nodes if n['attrs'].get('class')=='controls')
    children=[n for n in tree.nodes if n['parent'] is controls]
    timeline=ident('scrub');time=ident('time');speed=ident('speed');loop=ident('loop')['parent']
    controls_html=s[controls['start']:controls['start_end']]+''.join(node_html(s,n) for n in children if n not in [timeline,time,speed,loop])+'<div class="playback-timeline">'+node_html(s,timeline)+node_html(s,time)+'<details class="playback-options" open><summary aria-label="Loop and playback speed">Options</summary><div class="playback-options-content">'+node_html(s,loop)+node_html(s,speed)+'</div></details></div></div>'
    edits.append((controls['start'],controls['end'],controls_html))
    # Replace only our v026 navigation layer; scientific script blocks stay exact.
    oldnav=ident('2026-10-23-editorial-navigation')
    edits.append((oldnav['start'],oldnav['end'],'<script id="2026-10-23-mobile-navigation">\n'+(HERE/'mobile-navigation.js').read_text()+'</script>'))
    s=replace_nodes(s,edits)
    # A single sticky navigation wrapper and explicit viewer toolbar slots.
    s=s.replace('<nav class="target-tabs"','<div class="poster-navigation"><nav class="target-tabs"',1)
    marker='<nav class="poster-index" aria-label="Sections on this page"></nav>'
    assert s.count(marker)==1;s=s.replace(marker,marker+'</div>',1)
    for view in ['7X7S','Mad2']:
        marker=f'<div class="movie-playback-slot" data-view="{view}"></div>'
        assert s.count(marker)==1
        s=s.replace(marker,marker+f'<div class="viewer-tools" data-viewer-tools="{view}" aria-label="Viewer display settings"></div>',1)
    sentence='A virtual poster accompanies this physical poster, accessible by QR code.';assert s.count(sentence)==1;s=s.replace('<br>'+sentence,'')
    s=s.replace('<main>','<main id="poster-top">',1)
    # Remove a repeated implementation detail; retain its confidence caveat.
    s,n=re.subn(r' from the literal /ptm confidence field for all 11,000 (?:Adk|Mad2) AIS inputs','',s);assert n==2
    if repairing:
        old='The movie and saved PyMOL session therefore retain earlier AIS states.'
        assert s.count(old)==1
        s=s.replace(old,'The movie retains its earlier AIS states; the downloadable PyMOL session contains the selected S1/S2 structures.')
    s=s.replace('Download physical poster (PDF)','Download poster PDF')
    s=s.replace('as the new highest matches, shown as physical-poster S1/S2.','as the highest reference matches.')
    s=s.replace('its starting model differs from the physical poster’s updated S1.','its starting model differs from the selected S1 state.')
    heading='TM-score · all cluster medoids and reference states';assert s.count(heading)==2
    s=s.replace(heading,'TM-score comparisons')
    # Keep the actual route/methods; omit revision and candidate-review history.
    standalone_tree=Structure(s);history_edits=[]
    for node in standalone_tree.nodes:
        if node['tag']=='p' and node['parent'] and 'target-movie-methods' in node['parent']['attrs'].get('class','').split() and 'The expanded' in node_html(s,node):
            history_edits.append((node['start'],node['end'],''))
    assert len(history_edits)==2
    s=replace_nodes(s,history_edits)
    s=s.replace('The movie retains its original observed endpoints:','The movie uses the observed endpoints:')
    s=s.replace('; only projection positions, cluster labels and the matching tree are refreshed.','.')
    s=s.replace('Only their projection positions, cluster labels and matching tree are refreshed for the expanded cohort.','')
    s=s.replace('</head>','<style id="2026-10-23-phone-tablet">\n'+(HERE/'mobile.css').read_text()+'</style></head>',1)
    font_manifest=json.loads((HERE/'fonts'/'manifest.json').read_text())
    font_rules=[]
    for name,entry in font_manifest['files'].items():
        font=(HERE/'fonts'/name).read_bytes();assert sha(font)==entry['sha256'],'Font source hash changed'
        font_rules.append('@font-face{font-family:"'+entry['family']+'";src:url(data:font/woff2;base64,'+base64.b64encode(font).decode()+') format("woff2");font-weight:100 900;font-style:normal;font-display:swap}')
    font_rules.append((HERE/'brand.css').read_text())
    s=s.replace('</head>','<style id="2026-10-23-rpi-typography">'+''.join(font_rules)+'</style></head>',1)
    s=s.replace('</body>','<template id="geist-font-license">'+html.escape((HERE/'fonts'/'OFL.txt').read_text())+'</template></body>',1)
    assert sha((HERE/'fonts'/'OFL.txt').read_bytes())==font_manifest['license_sha256']
    removed_crop_uris=[];added_poster_uris=[];poster_manifest=None
    if a.poster_figures:
        poster_manifest=json.loads(a.poster_figures.read_text());matrix_tree=Structure(s);matrix_edits=[]
        for grid in [n for n in matrix_tree.nodes if n['attrs'].get('class')=='tm-readable-grid']:
            view=grid['attrs']['data-tm-view'];count=grid['attrs']['data-tm-count'];entry=poster_manifest['files'][view]
            figures=[n for n in matrix_tree.nodes if n['parent'] is grid and n['tag']=='figure']
            full=next(n for n in figures if n['attrs'].get('data-tm-page')=='all')
            full_image=next(n for n in matrix_tree.nodes if n['parent'] is full and n['tag']=='img')
            uri=full_image['attrs']['src'];assert sha(base64.b64decode(uri.split(',',1)[1]))==entry['full_matrix_sha256']
            for figure in figures:
                if figure is not full:
                    image=next(n for n in matrix_tree.nodes if n['parent'] is figure and n['tag']=='img');removed_crop_uris.append(image['attrs']['src'])
            image_bytes=(a.poster_figures.parent/entry['path']).read_bytes();assert sha(image_bytes)==entry['sha256']
            poster_uri='data:image/png;base64,'+base64.b64encode(image_bytes).decode();added_poster_uris.append(poster_uri)
            full_title=f'All clusters and references ({count} × {count})';poster_title='Selected states and references (4 × 4)'
            zoom_hint='<span class="matrix-zoom-hint" aria-hidden="true">⤢</span>'
            panel='<div class="tm-comparison" data-tm-view="'+view+'"><figure><h4>'+full_title+'</h4><button class="figure-zoom" aria-label="Enlarge '+full_title+'">'+zoom_hint+node_html(s,full_image)+'</button><figcaption>Cluster representatives are medoids.</figcaption></figure><figure><h4>'+poster_title+'</h4><button class="figure-zoom" aria-label="Enlarge selected states and references matrix">'+zoom_hint+'<img class="tm-readable-image" loading="lazy" src="'+poster_uri+'" alt="'+html.escape(('Adk' if view=='7X7S' else 'Mad2')+' selected states and references TM matrix: '+', '.join(entry['labels']))+'"></button><figcaption>S1 and S2 are selected by similarity to the open and closed references.</figcaption></figure></div>'
            matrix_edits.append((grid['start'],grid['end'],panel))
        assert len(removed_crop_uris)==4 and len(added_poster_uris)==2
        s=replace_nodes(s,matrix_edits)
    original=a.source.read_text();original_scripts=scripts(original);result_scripts=scripts(s)
    assert result_scripts[:-1]==original_scripts,'Original scientific scripts changed'
    before_payloads=payloads(original)
    # The two additional font assets are presentation; scientific payload order
    # and all prior data URIs remain checked independently.
    science_uri_source=re.sub(r'data:font/woff2[^\s"\'<>)}]+','EMBEDDED_FONT',s)
    if a.poster_figures:
        for uri in removed_crop_uris:original_without_crop=original.replace(uri,'REMOVED_DISPLAY_CROP',1);original=original_without_crop
        for uri in added_poster_uris:science_uri_source=science_uri_source.replace(uri,'ADDED_VERIFIED_POSTER_FIGURE',1)
        before_payloads=payloads(original)
    after_payloads=payloads(science_uri_source)
    if not repairing:assert before_payloads==after_payloads,'Embedded data changed'
    else:
        assert len(before_payloads)==len(after_payloads)
        assert sum(x!=y for x,y in zip(before_payloads,after_payloads))==2,'Expected only session and guide to change'
    parsed=Structure(s);ids=[n['attrs']['id'] for n in parsed.nodes if 'id'in n['attrs']];assert len(ids)==len(set(ids))
    orig_data={n['attrs']['id']:sha(original[n['start_end']:n['end_start']]) for n in Structure(original).nodes if n['tag']=='script' and n['attrs'].get('type')=='application/json'}
    data={n['attrs']['id']:sha(s[n['start_end']:n['end_start']]) for n in parsed.nodes if n['tag']=='script' and n['attrs'].get('type')=='application/json'};assert data==orig_data
    a.output.parent.mkdir(parents=True,exist_ok=True)
    source_snapshot=a.output.with_suffix('.sources');assert not source_snapshot.exists(),'Immutable source snapshot already exists'
    source_snapshot.mkdir()
    source_hashes={}
    for file in sorted(HERE.rglob('*')):
        if file.is_file() and file.suffix in ['.py','.css','.js','.md','.json','.woff2','.txt','.png']:
            relative=file.relative_to(HERE);destination=source_snapshot/relative;destination.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(file,destination);source_hashes[str(relative)]=sha(file.read_bytes())
    a.output.write_text(s)
    report={'status':'PASS_SOURCE_CHECKS_BROWSER_QA_PENDING','created_at':datetime.now(timezone.utc).isoformat(),'predecessor':str(a.source),'predecessor_sha256':PINNED,'output':str(a.output),'output_bytes':len(s.encode()),'output_sha256':sha(s),'original_script_blocks_preserved':len(original_scripts),'unchanged_scientific_json_payloads':data,'data_uri_payload_count':len(after_payloads),'data_uri_payload_changes':2 if repairing else 0,'pymol_repaired':repairing,'pymol_session_source':str(a.pymol_session) if repairing else None,'pymol_guide_source':str(a.pymol_guide) if repairing else None,'pymol_sha256':a.pymol_sha256,'pymol_guide_sha256':a.guide_sha256,'source_directory':str(HERE),'immutable_source_snapshot':str(source_snapshot),'source_sha256':source_hashes,'publication':'Local preview only'}
    report['font_manifest']=font_manifest;report['additional_embedded_fonts']=len(font_manifest['files'])
    report['poster_figure_manifest']=poster_manifest;report['removed_Mad2_display_crops']=len(removed_crop_uris)
    report['design_predecessor']=str(a.design_predecessor) if a.design_predecessor else None
    report['design_predecessor_sha256']=sha(a.design_predecessor.read_bytes()) if a.design_predecessor else None
    a.output.with_suffix('.validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
