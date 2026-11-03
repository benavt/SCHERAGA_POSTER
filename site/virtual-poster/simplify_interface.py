#!/usr/bin/env python3
"""Repackage the pinned static poster with a presentation-only text cleanup."""
from __future__ import annotations
import argparse,hashlib,json,re,zipfile
from pathlib import Path
ROUTE_NOTE='Cyan trail: visited model order. S / E: movie start / end. Click another representation to feature it in place.'
SOURCE_SHA256='331b1c2711e5815200a565319de00edfe60cb4a2246672b5e7c83d19e8a7ed75'
def simplify(page: str) -> str:
    old=page
    page=page.replace('<span class="eyebrow">Virtual poster</span>','',1)
    pattern=r'(<section class="usage-guide[^>]*>).*?(</section>)'
    replacement=r'\1<h2 id="webpage-guide-title">Interpretation</h2><p>Confidence and structural similarity do not establish equilibrium populations or kinetics.</p>\2'
    page,count=re.subn(pattern,replacement,page,count=1,flags=re.S)
    if count!=1:raise ValueError('Expected the reviewed guide section')
    page=page.replace("['Guide','abstract-section-guide']","['Interpretation','abstract-section-guide']")
    page=page.replace('<p>The structure session requires PyMOL. The HTML and PyMOL session work offline; external links require internet access.</p>','',1)
    page=re.sub(r'<(?:p|h3) class="joint-analysis-label">.*?</(?:p|h3)>','',page,flags=re.S)
    page=page.replace(ROUTE_NOTE,'')
    page=re.sub(r'(<details class="target-movie-methods"[^>]*><summary>.*?</summary>)',r'\1<p>Cyan paths follow the displayed model order; S and E mark the first and last movie frames.</p>',page,flags=re.S)
    # Only editorial navigation and interaction text may change in scripts. All scientific payloads remain exact.
    scripts=lambda s:re.findall(r'<script\b[^>]*>.*?</script>',s,re.S)
    expected=[s.replace("['Guide','abstract-section-guide']","['Interpretation','abstract-section-guide']").replace(ROUTE_NOTE,'') for s in scripts(old)]
    if scripts(page)!=expected:raise ValueError('Unexpected script or scientific JSON change')
    if page==old:raise ValueError('No presentation changes made')
    return page

def build(source: Path, output: Path) -> dict:
    if output.exists():raise ValueError('Use a new output directory')
    if hashlib.sha256(source.read_bytes()).hexdigest()!=SOURCE_SHA256:raise ValueError('Pinned poster bundle differs')
    with zipfile.ZipFile(source) as archive:
        bodies={name:archive.read(name) for name in archive.namelist()}
    inventory=json.loads(bodies['asset-manifest.json'])
    for row in inventory['files']:
        raw=bodies[row['path']]
        if len(raw)!=row['bytes'] or hashlib.sha256(raw).hexdigest()!=row['sha256']:raise ValueError('Invalid source member')
    inventory['version']='web-v004'
    inventory['predecessor_offline_source']=inventory.pop('source')
    inventory['predecessor_roundtrip_sha256']=inventory.pop('roundtrip_sha256')
    inventory['presentation_update']={'predecessor_bundle_sha256':SOURCE_SHA256,
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'scientific_assets_unchanged':True}
    bodies['index.html']=simplify(bodies['index.html'].decode()).encode()
    for row in inventory['files']:
        raw=bodies[row['path']];row.update(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
    bodies['asset-manifest.json']=(json.dumps(inventory,indent=2)+'\n').encode()
    output.mkdir(parents=True)
    site=output/'site';site.mkdir()
    for name,body in bodies.items():
        path=Path(name)
        if path.is_absolute() or '..' in path.parts:raise ValueError('Unsafe archive member')
        dest=site/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(body)
    bundle=output/'2026-11-02_virtual-poster-web-v004.zip'
    with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for name,body in sorted(bodies.items()):archive.writestr(name,body)
    receipt={'schema_version':1,'release_tag':'2026-11-02_virtual-poster-web-v004','asset_name':bundle.name,'sha256':hashlib.sha256(bundle.read_bytes()).hexdigest(),'bytes':bundle.stat().st_size,'source_sha256':SOURCE_SHA256,'scientific_assets_unchanged':len(bodies)-2,'scientific_computation':False}
    (output/'validation.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return receipt
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--source',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();print(json.dumps(build(args.source,args.output),indent=2))
