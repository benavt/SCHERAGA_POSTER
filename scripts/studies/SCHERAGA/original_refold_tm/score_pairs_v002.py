"""Approval-gated measured TM similarity of exact original/refold pairs.

Prepared source only until execution-approval.json binds the frozen plan.
Native coordinates are read only; ephemeral C-alpha inputs use the established
0.001-A PDB representation. No confidence values enter the measured score.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from io import StringIO
import argparse, re, csv, gzip, hashlib, json, math, os, resource, shutil, subprocess, sys, tempfile, time
from Bio.PDB import PDBParser, MMCIFParser
from Bio.Data.PDBData import protein_letters_3to1

R=Path(__file__).resolve().parent
EXE=None
parse_average_length_tm=None
OPTIONS=['-mol','prot','-ter','1','-a','T']
sha=lambda raw:hashlib.sha256(raw).hexdigest()
PLAN=None;APPROVAL=None
def write(p,data):
    Path(p).write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
def gate():
    assert APPROVAL['approved'] and sha((R/'execution-plan.json').read_bytes())==APPROVAL['plan_sha256']
    assert time.time()-APPROVAL['started_epoch']<7200 and shutil.disk_usage(R).free>50*2**30
def storage_gate():
    inodes={}
    for base,dirs,files in os.walk(R):
        for name in files:
            p=Path(base)/name
            if p.is_symlink():continue
            st=p.stat();key=(st.st_dev,st.st_ino)
            if key not in inodes:inodes[key]=[st,0]
            inodes[key][1]+=1
    used=sum(st.st_blocks*512 for st,count in inodes.values()if count==st.st_nlink)
    assert used<.75*2**30,(used,'0.75GiB run cap')
    return used

def ca_pdb(path,expected_sha,n,sequence_sha):
    raw=Path(path).read_bytes();assert sha(raw)==expected_sha,path
    text=raw.decode();parser=MMCIFParser(QUIET=True)if re.search(r'(?m)^\s*data_',text)else PDBParser(QUIET=True)
    structure=parser.get_structure('input',StringIO(text));assert len(structure)==1,path
    model=next(iter(structure));chains=[c for c in model if any('CA'in res for res in c)]
    assert len(chains)==1 and chains[0].id=='A',path
    residues=[r for r in chains[0]if 'CA'in r];assert [r.id for r in residues]==[(' ',i,' ')for i in range(1,n+1)],path
    sequence=''.join(protein_letters_3to1[r.resname]for r in residues);assert sha(sequence.encode())==sequence_sha,path
    lines=[]
    for i,res in enumerate(residues,1):
        atom=res['CA'];assert not atom.is_disordered(),path
        coords=[float(v)for v in atom.coord];assert all(math.isfinite(v)for v in coords)
        xyz=[f'{v:8.3f}'for v in coords];assert all(abs(float(x)-v)<=.00051 for x,v in zip(xyz,coords))
        lines.append(f'ATOM  {i:5d}  CA  {res.resname:>3s} A{i:4d}    '+''.join(xyz)+'  1.00  0.00           C\n')
    return (''.join(lines)+'TER\nEND\n').encode()
def compare(pair):
    gate();n=pair['residue_count'];inputs=[ca_pdb(pair[s+'_path'],pair[s+'_sha256'],n,pair['sequence_sha256'])for s in ['original','refold']]
    directions=[]
    with tempfile.TemporaryDirectory(prefix='pair-',dir=R/'tmp')as folder:
        paths=[Path(folder)/name for name in ['original.pdb','refold.pdb']]
        for p,raw in zip(paths,inputs):p.write_bytes(raw)
        for left,right in [(0,1),(1,0)]:
            gate();cmd=[str(EXE),str(paths[left]),str(paths[right]),*OPTIONS]
            result=subprocess.run(cmd,capture_output=True,text=True,timeout=180,check=True)
            value=parse_average_length_tm(result.stdout);assert math.isfinite(value)and 0<=value<=1
            directions.append({'orientation':'original_to_refold'if left==0 else'refold_to_original','TM_score':value,'stdout':result.stdout,'stderr':result.stderr,'options':OPTIONS})
    row={k:pair[k]for k in ['target','view_key','model','method','residue_count','sequence_sha256','original_sha256','refold_sha256']}
    row.update(original_CA_input_sha256=sha(inputs[0]),refold_CA_input_sha256=sha(inputs[1]),original_to_refold_TM=directions[0]['TM_score'],refold_to_original_TM=directions[1]['TM_score'],mean_bidirectional_TM=sum(d['TM_score']for d in directions)/2)
    return {'row':row,'directions':directions}
def main():
    global PLAN,APPROVAL,EXE,parse_average_length_tm
    APPROVAL=json.loads((R/'execution-approval.json').read_text());PLAN=json.loads((R/'execution-plan.json').read_text());gate();storage_gate()
    EXE=Path(PLAN['source_pins']['USalign']['path']);assert sha(EXE.read_bytes())==PLAN['source_pins']['USalign']['sha256']
    parser_path=Path(PLAN['source_pins']['TM_parser']['path']);assert sha(parser_path.read_bytes())==PLAN['source_pins']['TM_parser']['sha256']
    sys.path.insert(0,str(parser_path.parents[2]))
    from src.analysis.cluster_medoid_tm import parse_average_length_tm as frozen_parser
    assert Path(sys.modules[frozen_parser.__module__].__file__).resolve()==parser_path.resolve()
    parse_average_length_tm=frozen_parser
    assert sha((R/'paired-inputs.json').read_bytes())==PLAN['source_pins']['pairs']['sha256']
    recovery=json.loads((R/'implementation-recovery.json').read_text());assert recovery['plan_sha256']==APPROVAL['plan_sha256']
    assert sha((R/'score_pairs.py').read_bytes())==PLAN['source_pins']['scorer']['sha256']==recovery['original_scorer_sha256']
    assert sha(Path(__file__).read_bytes())==recovery['corrected_scorer_sha256']
    seed=Path(recovery['completed_evidence']['path']);assert sha(seed.read_bytes())==recovery['completed_evidence']['sha256']
    cached=[json.loads(line)for line in gzip.open(seed,'rt')];assert len(cached)==recovery['completed_pairs']==5
    pairs=json.loads((R/'paired-inputs.json').read_text())['pairs'];assert len(pairs)==22000
    assert len({(p['target'],p['model'])for p in pairs})==22000
    out=R/'scoring-v002';out.mkdir(exist_ok=True);(R/'tmp').mkdir(exist_ok=True)
    evidence=out/'paired-TM-evidence.jsonl.gz';assert not evidence.exists(),'Preserve partial evidence; explicit recovery review required'
    pilot_keys={tuple(k)for k in PLAN['pilot_model_keys']};seed_keys={(x['row']['target'],x['row']['model'])for x in cached};assert len(seed_keys)==5 and seed_keys<=pilot_keys
    by_key={(p['target'],p['model']):p for p in pairs}
    for entry in cached:
        row=entry['row'];pair=by_key[(row['target'],row['model'])]
        for field in ['original_sha256','refold_sha256','sequence_sha256','residue_count']:assert row[field]==pair[field]
        for side in ['original','refold']:
            raw=ca_pdb(pair[side+'_path'],pair[side+'_sha256'],pair['residue_count'],pair['sequence_sha256']);assert sha(raw)==row[side+'_CA_input_sha256']
        values=[parse_average_length_tm(d['stdout'])for d in entry['directions']];assert all(d['options']==OPTIONS and d['TM_score']==value for d,value in zip(entry['directions'],values))
        assert row['mean_bidirectional_TM']==sum(values)/2
    pilot=[p for p in pairs if (p['target'],p['model'])in pilot_keys-seed_keys];assert len(pilot)==3
    remaining=[p for p in pairs if (p['target'],p['model'])not in pilot_keys];rows=[]
    with gzip.open(evidence,'xt')as f:
        def record(result):
            rows.append(result['row']);f.write(json.dumps(result,separators=(',',':'))+'\n')
            if len(rows)%250==0:
                f.flush();gate();storage_gate();write(out/'progress.json',{'pairs_complete':len(rows),'directional_calls_complete':2*len(rows),'cap':44000});print('PAIR METRICS',len(rows),flush=True)
        for entry in cached:record(entry)
        for p in pilot:record(compare(p))
        write(out/'pilot-validation.json',{'status':'PASS','pairs':8,'directional_calls':16,'reused_pairs':5,'new_pairs_this_attempt':3,'input_CA_identity_and_full_sequence_checked':True,'scores_in_0_1':True})
        iterator=iter(remaining)
        with ThreadPoolExecutor(max_workers=4)as pool:
            pending={pool.submit(compare,next(iterator))for _ in range(4)}
            try:
                while pending:
                    done,pending=wait(pending,return_when=FIRST_COMPLETED)
                    for future in done:
                        record(future.result())
                        item=next(iterator,None)
                        if item is not None:pending.add(pool.submit(compare,item))
            except BaseException:
                for future in pending:future.cancel()
                raise
    assert len(rows)==22000 and 2*len(rows)==44000;rows.sort(key=lambda q:(q['target'],q['model']))
    with (out/'original-refold-TM.csv').open('x')as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    write(out/'completion.json',{'status':'PASS','pairs':22000,'directional_calls':44000,'new_directional_calls_this_attempt':43990,'reused_verified_directional_calls':10,'implementation_recovery':str(R/'implementation-recovery.json'),'full_residues':{'Adk':214,'Mad2':197},'normalization':'mean_bidirectional_average_length_usalign','coordinate_representation':'Ephemeral CA-only PDB,0.001A; no transformations/repairs/source edits','score_table_sha256':sha((out/'original-refold-TM.csv').read_bytes()),'evidence_sha256':sha(evidence.read_bytes()),'engine_sha256':sha(EXE.read_bytes()),'options':OPTIONS});gate();storage_gate();print('ALL ORIGINAL/REFOLD TM COMPLETE',flush=True)
if __name__=='__main__':
    args_parser=argparse.ArgumentParser(description=__doc__);args_parser.add_argument('--run-dir',required=True,type=Path);args=args_parser.parse_args();R=args.run_dir.resolve()
    assert hasattr(os,'sched_setaffinity'),'Approved scientific host requires Linux CPU affinity'
    os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[:4])
    resource.setrlimit(resource.RLIMIT_AS,(8*2**30,8*2**30))
    try:main()
    except BaseException as error:
        write(R/'scoring-v002-error.json',{'error':str(error),'automatic_retries':0});raise
