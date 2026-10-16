"""Six authenticated human-transcript input regulators composed with Ripple SuperNeuron.

Five added loci families each contribute measurable numerical dynamics. These are
engineered mappings informed by real gene identities, NOT implementations of
human phototransduction proteins, RNA chemistry or retinal spectral physics.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import statistics
import time
from superneuron import (LOCUS_COUNT, REFSEQ, SuperNeuron, locus_template,
                         parse_fasta, rgb_features, synthetic_stimulus, run_trial)

# SHA-256 of transcript after T -> U, fetched via NCBI E-utilities in Actions 2026-10-16.
EXPECTED_NCBI_RNA_SHA256 = {
    'OPN1LW':'dc2175733c89647f5aa29cfc589c98a2e71ac4c631e125d4675ca34c0d77e1f2',
    'OPN1MW':'1c4859bb5dc07d2e7ef5d5bf7aa59280b8cc69910ba7cefddeca90bc5d2a9320',
    'OPN1SW':'d27a8e88ab20c73b71690f2b4b30ec77d616a54e10b0a1e52b441330e07f8fcc',
    'GNAT2':'2a626ca8ea140bee5c520e21b70c5baf5b8ff65a33a94a1ff4aaf4130fca0c57',
    'RPE65':'f127c408c1c6a8f9fe9b972716b60c53545fe92dc5033f2451e1f0036e14c3e0',
}
GENES=tuple(EXPECTED_NCBI_RNA_SHA256)


def load_genes(directory:Path)->dict[str,str]:
    """Load only exact NCBI-versioned, SHA-pinned mRNA sequences; no fallback."""
    result={}
    for gene in GENES:
        accession=REFSEQ[gene]['accession']
        path=directory/f'{gene}_{accession}.fasta'
        seq=parse_fasta(path.read_text(encoding='utf-8'),accession)['rna']
        actual=hashlib.sha256(seq.encode()).hexdigest()
        if actual!=EXPECTED_NCBI_RNA_SHA256[gene]:
            raise ValueError(f'{gene} RNA checksum mismatch: {actual}')
        result[gene]=seq
    return result


class MultiGeneSuperNeuron:
    """Real sequence-coded digital filters with causal coupling into one inherited controller.

    All 5 added gene families change a model state/output. Knockout operates at
    family OR single-locus level. RHO's own 29 loci remain in the base engine.
    """
    def __init__(self, rho:str, genes:dict[str,str], knockout_gene:str|None=None,
                 knockout_locus:tuple[str,int]|None=None):
        if set(genes)!=set(GENES):raise ValueError('All five pinned input gene families required')
        if knockout_gene is not None and knockout_gene not in GENES:
            raise ValueError('Unknown gene knockout')
        if knockout_locus is not None and (knockout_locus[0] not in GENES or not 0<=knockout_locus[1]<LOCUS_COUNT):
            raise ValueError('Unknown individual locus')
        self.base=SuperNeuron(rho)
        self.genes=genes
        self.gene_alleles={g:locus_template(seq) for g,seq in genes.items()}
        self.filters={g:[0.0]*LOCUS_COUNT for g in GENES}
        self.knockout_gene=knockout_gene;self.knockout_locus=knockout_locus
        self.last_values={g:0.0 for g in GENES}

    def step(self,rgb:tuple[float,float,float])->dict:
        f=rgb_features(rgb);dt=self.base.dt
        cone_base={'OPN1LW':f['L'],'OPN1MW':f['M'],'OPN1SW':f['S']}
        cone_current=sum(cone_base.values())/3
        target={**cone_base,'GNAT2':cone_current,'RPE65':1.-self.base.energy}
        # Every live locus actually receives an input, maintains state, and
        # contributes to the conductance or energy controller.
        for gene in GENES:
            if gene==self.knockout_gene:
                self.last_values[gene]=0.
                continue
            num=den=0.
            for i,allele in enumerate(self.gene_alleles[gene]):
                if self.knockout_locus==(gene,i):continue
                tau=(.08,.16,.34,.68)[allele]*(1+.012*i)
                state=self.filters[gene][i]
                state+=(1-math.exp(-dt/tau))*(target[gene]-state)
                self.filters[gene][i]=state
                weight=(.7,.9,1.15,1.4)[allele]
                num+=weight*state; den+=weight
            # Holding common 29-site normalization makes locus removals causal.
            self.last_values[gene]=num/max(LOCUS_COUNT,1)
        cone_drive=.82*sum(self.last_values[g] for g in ('OPN1LW','OPN1MW','OPN1SW'))
        transduction=1+.9*self.last_values['GNAT2']
        # Synthetic digital ionic conductance pulse: real base.g_e is modified
        # before the archived numerical engine's conductance/membrane update.
        self.base.g_e+=dt*4.2*cone_drive*transduction
        out=self.base.step(rgb)
        # RPE65-inspired recovery modifier: causal model energy update only.
        self.base.energy=min(1.,self.base.energy+dt*.17*self.last_values['RPE65'])
        return {**out,'energy':self.base.energy,'gene_values':dict(self.last_values),
                'gene_count':6,'active_loci':174-(0 if self.knockout_gene is None else 29)
                                 -(0 if self.knockout_locus is None else 1),
                'gene_source':'NCBI-mRNA-derived software control'}


def evaluate(rho:str,genes:dict[str,str],nsteps:int=500)->dict:
    def run(ko_gene=None,ko_locus=None,frames=None):
        n=MultiGeneSuperNeuron(rho,genes,knockout_gene=ko_gene,knockout_locus=ko_locus)
        samples=frames if frames is not None else synthetic_stimulus(nsteps)
        traces=[n.step(rgb) for rgb in samples]
        return {'events':n.base.spikes,'mean_voltage':statistics.mean(x['u'] for x in traces),
                'min_energy':min(x['energy'] for x in traces),'trace':traces}
    start=time.perf_counter()
    base=run();x=base['trace'];baseline_u=[v['u'] for v in x]
    ablations={}
    for gene in GENES:
        c=run(ko_gene=gene)
        # RPE65 is a resource pathway; other genes affect membrane potential.
        changed=max(abs(a['u']-b['u'])+abs(a['energy']-b['energy']) for a,b in zip(x,c['trace']))
        ablations[gene]={'events':c['events'],'max_abs_state_difference':changed}
    loci={}
    for gene in GENES:
        changes=[]
        for i in range(LOCUS_COUNT):
            c=run(ko_locus=(gene,i))
            changes.append(max(abs(a['u']-b['u'])+abs(a['energy']-b['energy']) for a,b in zip(x,c['trace'])))
        loci[gene]={'total':len(changes),'min_effect':min(changes),'max_effect':max(changes),
                    'all_nonzero':all(v>1e-15 for v in changes)}
    # Strong sustained input tests energy recovery, absent in brief pulse trace.
    bright=[(1.,1.,1.)]*900
    energy_reference=run(frames=bright)
    energy_without_recovery=run(ko_gene='RPE65',frames=bright)
    rho_only=run_trial(rho,synthetic_stimulus(nsteps))
    return {'classification':'EXECUTED_SOFTWARE_ON_SYNTHETIC_RGB',
            'real_human_genes_count':6,'gene_loci_executed':174,
            'actual_evaluations':1+len(GENES)+len(GENES)*LOCUS_COUNT+2+1,
            'original_multigene_events':base['events'],'rho_only_events':rho_only['events'],
            'gene_family_ablation':ablations,'individual_locus_ablation':loci,
            'all_added_loci_causal':all(x['all_nonzero'] for x in loci.values()),
            'energy_sustained':{'full_min':energy_reference['min_energy'],
                                'without_RPE65_min':energy_without_recovery['min_energy'],
                                'difference':energy_reference['min_energy']-energy_without_recovery['min_energy']},
            'no_physical_phototransduction_or_cognition_validated':True,
            'wall_seconds':time.perf_counter()-start}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rho',default='data/RHO_NM_000539.3_mirror.fasta')
    p.add_argument('--genes',default='data/ncbi_genes')
    p.add_argument('--output',default='results/multigene_benchmark.json')
    a=p.parse_args()
    rho=parse_fasta(Path(a.rho).read_text(),'NM_000539.3')['rna']
    genes=load_genes(Path(a.genes))
    r=evaluate(rho,genes)
    Path(a.output).parent.mkdir(parents=True,exist_ok=True)
    Path(a.output).write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(r,indent=2))
if __name__=='__main__':main()
