"""RNA-sequence-driven, energy-constrained conductance neuron research engine.

This is computational engineering: authentic imported RNA nucleotides alter real
filter coefficients, synaptic drive and firing; DNA motifs do NOT automatically
encode known biological protein behavior. All RGB signals are *digital pixel*
values; spectral physics requires separately calibrated optical measurements.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
from vendor.charlie_v2.neuron import CharlieNeuron
import random
import re
import statistics
import time
import urllib.parse
import urllib.request

LOCUS_COUNT = 29
SEARCH_SPACE = 4 ** LOCUS_COUNT
BASES = "ACGU"
REFSEQ = {
    "RHO": {"accession": "NM_000539.3", "role": "rod-like luminance and contrast path", "ncbi_gene":6010},
    "OPN1LW": {"accession":"NM_020061.6", "role":"long-cone-inspired RGB projection", "ncbi_gene":5956},
    "OPN1MW": {"accession":"NM_000513.2", "role":"medium-cone-inspired RGB projection", "ncbi_gene":2652},
    "OPN1SW": {"accession":"NM_001385125.1", "role":"short-cone-inspired RGB projection", "ncbi_gene":611},
    "GNAT2": {"accession":None, "role":"candidate cone-signal transduction analogue", "ncbi_gene":2780},
    "RPE65": {"accession":None, "role":"candidate recovery/visual-cycle analogue", "ncbi_gene":6121},
}


def parse_fasta(text: str, expected_accession: str | None = None) -> dict:
    lines = text.splitlines()
    if not lines or not lines[0].startswith(">"):
        raise ValueError("FASTA header is required")
    header = lines[0][1:].strip()
    if expected_accession and expected_accession not in header:
        raise ValueError(f"FASTA header lacks expected accession {expected_accession}")
    sequence = "".join(x.strip().upper() for x in lines[1:]).replace("T", "U")
    if len(sequence) < LOCUS_COUNT * 3 or set(sequence) - set(BASES):
        raise ValueError("RNA must have at least 87 unambiguous A/C/G/U bases")
    return {"header":header, "rna":sequence, "bases":len(sequence),
            "sha256":hashlib.sha256(sequence.encode()).hexdigest()}


def fetch_ncbi_fasta(accession: str, out: Path) -> dict:
    """Explicit network fetch. Requires real NCBI access; no synthetic fallback."""
    if not re.fullmatch(r"NM_\d+\.\d+", accession):
        raise ValueError("Accession must be a versioned RefSeq mRNA (NM_...)")
    q = urllib.parse.urlencode({"db":"nuccore", "id":accession, "rettype":"fasta", "retmode":"text"})
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?" + q
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent":"Ripple-SuperNeuron/0.1 research"}), timeout=25) as r:
        raw = r.read(2_000_001)
    if len(raw) >= 2_000_001:
        raise ValueError("RefSeq response unexpectedly large")
    parsed = parse_fasta(raw.decode("utf-8"), accession)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_bytes(raw)
    return {"url":url,"path":str(out),**{k:v for k,v in parsed.items() if k!="rna"}}


def locus_template(rna: str) -> tuple[int,...]:
    """29 non-overlapping transcript positions; engineered controller, not RNA translation."""
    if len(rna) < LOCUS_COUNT * 3 or set(rna) - set(BASES):
        raise ValueError("Invalid RNA")
    # Even sampling across entire transcript, rather than using just the start.
    positions = [min(len(rna)-1, ((2*i+1)*len(rna)) // (2*LOCUS_COUNT)) for i in range(LOCUS_COUNT)]
    return tuple(BASES.index(rna[p]) for p in positions)


def encode_base4(states: tuple[int,...]) -> int:
    if len(states)!=LOCUS_COUNT or any(x not in (0,1,2,3) for x in states):
        raise ValueError("29 base-four states required")
    n=0
    for x in states:n=4*n+x
    return n


def decode_base4(n: int) -> tuple[int,...]:
    if not 0 <= n < SEARCH_SPACE:raise ValueError("Genome index outside 4^29 search space")
    states=[0]*LOCUS_COUNT
    for i in range(LOCUS_COUNT-1,-1,-1):
        states[i]=n%4;n//=4
    return tuple(states)


def linear_srgb(v:float)->float:
    v=min(1.0,max(0.0,float(v)))
    return v/12.92 if v<=0.04045 else ((v+0.055)/1.055)**2.4


def rgb_features(rgb: tuple[float,float,float])->dict:
    if len(rgb)!=3 or any(not math.isfinite(v) or v<0 or v>1 for v in rgb):
        raise ValueError("RGB requires 3 finite sRGB values within [0,1]")
    r,g,b=(linear_srgb(v) for v in rgb)
    # Digital engineering projections. NOT calibrated human spectral cone responses.
    return {"L":.76*r+.24*g, "M":.18*r+.72*g+.10*b,
            "S":.04*g+.96*b, "Y":.2126*r+.7152*g+.0722*b}


class SuperNeuron:
    """29 RNA-coded kinetic regulators + conductance membrane + energy accounting.

    Each regulator receives a real input and changes the membrane and state.
    Knockout disables the named regulator with unchanged other parameters.
    """
    def __init__(self, rna:str, genotype:tuple[int,...]|None=None, knockout:int|None=None,
                 mode:str="super", dt:float=.05):
        if dt<=0 or dt>.1:raise ValueError("dt must be (0,0.1]")
        if mode not in ("super","conductance","lif"):
            raise ValueError("unknown mode")
        self.dt=dt;self.mode=mode;self.rna=rna
        self.genotype=genotype if genotype is not None else locus_template(rna)
        if len(self.genotype)!=LOCUS_COUNT or any(v not in range(4) for v in self.genotype):
            raise ValueError("wrong genotype")
        if knockout is not None and not 0<=knockout<LOCUS_COUNT:raise ValueError("wrong knockout")
        self.knockout=knockout
        self.regulators=[0.0]*LOCUS_COUNT
        self.u=0.;self.g_e=0.;self.g_i=0.;self.adaptation=0.;self.energy=1.
        self.baseline=0.;self.refractory=0.;self.spikes=0;self.t=0.;self.last_signal=0.

    def step(self, rgb:tuple[float,float,float])->dict:
        f=rgb_features(rgb);dt=self.dt; self.t+=dt
        signal=.50*f["Y"]+.22*f["L"]+.20*f["M"]+.08*f["S"]
        self.baseline += (1-math.exp(-dt/1.6))*(signal-self.baseline)
        contrast=signal-self.baseline
        if self.mode=="super":
            # All 29 genome positions regulate real filter kinetics and coupling.
            # Every term is nonnegative and carries causal influence (ablation-tested).
            pathway=0.;weights=0.
            for i,b in enumerate(self.genotype):
                if i==self.knockout:continue
                tau=(.09,.18,.4,.85)[b]*(1+.016*i)
                alpha=1-math.exp(-dt/tau)
                self.regulators[i]+=alpha*(contrast-self.regulators[i])
                gain=(.65,.85,1.15,1.45)[b]
                pathway+=gain*self.regulators[i]
                weights+=gain
            self.last_signal=pathway/max(weights,1e-12)
            stimulus=max(0.,2.2*signal+10.0*self.last_signal)
            inhib=max(0.,-1.8*self.last_signal)
        else:
            self.last_signal=0.
            stimulus=max(0.,2.2*signal)
            inhib=0.
        if self.mode=="lif":
            self.u += (1-math.exp(-dt/.5))*(stimulus-self.u)
        else:
            # Two synaptic conductances (Charlie-like), voltage-dependent current.
            self.g_e+=(1-math.exp(-dt/.18))*(stimulus-self.g_e)
            self.g_i+=(1-math.exp(-dt/.32))*(inhib-self.g_i)
            self.adaptation*=math.exp(-dt/.65)
            g=.30+self.g_e+self.g_i
            q=self.g_e-.25*self.g_i-self.adaptation
            self.u=q/g+(self.u-q/g)*math.exp(-g*dt/.37)
        self.refractory=max(0.,self.refractory-dt)
        spike=bool(self.u>=.48 and self.refractory==0 and self.energy>=.10)
        if spike:
            self.u=0.;self.refractory=.1;self.spikes+=1
            if self.mode!="lif":self.adaptation+=.12
        if self.mode=="super":
            # Computed resource constraint: energy depletion can prevent firing.
            self.energy=min(1.,max(0.,self.energy+dt*.13-dt*.013*stimulus-(.09 if spike else 0.)))
        return {"t":round(self.t,5),"spike":spike,"u":self.u,
                "gene_signal":self.last_signal,"energy":self.energy,
                "drive":stimulus,"channels":f}


def synthetic_stimulus(n=400, dt=.05):
    """Deterministic artificial RGB task: not a physical camera recording."""
    arr=[]
    for i in range(n):
        t=i*dt
        envelope=.18 + (.22 if 3<=t<5 or 10<=t<12 or 16<=t<18 else 0.)
        drift=.03*math.sin(t*.38)
        rgb=(min(1.,max(0.,envelope+drift+.03*math.sin(t*3))),
             min(1.,max(0.,envelope*.8+drift)),
             min(1.,max(0.,envelope*.6+.025*math.cos(t*.72))))
        arr.append(rgb)
    return arr


def run_trial(rna:str, seq:list, genotype:tuple[int,...]|None=None,
              knockout:int|None=None,mode="super",dt=.05)->dict:
    neuron=SuperNeuron(rna,genotype,knockout,mode,dt)
    out=[neuron.step(v) for v in seq]
    return {"events":neuron.spikes,"mean_voltage":statistics.mean(x["u"] for x in out),
            "mean_gene_signal":statistics.mean(x["gene_signal"] for x in out),
            "mean_energy":statistics.mean(x["energy"] for x in out),
            "trace":out}


def benchmark(rna:str, samples:int=256, seed:int=101, nsteps:int=400)->dict:
    if samples<1 or samples>100_000:raise ValueError("samples must be [1,100000]")
    seq=synthetic_stimulus(nsteps)
    base=locus_template(rna)
    t0=time.perf_counter()
    default=run_trial(rna,seq,base)
    modes={m:run_trial(rna,seq,base,mode=m) for m in ("lif","conductance")}
    inherited=CharlieNeuron()
    inherited_trace=[inherited.step(rgb, .05) for rgb in seq]
    knock={str(i):run_trial(rna,seq,base,knockout=i) for i in range(LOCUS_COUNT)}
    original={k:default[k] for k in default if k!="trace"}
    control={m:{k:v[k] for k in v if k!="trace"} for m,v in modes.items()}
    control["inherited_charlie_v2"]={"events":inherited.count,
              "mean_voltage":statistics.mean(x["membrane"] for x in inherited_trace),
              "source":"immutable archived Charlie v2 core; own original event/reset model"}
    original_series=[x["gene_signal"] for x in default["trace"]]
    original_voltage=[x["u"] for x in default["trace"]]
    delta={str(i):{
        "max_abs_gene_signal_change":max(abs(a-b) for a,b in zip(original_series,[y["gene_signal"] for y in x["trace"]])),
        "max_abs_membrane_voltage_change":max(abs(a-b) for a,b in zip(original_voltage,[y["u"] for y in x["trace"]])),
        "event_count_difference":x["events"]-default["events"]} for i,x in knock.items()}
    rng=random.Random(seed)
    # Diverse, deterministically sampled genotypes, NOT exhaustive 4^29 runs.
    seen={encode_base4(base)};candidates=[]
    while len(candidates)<samples:
        n=rng.randrange(SEARCH_SPACE)
        if n in seen:continue
        seen.add(n)
        run=run_trial(rna,seq,decode_base4(n))
        candidates.append({"genotype_index":n,"events":run["events"],
                           "mean_gene_signal":run["mean_gene_signal"],"mean_energy":run["mean_energy"]})
    return {"status":"EXECUTED_SYNTHETIC_SOFTWARE", "gene_source_sha256":hashlib.sha256(rna.encode()).hexdigest(),
            "search_space_exact":SEARCH_SPACE,"simulated_candidate_genotypes":len(candidates),
            "real_genotypes_in_demo":1,"population_evaluations":1+len(candidates)+LOCUS_COUNT+len(modes)+1,
            "dt_model_seconds":.05,"nsteps":nsteps,"seed":seed,
            "original":original,"controls":control,
            "regulator_ablation":delta,
            "all_regulators_have_nonzero_numerical_effect":all(x["max_abs_membrane_voltage_change"]>1e-14 for x in delta.values()),
            "candidate_event_counts":sorted({r["events"] for r in candidates}),
            "candidate_event_distribution":{str(e):sum(r["events"]==e for r in candidates) for e in sorted({r["events"] for r in candidates})},
            "best_by_event_count":max(candidates,key=lambda x:x["events"]),
            "wall_seconds":time.perf_counter()-t0,
            "no_biological_fitness_or_intelligence_metric":True}


def main():
    p=argparse.ArgumentParser(description="Ripple SuperNeuron RNA research engine")
    s=p.add_subparsers(dest="command",required=True)
    fetch=s.add_parser("fetch-refseq",help="retrieve authentic NCBI transcript; requires internet")
    fetch.add_argument("symbol", choices=[x for x in REFSEQ if REFSEQ[x]["accession"]]);fetch.add_argument("--out",required=True)
    demo=s.add_parser("benchmark",help="run numerical benchmark on artificial RGB fixtures")
    demo.add_argument("--fasta",required=True);demo.add_argument("--accession",default="NM_000539.3")
    demo.add_argument("--samples",type=int,default=256);demo.add_argument("--output",default="results/benchmark.json")
    args=p.parse_args()
    if args.command=="fetch-refseq":
        result=fetch_ncbi_fasta(REFSEQ[args.symbol]["accession"],Path(args.out))
    else:
        source=Path(args.fasta)
        parsed=parse_fasta(source.read_text(encoding="utf-8"),args.accession)
        result=benchmark(parsed["rna"],samples=args.samples)
        result["fasta_header"]=parsed["header"]
        result["fasta_path"]=str(source)
        result["fasta_sha256"]=hashlib.sha256(source.read_bytes()).hexdigest()
        Path(args.output).parent.mkdir(parents=True,exist_ok=True)
        Path(args.output).write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k not in ("regulator_ablation",)},indent=2))

if __name__=="__main__":main()