"""Retrieve and verify selected human vision-gene reference mRNAs from NCBI.

The accession list is externally grounded in NCBI Gene. Download failures are
recorded explicitly; failed/missing sequences are never replaced by fixtures.
"""
import json
from pathlib import Path
import sys
import time
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from superneuron import REFSEQ, fetch_ncbi_fasta
ROOT=Path(__file__).resolve().parents[1]
RECORD=ROOT/'results'/'ncbi_gene_catalog.json'
GENES=ROOT/'data'/'ncbi_genes'


def collect(names=('OPN1LW','OPN1MW','OPN1SW','GNAT2','RPE65')):
    GENES.mkdir(exist_ok=True,parents=True)
    results={}
    for gene in names:
        if gene not in REFSEQ:raise ValueError('unknown gene')
        acc=REFSEQ[gene]['accession']
        try:
            item=fetch_ncbi_fasta(acc,GENES/f'{gene}_{acc}.fasta')
            results[gene]={"status":"DOWNLOADED_NCBI", "ncbi_gene_id":REFSEQ[gene]['ncbi_gene'],**item}
        except Exception as e:
            results[gene]={"status":"UNAVAILABLE", "accession":acc, "reason":f'{type(e).__name__}: {e}'[:240]}
        time.sleep(.4)
    output={"status":"SOURCE_COLLECTION_ONLY_NOT_BIOLOGICAL_VALIDATION", "genes":results}
    RECORD.parent.mkdir(exist_ok=True,parents=True)
    RECORD.write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps(output,indent=2))
    return int(any(r['status']!='DOWNLOADED_NCBI' for r in results.values()))

if __name__=='__main__':raise SystemExit(collect())
