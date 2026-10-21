"""Independent NCBI RefSeq mRNA authentication of the bundled RHO mirror.

Exit nonzero on an unavailable source OR a mismatch; prints JSON with outcome.
A failing network probe is not evidence of sequence mismatch.
"""
import json
from pathlib import Path
import sys
import urllib.error
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from superneuron import fetch_ncbi_fasta, parse_fasta

ACC = 'NM_000539.3'
REFERENCE = Path(__file__).resolve().with_name('RHO_NM_000539.3_mirror.fasta')
OUTPUT = Path(__file__).resolve().parents[1]/'results'/'ncbi_provenance.json'


def check(download=fetch_ncbi_fasta):
    original = parse_fasta(REFERENCE.read_text(), ACC)
    report = {'accession':ACC,'mirror_rna_sha256':original['sha256'],
              'result':'UNVERIFIED', 'source':'NCBI E-utilities RefSeq transcript'}
    try:
        tempfile = OUTPUT.with_name('ncbi_refseq_verification_temp.fasta')
        receipt = download(ACC, tempfile)
        confirmed = parse_fasta(tempfile.read_text(),ACC)
        tempfile.unlink(missing_ok=True)
        report['ncbi_rna_sha256'] = confirmed['sha256']
        report['retrieval_url'] = receipt['url']
        report['result'] = 'MATCH' if confirmed['rna']==original['rna'] else 'MISMATCH'
    except Exception as error:
        report['reason'] = type(error).__name__ + ': ' + str(error)[:250]
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(report,indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report,indent=2))
    return 0 if report['result']=='MATCH' else 1

if __name__=='__main__':raise SystemExit(check())
