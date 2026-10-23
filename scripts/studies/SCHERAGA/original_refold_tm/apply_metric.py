"""SOURCE-ONLY draft: add a measured AIS/refold TM coloring to frozen poster v018.

No files are exported by this module. No scoring, fitting, browser fixture, movie
rendering or inference is performed. Call apply_metric only after the new
scientific/export plan is explicitly approved and all measured scores validate.

Caller input contract (both objects status=PASS):
  expected_pairs = {parent_html_sha256, targets: {view: {ca_count, rows: [
    {model_id, ais_sha256, refold_sha256}, ...]}}}
  measured = {metric_definition: METRIC_DEFINITION,
              targets: {view: {ca_count, rows: [
                {model_id, ais_sha256, refold_sha256, ais_refold_tm}, ...]}}}
Use views7X7S (current1AKE sequence) andMad2,11000 rows each. No partial data,
confidence substitutions or row-index joins are accepted. PDB controls unscored.
"""
from pathlib import Path
import copy, hashlib, json, math, re

PARENT_SHA256='5468a4c75868b6dfb20fa0f1b212f370983353d4a3ce0c643711fc8e95d1e2b0'
METRIC='ais_refold_tm'
METRIC_DEFINITION='mean_bidirectional_USalign_TM_average_length_normalized_full_CA'
TARGETS={'7X7S':214,'Mad2':197}
BUTTON='AIS ↔ Boltz2 refold TM'
HEX_SHA=re.compile(r'^[0-9a-f]{64}$')


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def script_json(text, ident):
    match=re.search(r'<script[^>]*id="'+re.escape(ident)+r'"[^>]*>(.*?)</script>',text,re.S)
    assert match,ident
    return json.loads(match[1])



def protected_fragments(text):
    start=text.index('<section class="working-abstract')
    depth=0
    abstract=None
    for token in re.finditer(r'</?section\b[^>]*>',text[start:]):
        depth += -1 if token[0].startswith('</') else 1
        if depth==0:
            abstract=text[start:start+token.end()]
            break
    assert abstract is not None
    references=re.findall(r'<li\b[^>]*id="reference-\d+"[^>]*>.*?</li>',text,re.S)
    assert len(references)==14
    downloads=re.findall(r'<a\b[^>]*\bdownload="[^\"]+"[^>]*>',text)
    styles=re.findall(r'<style[^>]*>.*?</style>',text,re.S)
    return {'abstract':digest(abstract.encode()),
            'references':digest(''.join(references).encode()),
            'all_existing_download_anchors':digest(''.join(downloads).encode()),
            'styles':digest(''.join(styles).encode())}


def _replace_once(text, old, new):
    assert text.count(old)==1,('Unexpected source splice count',old[:90],text.count(old))
    return text.replace(old,new,1)


