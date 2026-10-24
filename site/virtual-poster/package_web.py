#!/usr/bin/env python3
"""Externalize an immutable offline poster into a hash-verified static bundle."""
import argparse
import base64
from collections import Counter
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import re
import zipfile

PINNED_OFFLINE_SHA256='f2d01925892f42f0e9336f626c4fedc92a29f13635014b937754afcbc128a5ef'
DATA_URI=re.compile(r'data:([a-z]+/[A-Za-z0-9.+-]+);base64,([A-Za-z0-9+/=]+)')
ASSET_URL=re.compile(r'assets/[a-f0-9]{64}\.[a-z0-9]+')
EXTENSIONS={'image/webp':'webp','image/svg+xml':'svg','image/gif':'gif','image/png':'png','image/jpeg':'jpg','video/mp4':'mp4','font/woff2':'woff2','application/pdf':'pdf','application/octet-stream':'bin','text/plain':'txt'}
ZIP_TIMESTAMP=(2026,10,23,0,0,0)

def digest(value):
    return hashlib.sha256(value).hexdigest()

def json_bytes(value):
    return (json.dumps(value,indent=2,ensure_ascii=False)+'\n').encode()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--expected-sha256',default=PINNED_OFFLINE_SHA256)
    args=parser.parse_args()
    original=args.input.read_bytes()
    if digest(original)!=args.expected_sha256:raise ValueError('Offline predecessor SHA256 does not match')
    if args.output_dir.exists():raise FileExistsError('Immutable output directory already exists')
    text=original.decode('utf-8')
    assets={};reverse={};counts=Counter();occurrences=[]
    def externalize(match):
        mime,encoded=match.groups()
        if mime not in EXTENSIONS:raise ValueError('Unsupported MIME type: '+mime)
        raw=base64.b64decode(encoded,validate=True);sha=digest(raw)
        path='assets/'+sha+'.'+EXTENSIONS[mime]
        if path in text:raise ValueError('Asset URL collides with existing source text')
        if path in reverse and reverse[path]!=match.group(0):raise ValueError('Different URI encodings share one asset URL; round-trip would be ambiguous')
        reverse[path]=match.group(0)
        previous=assets.setdefault(path,{'bytes':raw,'sha256':sha,'mime':mime,'occurrences':0})
        if previous['bytes']!=raw:raise ValueError('Hash collision')
        previous['occurrences']+=1;counts[mime]+=1
        occurrences.append(path)
        return path
    packaged=DATA_URI.sub(externalize,text)
    if not occurrences:raise ValueError('No embedded assets found')
    if DATA_URI.search(packaged):raise ValueError('A base64 URI remains in the web HTML')
    restored=ASSET_URL.sub(lambda match:reverse[match.group(0)],packaged).encode('utf-8')
    if restored!=original:raise ValueError('URI replacement round-trip did not reproduce the offline predecessor exactly')
    site=args.output_dir/'site';asset_dir=site/'assets';asset_dir.mkdir(parents=True)
    (site/'index.html').write_bytes(packaged.encode('utf-8'))
    (site/'.nojekyll').write_bytes(b'')
    for path,entry in sorted(assets.items()):(site/path).write_bytes(entry['bytes'])
    files=[]
    for file in sorted(site.rglob('*')):
        if file.is_file():
            raw=file.read_bytes();files.append({'path':file.relative_to(site).as_posix(),'bytes':len(raw),'sha256':digest(raw)})
    manifest={'schema_version':1,'version':'web-v001','source':{'asset_name':args.input.name,'bytes':len(original),'sha256':digest(original)},'roundtrip_sha256':digest(restored),'files':files,'asset_occurrences':len(occurrences),'unique_assets':len(assets),'asset_types':dict(sorted(counts.items()))}
    (site/'asset-manifest.json').write_bytes(json_bytes(manifest))
    # Manifest is deliberately not a member of its own file hash list. The ZIP
    # hash authenticates it; the manifest authenticates every served payload.
    archive=args.output_dir/'2026-10-23_virtual-poster-web-v001.zip'
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as bundle:
        for file in sorted(site.rglob('*')):
            if file.is_file():
                info=zipfile.ZipInfo(file.relative_to(site).as_posix(),date_time=ZIP_TIMESTAMP)
                info.compress_type=zipfile.ZIP_DEFLATED;info.create_system=3;info.external_attr=0o100644<<16
                bundle.writestr(info,file.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
    with zipfile.ZipFile(archive) as bundle:
        names=bundle.namelist()
        allowed={entry['path'] for entry in files}|{'asset-manifest.json'}
        if set(names)!=allowed or len(names)!=len(allowed):raise ValueError('Unexpected ZIP members')
        for entry in files:
            raw=bundle.read(entry['path'])
            if len(raw)!=entry['bytes'] or digest(raw)!=entry['sha256']:raise ValueError('ZIP member validation failed')
    # Diagnostic sidecars remain outside the public bundle.
    (args.output_dir/'asset-manifest.json').write_bytes(json_bytes(manifest))
    (args.output_dir/'URI-map.json').write_bytes(json_bytes({'source_sha256':digest(original),'occurrences':occurrences,'assets':[{'path':path,'mime':entry['mime'],'bytes':len(entry['bytes']),'sha256':entry['sha256'],'occurrences':entry['occurrences']} for path,entry in sorted(assets.items())]}))
    (args.output_dir/'package_web.py').write_bytes(Path(__file__).read_bytes())
    validation={'status':'PASS_ROUNDTRIP_ASSET_AND_ZIP_CHECKS_BROWSER_QA_PENDING','created_at':datetime.now(timezone.utc).isoformat(),'version':'web-v001','offline_predecessor':args.input.name,'offline_predecessor_sha256':digest(original),'offline_predecessor_bytes':len(original),'index_bytes':len(packaged.encode()),'index_gzip_bytes':len(gzip.compress(packaged.encode(),mtime=0)),'index_sha256':digest(packaged.encode()),'base64_uri_occurrences_externalized':len(occurrences),'unique_assets':len(assets),'unique_asset_bytes':sum(len(entry['bytes']) for entry in assets.values()),'roundtrip_byte_identical':True,'roundtrip_sha256':digest(restored),'all_asset_bytes_verified':True,'all_zip_members_verified':True,'zip':archive.name,'zip_bytes':archive.stat().st_size,'zip_sha256':digest(archive.read_bytes()),'source_script_sha256':digest(Path(__file__).read_bytes()),'runtime_assumptions':'Original scripts use ordinary Image.src and anchor.href; no data-URI-only decoder is present. Existing frame preload behavior is unchanged.','publication':'Prepared static bundle only; no deployment'}
    (args.output_dir/'validation.json').write_bytes(json_bytes(validation))
    print(json.dumps(validation,indent=2))

if __name__=='__main__':main()
