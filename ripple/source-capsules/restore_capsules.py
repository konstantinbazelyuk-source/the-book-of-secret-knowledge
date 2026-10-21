#!/usr/bin/env python3
"""Restore audited Ripple source-only capsules; no code is executed by this tool."""
import argparse,base64,hashlib,io,json,pathlib,zipfile,sys
HERE=pathlib.Path(__file__).resolve().parent

def sha(data):return hashlib.sha256(data).hexdigest()
def validate(capsule_path, manifest):
    if not capsule_path.exists():raise FileNotFoundError(capsule_path)
    src=capsule_path.read_bytes()
    if sha(src)!=manifest['base64_sha256']:raise ValueError('Base64 source file SHA-256 mismatch')
    raw=base64.b64decode(src.strip(),validate=True)
    if sha(raw)!=manifest['capsule_sha256']:raise ValueError('Capsule archive SHA-256 mismatch')
    expected={row['path']:row for row in manifest['files']}
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        actual=set(z.namelist())-{'RIPPLE_CAPSULE_MANIFEST.json'}
        if actual!=set(expected):raise ValueError('Source list mismatch')
        internal=json.loads(z.read('RIPPLE_CAPSULE_MANIFEST.json'))
        if internal.get('archive_sha256')!=manifest['archive_sha256']:raise ValueError('Ancestor archive hash mismatch')
        for name,meta in expected.items():
            p=pathlib.PurePosixPath(name)
            if p.is_absolute() or '..' in p.parts or '\\' in name:raise ValueError('Unsafe archive path')
            info=z.getinfo(name)
            if info.file_size>1_000_000:raise ValueError('Unexpectedly large member')
            b=z.read(name)
            if len(b)!=meta['bytes'] or sha(b)!=meta['sha256']:raise ValueError('Member source checksum mismatch: '+name)
    return raw

def main(argv=None):
    p=argparse.ArgumentParser(description='Verify and restore Ripple source-only capsules; no binary/vendor copies and no programs executed.')
    p.add_argument('--verify',action='store_true')
    p.add_argument('--extract',action='store_true')
    p.add_argument('--only',help='One archive filename or capsule slug')
    p.add_argument('--dest',type=pathlib.Path,default=HERE/'restored')
    args=p.parse_args(argv)
    catalog=json.loads((HERE/'SOURCE_CAPSULES.json').read_text())['capsules']
    selected=[row for row in catalog if not args.only or args.only in (row['archive_name'],pathlib.Path(row['git_path']).name.removesuffix('.zip.b64'))]
    if not selected:raise SystemExit('No matching capsule')
    total=0
    for row in selected:
        file=HERE/'capsules'/pathlib.Path(row['git_path']).name
        data=validate(file,row)
        total+=len(row['files'])
        if args.extract:
            destination=args.dest/file.name.removesuffix('.zip.b64')
            destination.mkdir(parents=True,exist_ok=True)
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                for name in (m['path'] for m in row['files']):
                    outfile=destination/name
                    outfile.parent.mkdir(parents=True,exist_ok=True)
                    if outfile.exists():
                        if sha(outfile.read_bytes())!=next(m['sha256'] for m in row['files'] if m['path']==name):
                            raise FileExistsError('Refuse overwrite changed file: '+str(outfile))
                    else:outfile.write_bytes(z.read(name))
        print(('RESTORED' if args.extract else 'VALID'),row['archive_name'],len(row['files']),'files')
    print('Verified',len(selected),'distinct source capsules and',total,'individual files. Source-only, no code execution claimed.')

if __name__=='__main__':main()