def patch_UI_source(text):
    """Pure in-memory source splice. Does not inspect or manufacture scores."""
    assert 'data-color-mode="ais_refold_tm"'not in text,'Metric already installed'
    for view,ca_count in TARGETS.items():
        start=text.index('<div class="support-color-menu" data-color-toolbar data-view="'+view+'"')
        end=text.index('</div>',start)
        chunk=text[start:end]
        button='<button type="button" data-color-mode="boltz2_refold_ptm" aria-pressed="true">Boltz2 refold pTM</button>'
        assert chunk.count(button)==1
        addition='<button type="button" data-color-mode="ais_refold_tm" aria-pressed="false">'+BUTTON+'</button>'
        chunk=chunk.replace(button,button+addition,1)
        text=text[:start]+chunk+text[end:]
        start=text.index('<p class="reference-caption" data-color-caption data-view="'+view+'"')
        end=text.index('</p>',start)
        caption='<span class="ais-refold-tm-caption" hidden> Projection colors show measured mean bidirectional US-align<sup class="citation"><a href="#reference-13" aria-label="Reference 13">13</a></sup> TM similarity between each original AIS model and its matched Boltz2 exact template-only refold, with full-length Cα inputs ('+str(ca_count)+' positions). This measures coordinate similarity, not confidence. Experimental PDB controls remain unscored.</span>'
        text=text[:end]+caption+text[end:]
    text=_replace_once(text,
        "if(key==='confidence'||key==='tm'||key==='boltz2_refold_ptm'){",
        "if(['confidence','tm','boltz2_refold_ptm','ais_refold_tm'].includes(key)){")
    text=_replace_once(text,
        "label=key==='confidence'?'native pTM':key==='boltz2_refold_ptm'?'Boltz2 refold pTM':'TM similarity to '+reference;",
        "label=key==='confidence'?'native pTM':key==='boltz2_refold_ptm'?'Boltz2 refold pTM':key==='ais_refold_tm'?'AIS ↔ refold TM':'TM similarity to '+reference;")
    text=_replace_once(text,
        "caption.hidden=!['confidence','tm','boltz2_refold_ptm'].includes(key);",
        "caption.hidden=!['confidence','tm','boltz2_refold_ptm','ais_refold_tm'].includes(key);")
    text=_replace_once(text,
        "if(refoldCaption)refoldCaption.hidden=key!=='boltz2_refold_ptm';caption.dataset.colorMode=key;",
        "if(refoldCaption)refoldCaption.hidden=key!=='boltz2_refold_ptm';const pairedCaption=caption.querySelector('.ais-refold-tm-caption');if(pairedCaption)pairedCaption.hidden=key!=='ais_refold_tm';caption.dataset.colorMode=key;")
    # Same current-frame TM/readout line; present only while this coloring is active.
    frame="e.tm.appendChild(refoldItem);e.tm.dataset.model=f.model;"
    frame_new="e.tm.appendChild(refoldItem);if(d.display_color_mode==='ais_refold_tm'){const value=d.color_schemes.ais_refold_tm?.values?.[f.model_index],item=document.createElement('span');item.dataset.metric='ais_refold_tm';item.dataset.model=f.model;item.title='Measured original AIS versus matched Boltz2 exact template-only refold TM similarity; full predicted chain, not confidence';item.textContent=Number.isFinite(value)?'AIS ↔ refold TM: '+value.toFixed(2):'AIS ↔ refold TM unavailable';e.tm.appendChild(item);}e.tm.dataset.model=f.model;"
    text=_replace_once(text,frame,frame_new)
    assert text.count('data-color-mode="ais_refold_tm"')==2
    assert text.count('class="ais-refold-tm-caption"')==2
    # Defaults are deliberately unchanged; the existing pTM initialization remains.
    default="mode(view,review.data.targets[view].color_schemes.boltz2_refold_ptm?.values?.some(Number.isFinite)?'boltz2_refold_ptm':'confidence');"
    assert text.count(default)==1
    return text


def _indexed_rows(target, expected_ids):
    rows=target['rows']
    assert len(rows)==11000
    lookup={r['model_id']:r for r in rows}
    assert len(lookup)==len(rows)and set(lookup)==expected_ids
    for row in rows:
        assert HEX_SHA.fullmatch(row['ais_sha256'])and HEX_SHA.fullmatch(row['refold_sha256'])
    return lookup


def _scheme(models, measured, expected):
    # Matplotlib import/normalization occurs only during an approved adapter call.
    from matplotlib import colormaps,colors
    values=[]
    for model in models:
        if model.startswith('PDB_REF'):
            values.append(None)
            continue
        score=measured[model]
        pair=expected[model]
        assert score['ais_sha256']==pair['ais_sha256']and score['refold_sha256']==pair['refold_sha256'],model
        value=score[METRIC]
        assert isinstance(value,(float,int))and not isinstance(value,bool)and math.isfinite(value)and 0<=value<=1,model
        values.append(value)
    finite=[float(v)for v in values if v is not None]
    assert len(finite)==11000
    low,high=min(finite),max(finite)
    palette=colormaps['plasma']
    fills=['#bfc3c7'if v is None else colors.to_hex(palette((float(v)-low)/(high-low)if high>low else .5))for v in values]
    return {'metric':'Measured original AIS ↔ matched Boltz2 exact template-only refold TM',
            'values':values,'colors':fills,
            'groups':['Unscored experimental control'if v is None else 'AIS ↔ refold TM: '+format(v,'.2f')for v in values],
            'display_min':low,'display_max':high,'display_colormap':'Plasma',
            'display_normalization':'Observed full-cohort AIS min–max; PDB controls excluded; constant values use midpoint color',
            'display_gradient':'linear-gradient(90deg,'+','.join(colors.to_hex(palette(i/10))for i in range(11))+')',
            'quantity':'coordinate_similarity_not_confidence','metric_definition':METRIC_DEFINITION}


