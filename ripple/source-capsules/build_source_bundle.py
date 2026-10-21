#!/usr/bin/env python3
"""Recreate public source-only release ZIP after validating every original source member."""
import pathlib,hashlib,zipfile,sys
from restore_capsules import main as verify_and_restore, HERE

def main():
    verify_and_restore(['--verify'])
    output=HERE/'Ripple-Lineage-Reconstructed-Source-Only.zip'
    restored=HERE/'restored'
    verify_and_restore(['--extract','--dest',str(restored)])
    paths=sorted(p for p in restored.rglob('*') if p.is_file())
    with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in paths:z.write(p,p.relative_to(restored))
    digest=hashlib.sha256(output.read_bytes()).hexdigest()
    (HERE/'RELEASE_SHA256.txt').write_text(f'{digest}  {output.name}\n')
    print(f'Created {output} with {len(paths)} code/documentation files, SHA256 {digest}')
if __name__=='__main__':main()
