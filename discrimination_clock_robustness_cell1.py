#!/usr/bin/env python3
"""Post-hoc robustness controls for the cell1 discrimination-clock gate."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr
import space_time_observability_cell1 as sto
import discrimination_clock_cell1 as dc

READOUTS = {
    "R0_soma": [0],
    "R6_all": [0,1,2,3,4,5],
    "J1_drop_r1": [0,2,3,4,5],
    "J2_drop_r2_same_branch": [0,1,3,4,5],
    "J3_drop_r3": [0,1,2,4,5],
    "J4_drop_r4": [0,1,2,3,5],
    "J5_drop_r5": [0,1,2,3,4],
}

def q5(x):
    x=np.asarray(x,float)
    q=np.quantile(x,[0,.1,.5,.9,1])
    return {k:float(v) for k,v in zip(['min','q10','median','q90','max'],q)}

def summarize(result, exclude_source6=False):
    clock=result['clock_pairs']; spec={(r['i'],r['j']):r for r in result['spectral_pair_rows']}
    if exclude_source6:
        clock=[r for r in clock if r['i'] != 6 and r['j'] != 6]
    t=np.array([r['t90_ms'] for r in clock])
    ph=np.array([spec[(r['i'],r['j'])]['phase_fraction'] for r in clock])
    path=np.array([r['max_path_um'] for r in clock])
    def rho(a,b):
        z=spearmanr(a,b).statistic
        return float(z) if np.isfinite(z) else None
    final=result['contrast_spectrum_by_horizon'][-1]
    return {
        'n_pairs':len(clock),
        't90_ms':q5(t),
        'phase_fraction':q5(ph),
        'rho_t90_vs_max_path':rho(t,path),
        'rho_t90_vs_phase_fraction':rho(t,ph),
        'final_contrast_top_eigenvalue_mV2_ms':float(final['eigenvalues_mV2_ms'][0]),
        'final_contrast_participation_rank':float(final['participation_rank']),
        'guards':result['guards'],
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--fci-root',type=Path,required=True)
    p.add_argument('--sources-per-tree',type=int,default=8)
    p.add_argument('--amp-na',type=float,default=.02)
    p.add_argument('--delay-ms',type=float,default=20.)
    p.add_argument('--dur-ms',type=float,default=.5)
    p.add_argument('--tstop-ms',type=float,default=140.05)
    p.add_argument('--v-init-mv',type=float,default=-70.)
    p.add_argument('--dt-ms',type=float,default=.05)
    p.add_argument('--output',type=Path,default=Path('discrimination_clock_robustness_cell1_result.json'))
    a=p.parse_args()
    A,t,src,rec=sto.simulate_tensor(a)
    results={}
    for name,inds in READOUTS.items():
        r=dc.analyze_readout(A,t,inds,a.dt_ms,src)
        results[name]=summarize(r,False)
        if name in {'R6_all','J2_drop_r2_same_branch'}:
            results[name+'_exclude_source6_pairs']=summarize(r,True)
    out={
        'model_commit':'ido4848/FCI@55826436751c03a32dfd39e91a48894869e1db57',
        'readouts':READOUTS,
        'source6':src[6],
        'receiver2':rec[2],
        'results':results,
    }
    a.output.write_text(json.dumps(out,indent=2),encoding='utf-8')
    compact={k:{'t90':v['t90_ms'],'phase':v['phase_fraction'],'rho_path':v['rho_t90_vs_max_path'],'top_eig':v['final_contrast_top_eigenvalue_mV2_ms'],'prank':v['final_contrast_participation_rank']} for k,v in results.items()}
    print('ROBUST_CLOCK_RESULT',json.dumps(compact,separators=(',',':')))
    print('wrote',a.output)
if __name__=='__main__': main()
