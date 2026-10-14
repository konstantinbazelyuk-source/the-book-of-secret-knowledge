"""Ripple EvoPareto v1.3: multi-objective simulated policy search.

Scientific scope: commanded kinematic joint trajectories + first-order rate-limited
actuator model. No ground-contact dynamics, torque, camera, or physical measurements.
Approved Ripple, servo and kinematics source is imported without mutation.
"""
from __future__ import annotations
from dataclasses import asdict
import hashlib, json, math, random, statistics
from ripple_evo.evolution import Genome, BASELINE, BOUNDS, scenario, simulate

TARGET_SPEED_MM_S = BASELINE['stride_mm'] / (BASELINE['cycle_s'] * BASELINE['duty'])


def stress_scenarios(count=10, seed=0, split='train'):
    """Independent perturbations of existing first-order actuator parameters only."""
    rng = random.Random(f'{split}:{seed}:v1.3')
    return [{'id':f'{split}-{i}', 'tau_s':round(rng.uniform(.045, .18),6),
             'max_speed_rad_s':round(rng.uniform(1.4,4.0),6)} for i in range(count)]


def describe(genome:Genome, cases:list[dict],duration_s=4.8):
    g=genome.check()
    trials=[simulate(g, s, duration_s=duration_s) for s in cases]
    errors=[t['rms_toe_error_mm'] for t in trials]
    speeds=[t['command_distance_proxy_mm']/t['duration_s'] for t in trials]
    clips=[t['rate_limit_hits'] for t in trials]
    support=[t['support_proxy_loss_frames'] for t in trials]
    violations=sum(t['ik_failures'] for t in trials)
    stress_passes=sum(t['ik_failures']==0 and t['support_proxy_loss_frames']<=5 and
       t['rms_toe_error_mm']<=8 and (t['command_distance_proxy_mm']/t['duration_s'])>=.75*TARGET_SPEED_MM_S for t in trials)
    p90=sorted(errors)[math.ceil(.9*len(errors))-1]
    # Four conflicting proxy objectives: toe error, speed, clipping, and commanded support failure.
    # These are not force/contact physics and must not be labeled safety clearance.
    obj=(statistics.mean(errors), -statistics.mean(speeds), statistics.mean(clips),sum(support)/len(cases))
    return {'mean_toe_error_mm':round(obj[0],6),'p90_toe_error_mm':round(p90,6),
            'mean_commanded_speed_mm_s':round(-obj[1],6),
            'mean_rate_limit_hits':round(obj[2],6),
            'mean_support_proxy_loss_frames':round(obj[3],6),
            'total_support_proxy_loss_frames':sum(support),
            'total_ik_failures':violations,'n_scenarios':len(cases),
            'objectives_minimize':tuple(round(v,6) for v in obj),
            'proxy_stress_cases_passed':stress_passes,
            'proxy_stress_cases_pct':round(100*stress_passes/len(cases),3),
            'zero_ground_truth':True}


def feasible(m:dict, speed_floor=0.75*TARGET_SPEED_MM_S):
    return (m['total_ik_failures']==0 and m['mean_commanded_speed_mm_s']>=speed_floor
            and m['total_support_proxy_loss_frames'] <= 5*m['n_scenarios'])


def dominates(a:dict,b:dict):
    fa,fb=feasible(a),feasible(b)
    if fa!=fb:return fa
    av=a['objectives_minimize']; bv=b['objectives_minimize']
    return all(x<=y+1e-10 for x,y in zip(av,bv)) and any(x<y-1e-10 for x,y in zip(av,bv))


def nondominated_fronts(keys:list[str], metrics:dict):
    # Deterministic, no external NSGA-II implementation; O(M*N^2) dominance ranking.
    dominated={k:[] for k in keys};counts={k:0 for k in keys}
    for i,a in enumerate(keys):
        for b in keys[i+1:]:
            if dominates(metrics[a],metrics[b]): dominated[a].append(b);counts[b]+=1
            elif dominates(metrics[b],metrics[a]):dominated[b].append(a);counts[a]+=1
    result=[];front=sorted(k for k in keys if counts[k]==0)
    while front:
        result.append(front)
        next_front=[]
        for a in front:
            for b in dominated[a]:
                counts[b]-=1
                if counts[b]==0:next_front.append(b)
        front=sorted(next_front)
    return result


def crowding(front:list[str],metrics:dict):
    d={k:0. for k in front}
    if len(front)<3:return {k:float('inf') for k in front}
    for i in range(4):
        order=sorted(front,key=lambda k:(metrics[k]['objectives_minimize'][i],k))
        d[order[0]]=d[order[-1]]=float('inf')
        lo=metrics[order[0]]['objectives_minimize'][i];hi=metrics[order[-1]]['objectives_minimize'][i]
        if hi<=lo:continue
        for ix in range(1,len(order)-1):
            if math.isfinite(d[order[ix]]):
                d[order[ix]]+=(metrics[order[ix+1]]['objectives_minimize'][i]-metrics[order[ix-1]]['objectives_minimize'][i])/(hi-lo)
    return d


