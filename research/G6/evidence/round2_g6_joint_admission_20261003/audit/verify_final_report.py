"""Independently check published main table numbers against raw results."""
from pathlib import Path
import json,hashlib,re
import numpy as np
OUT=Path(__file__).resolve().parent;ROOT=OUT.parent
report=ROOT/'reports/G6_FULL_REPORT_ZH.md';text=report.read_text()
rows={line.split('|')[1].strip():[x.strip() for x in line.split('|')[2:-1]]
      for line in text.splitlines() if line.startswith('| ')}
checks=[]
def eq(a,b,tol):
    assert abs(float(a)-float(b))<=tol,(a,b,tol)
for label,path in [('旧Kundur：零基值探针','transfer/kundur_summary.json'),
                   ('旧WECC：零基值探针','transfer/wecc_summary.json'),
                   ('新Kundur：每PCC正50MW','positive_workpoint/positive_summary.json')]:
    data=json.loads((ROOT/path).read_text())['equal_split']
    for token,contract in zip(rows[label],['committed','fixed_optional','dynamic_optional','independent_ports']):
        match=re.fullmatch(r'κ=([\d.]+)–([\d.]+); a1=a2=([\d.]+)–([\d.]+)',token)
        assert match,token
        lo,hi,alo,ahi=map(float,match.groups())
        true_lo=data[contract+'_capacity_lower_MW'];true_hi=data[contract+'_capacity_upper_MW']
        assert lo<=true_lo<=lo+.00010001 and hi-.00010001<=true_hi<=hi
        assert alo<=true_lo/2<=alo+.00010001 and ahi-.00010001<=true_hi/2<=ahi
    checks.append(label)
positive_labels=['committed_inner','committed_outer','dynamic_optional_inner','dynamic_optional_outer',
                 'independent_ports_inner','independent_ports_outer','reset_false_admission']
for label in positive_labels:
    dt=256 if label in ['dynamic_optional_inner','dynamic_optional_outer','reset_false_admission'] else 128
    path=ROOT/f'positive_workpoint/{label}_dt{dt}'
    meta=json.loads(path.with_suffix('.json').read_text());raw=np.load(path.with_suffix('.npz'))
    tokens=rows[label];peak=float(abs(raw['frequency_Hz']).max())
    eq(tokens[0],meta['case']['total_amplitude_MW'],.00005001)
    for val in tokens[1].strip('()').split(','):eq(val,meta['case']['total_amplitude_MW']/2,.00005001)
    eq(tokens[2],abs(raw['exact_LTI_frequency_Hz']).max(),.0000005001)
    eq(tokens[3],peak,.0000005001)
    assert tokens[4]==('采样未越限' if peak<=.05 else '采样越限')
    eq(tokens[5],raw['bus_voltage_pu'].min(),.000005001)
    eq(tokens[6],raw['total_compute_MW'].min(),.00005001)
    checks.append(label)
for network in ['kundur','wecc']:
    for label in ['committed_inner','committed_outer','dynamic_optional_inner','dynamic_optional_outer','reset_inner_error']:
        path=ROOT/f'nonlinear/{network}_{label}_dt128';raw=np.load(path.with_suffix('.npz'));meta=json.loads(path.with_suffix('.json').read_text())
        coarse=np.load(ROOT/f'nonlinear/{network}_{label}_dt64.npz')
        tokens=rows[network+' '+label];peak=float(abs(raw['frequency_Hz']).max())
        eq(tokens[0],meta['case']['total_amplitude_MW'],.00005001)
        for val,expected in zip(tokens[1].strip('()').split(','),meta['case']['allocation_MW']):eq(val,expected,.00005001)
        eq(tokens[2],peak,.0000005001);eq(tokens[3],abs(raw['exact_LTI_frequency_Hz']).max(),.0000005001)
        difference=abs(peak-float(abs(coarse['frequency_Hz']).max()))
        assert abs(float(tokens[4])-difference)<=.051*difference+1e-15
        if label.endswith('inner'):assert tokens[5]==('未转移' if peak>.05 else '该轨迹转移')
        lo,hi=tokens[6].split('/');eq(lo,raw['bus_voltage_pu'].min(),.000005001);eq(hi,raw['bus_voltage_pu'].max(),.000005001)
        checks.append(network+' '+label)
assert '.945044/.948743' in text and '0.053099550' in text
assert '不是新增平均算力容量' in text and '不是全指标接入许可' in text
assert '0<ℓ<u<∞' in text and '到最近整数的距离' in text and '每个符号到每个符号' in text
out={'main_report':str(report.relative_to(ROOT)),'main_report_sha256':hashlib.sha256(report.read_bytes()).hexdigest(),
     'table_rows_checked':len(checks),'checked_rows':checks,'all_numeric_table_checks_passed':True,
     'displayed_LTI_brackets_rounded_outward_from_numerical_endpoints':True,
     'total_and_per_port_amplitude_columns_checked':True,
     'scope':'Numeric tables checked against raw NPZ trajectories and audited capacity summaries; mathematical hypotheses separately reviewed in INDEPENDENT_PROOF_AUDIT.md'}
(OUT/'FINAL_MAIN_REPORT_CHECK.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(out,indent=2,ensure_ascii=False))