def apply_metric(parent_html, measured, expected_pairs):
    """Return patched text+receipt, without writing it. Approved execution only."""
    assert digest(parent_html.encode())==PARENT_SHA256
    assert expected_pairs['status']=='PASS'and measured['status']=='PASS'
    assert expected_pairs['parent_html_sha256']==PARENT_SHA256
    assert measured['metric_definition']==METRIC_DEFINITION
    assert set(measured['targets'])==set(expected_pairs['targets'])==set(TARGETS)
    protected=protected_fragments(parent_html)
    before=script_json(parent_html,'poster-data')
    data=copy.deepcopy(before)
    counts={}
    for view,count in TARGETS.items():
        target=data['targets'][view]
        ids={model for model in target['models']if not model.startswith('PDB_REF')}
        assert len(ids)==11000 and len(target['models'])==11002
        rows=measured['targets'][view];pairs=expected_pairs['targets'][view]
        assert rows['ca_count']==pairs['ca_count']==count
        indexed=_indexed_rows(rows,ids);expected=_indexed_rows(pairs,ids)
        assert METRIC not in target['color_schemes']
        target['color_schemes'][METRIC]=_scheme(target['models'],indexed,expected)
        target['color_schemes'][METRIC]['full_CA_count']=count
        counts[view]={'predictions':11000,'unscored_controls':2,'full_CA_count':count,
                      'min':target['color_schemes'][METRIC]['display_min'],
                      'max':target['color_schemes'][METRIC]['display_max']}
    # Undo only new metric dictionaries: every prior scientific/movie datum exact.
    restored=copy.deepcopy(data)
    for target in restored['targets'].values():target['color_schemes'].pop(METRIC)
    assert restored==before
    text=patch_UI_source(parent_html)
    encoded=json.dumps(data,ensure_ascii=False,separators=(',',':'),allow_nan=False).replace('</','<\\/')
    pattern=r'(<script[^>]*id="poster-data"[^>]*>)(.*?)(</script>)'
    text,n=re.subn(pattern,lambda m:m[1]+encoded+m[3],text,flags=re.S)
    assert n==1
    assert protected_fragments(text)==protected
    receipt={'status':'DRAFT_ADAPTER_RESULT_NOT_EXPORTED','parent_sha256':PARENT_SHA256,
             'metric':METRIC,'targets':counts,'old_payload_exact_when_new_schemes_removed':True,
             'refold_pTM_default_unchanged':True,'new_metric_is_numeric_not_categorical':True,
             'new_metric_current_frame_readout_only_while_selected':True,
             'no_projection_cluster_movie_tree_or_coordinate_recalculation':True}
    return text,receipt


def inspect_source_only(parent_path):
    """Dry-check UI splice sites in memory; never loads measured scientific data."""
    parent=Path(parent_path).read_text()
    assert digest(parent.encode())==PARENT_SHA256
    protected=protected_fragments(parent)
    patched=patch_UI_source(parent)
    assert protected_fragments(patched)==protected
    # No color-data or science dictionaries are changed by this UI-only inspection.
    assert script_json(parent,'poster-data')==script_json(patched,'poster-data')
    for ident in ['Adk-refold-structure-data','Mad2-refold-structure-data','tree-display-data']:
        pattern=r'<script[^>]*id="'+ident+r'"[^>]*>(.*?)</script>'
        assert re.search(pattern,parent,re.S)[1]==re.search(pattern,patched,re.S)[1]
    return {'status':'SOURCE_ONLY_SPLICE_INSPECTION_PASS','parent_sha256':PARENT_SHA256,
            'added_buttons':patched.count('data-color-mode="ais_refold_tm"'),
            'metric_captions':patched.count('class="ais-refold-tm-caption"'),
            'existing_data_and_movie_scripts_unchanged':True,
            'measured_scores_loaded':False,'scientific_scores_computed':False,
            'browser_or_fixture_executed':False,'HTML_or_ZIP_export_written':False}


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description='Source-only splice inspection; no exports or score loading.')
    parser.add_argument('--inspect-parent',required=True,type=Path)
    args=parser.parse_args()
    print(json.dumps(inspect_source_only(args.inspect_parent),indent=2))