def select(keys, metrics, n):
    ans=[]
    for front in nondominated_fronts(keys,metrics):
        cd=crowding(front,metrics)
        selected=sorted(front,key=lambda k:(-cd[k],k))
        ans.extend(selected[:max(0,n-len(ans))])
        if len(ans)>=n:break
    return ans


def mutate(g,rng):
    a=asdict(g)
    for k,(lo,hi) in BOUNDS.items():
        if rng.random()<.65:
            a[k]=round(max(lo,min(hi,a[k]+rng.gauss(0,.14*(hi-lo)))),5)
    return Genome(**a).check()


def cross(a,b,rng):
    return Genome(**{k:getattr(a,k) if rng.random()<.5 else getattr(b,k) for k in BOUNDS}).check()


def evolve_pareto(seed=20261013,population=12,generations=4,train_n=6,holdout_n=16):
    if population<4 or generations<1:raise ValueError('population/generations')
    rng=random.Random(seed)
    train=stress_scenarios(train_n,seed=112358,split='train')
    holdout=stress_scenarios(holdout_n,seed=223344,split='holdout')
    base=Genome()
    prev_best=Genome(stride_mm=37.41584,swing_height_mm=17.241,cycle_s=1.81971,duty=.60,gain=0)
    population_list=[base,prev_best]
    while len(population_list)<population:population_list.append(mutate(rng.choice(population_list),rng))
    candidates={};train_metrics={};hist=[]
    def register(g):
        k=g.id()
        if k not in candidates:
            candidates[k]=g
            train_metrics[k]=describe(g,train)
        return k
    keys=list(dict.fromkeys(register(g) for g in population_list))
    for gen in range(generations):
        selected=select(keys,train_metrics,min(population,len(keys)))
        hist.append({'generation':gen,'archive_size':len(nondominated_fronts(selected,train_metrics)[0]),'evaluated_distinct':len(candidates)})
        children=[candidates[k] for k in selected]
        while len(children)<2*population:
            pa=candidates[rng.choice(selected)];pb=candidates[rng.choice(selected)]
            children.append(mutate(cross(pa,pb,rng),rng))
        keys=list(dict.fromkeys(register(g) for g in children))
    keys=select(keys,train_metrics,min(population,len(keys)))
    front=[k for k in nondominated_fronts(keys,train_metrics)[0] if feasible(train_metrics[k])]
    if not front:
        front=[register(base)]
    # Selection uses TRAIN ONLY; holdout is never used for model selection.
    # Precision vs speed: two reproducible knee points of the training Pareto frontier.
    precision=min(front,key=lambda k:(train_metrics[k]['mean_toe_error_mm'], -train_metrics[k]['mean_commanded_speed_mm_s'],k))
    throughput=max(front,key=lambda k:(train_metrics[k]['mean_commanded_speed_mm_s'],-train_metrics[k]['mean_toe_error_mm'],k))
    chosen={'precision':precision,'throughput':throughput,'baseline':register(base),'previous_v1_2':register(prev_best)}
    results={}
    for label,key in chosen.items():
        train_result=train_metrics[key]
        # The holdout environment is independent, and run once after search.
        hold=describe(candidates[key],holdout)
        results[label]={'genome':asdict(candidates[key]),'train':train_result,'holdout':hold,'feasible_holdout':feasible(hold)}
    for label,policy in results.items():
        policy['release_gate'] = ('PASS_SIMULATION_PROXY_GATE' if policy['feasible_holdout'] else 'REJECTED_HOLDOUT_PROXY_GATE')
        policy['hardware_deployment_authorized'] = False
    return {'schema':'ripple-evo-pareto/1','seed':seed,'training_scenarios':train,'holdout_scenarios':holdout,
            'generations':hist,'searched_candidates':len(candidates),'nondominated_train':len(front),
            'policies':results,'selection_note':'selected on train only; separate fixed holdout',
            'evidence':'numerical_first_order_motor_simulation_no_contact_physics_no_hardware'}


def manifest(root):
    from pathlib import Path
    root=Path(root); result={}
    for f in sorted(root.rglob('*')):
        if f.is_file() and not any(part in ('__pycache__','.git') for part in f.parts) and f.name!='MANIFEST.sha256':
            result[str(f.relative_to(root))]=hashlib.sha256(f.read_bytes()).hexdigest()
    return result

if __name__=='__main__':
    import argparse
    from pathlib import Path
    p=argparse.ArgumentParser();p.add_argument('--out',default='results/pareto.json');p.add_argument('--seed',type=int,default=20261013)
    p.add_argument('--population',type=int,default=12);p.add_argument('--generations',type=int,default=4)
    a=p.parse_args();result=evolve_pareto(a.seed,a.population,a.generations)
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'output':str(out),'searched_candidates':result['searched_candidates'],
                      'holdout':{k:v['holdout'] for k,v in result['policies'].items()}},indent=2))