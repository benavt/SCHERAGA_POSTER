#!/usr/bin/env python3
"""One-file, offline, presentation-only successor. Refuses to overwrite outputs."""
import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

PINNED = '5ec4cb77883910018fd019b617d8b2993b31cb329e6eee4397bd5216a3db31b3'
VOID = set('area base br col embed hr img input link meta param source track wbr'.split())
def sha(s):
    return hashlib.sha256(s.encode() if isinstance(s, str) else s).hexdigest()

class Structure(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.source=source; self.lines=[0]; self.nodes=[]; self.stack=[]
        for m in re.finditer('\n',source): self.lines.append(m.end())
        self.feed(source)
    def at(self):
        line,col=self.getpos(); return self.lines[line-1]+col
    def handle_starttag(self,tag,attrs):
        n={'tag':tag,'attrs':dict(attrs),'start':self.at(),'start_end':self.at()+len(self.get_starttag_text()),'parent':self.stack[-1] if self.stack else None}
        self.nodes.append(n)
        if tag not in VOID:self.stack.append(n)
    def handle_endtag(self,tag):
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i]['tag']==tag:
                n=self.stack[i];n['end_start']=self.at();n['end']=self.source.index('>',self.at())+1
                del self.stack[i:];return

def scripts(s):
    return [m.group(0) for m in re.finditer(r'<script\b[^>]*>.*?</script>',s,re.S)]
def payloads(s):
    return [sha(m.group(0)) for m in re.finditer(r'data:[^\s"\'<>]+',s)]

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    raw=a.source.read_bytes();assert sha(raw)==PINNED,'Unapproved predecessor hash'
    assert not a.output.exists(),'Immutable output already exists'
    s=raw.decode();tree=Structure(s);edits=[];converted=[];support_counts={}
    for n in tree.nodes:
        attrs=n['attrs'];classes=attrs.get('class','').split();parent=n['parent']
        overview=n['tag']=='details' and 'overview-dropdown' in classes
        support=n['tag']=='details' and parent and 'supplement' in parent['attrs'].get('class','').split()
        if overview or support:
            heading=next(c for c in tree.nodes if c['parent'] is n and c['tag']=='summary')
            start=s[n['start']:n['start_end']].replace('<details','<section',1)
            start=re.sub(r'\sopen(?=[\s>])','',start)
            if overview:start=start.replace('overview-dropdown','poster-section')
            else:
                view=parent['attrs']['data-view'];support_counts[view]=support_counts.get(view,0)+1
                ident=f'figure-{view}-{support_counts[view]}'
                if 'class=' in start:start=start.replace('class="','class="support-figure ',1)
                else:start=start[:-1]+' class="support-figure">'
                start=start[:-1]+f' id="{ident}">'
            ht='h2' if overview else 'h3'
            edits.extend([(n['start'],n['start_end'],start),(n['end_start'],n['end'],'</section>'),(heading['start'],heading['start_end'],s[heading['start']:heading['start_end']].replace('<summary','<'+ht,1)),(heading['end_start'],heading['end'],'</'+ht+'>')])
            converted.append(attrs.get('id',attrs.get('class','support')))
        if n['tag']=='details' and 'movie-entry' in classes:
            start=s[n['start']:n['start_end']]
            edits.append((n['start'],n['start_end'],start[:-1]+f' id="movie-{attrs["data-view"]}">'))
    for start,end,replacement in sorted(edits,reverse=True):s=s[:start]+replacement+s[end:]
    assert len(converted)==12 and support_counts=={'7X7S':3,'Mad2':3}
    # Only UI instructions change; all scientific prose is retained verbatim.
    old='Expand <b>Distance variance</b>, <b>TM-score</b> or <b>Bonsai</b> under Supporting figures as needed. All start minimized and resize to the screen.'
    new='The <b>Distance variance</b>, <b>TM-score</b> and <b>Bonsai</b> supporting figures appear below each movie. Use the page links to move between them.'
    assert s.count(old)==1;s=s.replace(old,new)
    old='All Abstract-page sections can collapse.';assert s.count(old)==1
    s=s.replace(old,'The Abstract-page sections remain visible; use the page links to navigate.')
    nav=next(n for n in tree.nodes if n['tag']=='nav' and n['attrs'].get('class')=='target-tabs')
    # Stable exact boundary outside every embedded payload.
    marker='</nav><section class="working-abstract'
    assert s.count(marker)==1
    s=s.replace(marker,'</nav><nav class="poster-index" aria-label="Sections on this page"></nav><section class="working-abstract',1)
    s=s.replace('<body data-focus="overview">','<body data-focus="overview"><a class="skip-link" href="#working-abstract-title">Skip to poster content</a>',1)
    css=Path(__file__).with_name('editorial.css').read_text()
    js=Path(__file__).with_name('navigation.js').read_text()
    s=s.replace('</head>','<style id="2026-10-23-editorial-design">\n'+css+'</style></head>',1)
    s=s.replace('</body>','<script id="2026-10-23-editorial-navigation">\n'+js+'</script></body>',1)
    original_scripts=scripts(raw.decode());new_scripts=scripts(s)
    assert new_scripts[:-1]==original_scripts,'Existing script changed'
    assert payloads(raw.decode())==payloads(s),'Embedded payload changed'
    before=Structure(raw.decode());after=Structure(s)
    def links(t):return [(n['tag'],n['attrs'].get('href'),n['attrs'].get('download')) for n in t.nodes if n['tag']=='a']
    assert links(before)==[v for v in links(after) if v[1]!='#working-abstract-title'],'Existing links/downloads changed'
    ids=[n['attrs']['id'] for n in after.nodes if 'id' in n['attrs']]
    assert len(ids)==len(set(ids)),'Duplicate IDs'
    a.output.write_text(s)
    report={'status':'PASS_SOURCE_CHECKS_VISUAL_QA_PENDING','created_at':datetime.now(timezone.utc).isoformat(),'predecessor':str(a.source),'predecessor_sha256':PINNED,'output':str(a.output),'output_sha256':sha(s),'output_bytes':len(s.encode()),'existing_script_blocks_preserved':len(original_scripts),'existing_embedded_payloads_preserved':len(payloads(s)),'data_payload_sha256':{n['attrs']['id']:sha(s[n['start_end']:n['end_start']]) for n in after.nodes if n['tag']=='script' and n['attrs'].get('type')=='application/json'},'static_sections_converted':len(converted),'support_figure_counts':support_counts,'default_science_state':'Unmodified original scripts: t-SNE, Boltz2 refold pTM, structure Chainbow','links_and_downloads_preserved':True,'duplicate_ids':False,'changes':['RPI red editorial CSS','Visible overview and support sections','Section jump navigation','Updated two obsolete UI guidance sentences'],'publication':'None; immutable local design draft only'}
    a.output.with_suffix('.validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__': main()
