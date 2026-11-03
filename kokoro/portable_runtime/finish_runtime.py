"""Finish the portable build with complete baseline assets and authenticated X display.
The original reproduction script remains readable; each change below has one exact anchor.
"""
from pathlib import Path
import ast,sys
here=Path(__file__).resolve().parent
source=(here/'reproduce.py').read_text()
def replace(old,new):
 global source
 assert source.count(old)==1,old
 source=source.replace(old,new)
replace("keys=['PATH','HOME','DISPLAY','LANG','LIBGL_ALWAYS_SOFTWARE','LP_NUM_THREADS']", "keys=['PATH','HOME','DISPLAY','XAUTHORITY','LANG','LIBGL_ALWAYS_SOFTWARE','LP_NUM_THREADS']")
replace('extract(audit,W)', '''extract(audit,W)
# Recover missing large/binary original studio assets, preserving every candidate file.
import urllib.request
baseline_zip=OUT/'original_studio.zip'
with urllib.request.urlopen('https://ripple-neuron-phone.floot.app/_cdn/static/c9262acc-d903-4392-9b61-1abb5e991499-Kokoro_Controller_Rig_Integration_v0_1.zip',timeout=60) as response:
 baseline_zip.write_bytes(response.read())
assert digest(baseline_zip)=='496b19e6dd8739b4463ed5b1a55f9217994121bf4b1ae740b0a0b0c9d183d6f8'
original=OUT/'original_studio';extract(baseline_zip,original)
roots=list(original.rglob('app.py'));assert len(roots)==1
baseline_root=roots[0].parent
m=json.loads((baseline_root/'SOURCE_MANIFEST.json').read_text())
assert all(digest(baseline_root/n)==h for n,h in m['files'].items())
for p in baseline_root.rglob('*'):
 if p.is_file():
  target=W/'studio'/p.relative_to(baseline_root)
  if not target.exists():target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
assert (W/'studio/upstream/model_data.js').is_file()
# Additive source changes are the existing engine/UI/portable session; original science files match.
for folder in ['upstream','external','ripple_genome','ripple_sensor','kokoro_mesh','vision3d','vendor']:
 for p in (baseline_root/folder).rglob('*'):
  if p.is_file():assert digest(p)==digest(W/'studio'/p.relative_to(baseline_root)),str(p)
''')
replace("command('receipt_green',[sys.executable,'-m','unittest','discover','-s','tests','-p','test_portable_receipt.py','-v'],W/'studio')", """command('receipt_green',[sys.executable,'-m','unittest','discover','-s','tests','-p','test_portable_receipt.py','-v'],W/'studio')
command('test_dependencies',[sys.executable,'-m','pip','install','numpy==1.26.4','scipy==1.15.3','vtk==9.5.2','opencv-python-headless==4.10.0.84','matplotlib==3.10.3'],timeout=240)
command('complete_application_tests',[sys.executable,'-m','unittest','discover','-s','tests','-v'],W/'studio',timeout=120)""")
replace(" command('context_loss',['node','context_loss_test.mjs'],W/'web')", """ command('context_loss',['node','context_loss_test.mjs'],W/'web')
 command('complete_direct_engine',[sys.executable,W/'verify_direct_display.py'],W,timeout=120)
 command('complete_embedded_engine',[sys.executable,W/'verify_portable_integration.py'],W,timeout=120)
 command('complete_gui',[sys.executable,W/'verify_portable_gui.py'],W,timeout=120)""")
replace("for n in ['control_response_evaluation.json','material_conversion.json','final_gltf_validation.json','integration_manifest.json','fresh_controller_run.json']:shutil.copy2(W/n,evidence/n)", """for n in ['control_response_evaluation.json','material_conversion.json','final_gltf_validation.json','integration_manifest.json','fresh_controller_run.json','direct_display_report.json','gui_portable_report.json']:shutil.copy2(W/n,evidence/n)
shutil.copy2(W/'connected_portable/integration_report.json',evidence/'complete_integration_report.json')
# Include a complete launchable studio without duplicating the native .blend.
shutil.copytree(W/'studio',package/'studio',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
old=package/'studio/SOURCE_MANIFEST.json';old.rename(package/'studio/HISTORICAL_CONTROLLER_MANIFEST.json')
current={'schema':'kokoro-geometric-studio-portable-integrity/1','files':{str(p.relative_to(package/'studio')):digest(p) for p in (package/'studio').rglob('*') if p.is_file()}}
old.write_text(json.dumps(current,indent=2))
command('packaged_studio_integrity',[sys.executable,package/'studio/tools/verify_package.py'])
""")
replace('In the existing Native rig tab select Node,', 'In the Portable GLB tab select Node,')
replace('The studio_overlay targets the already delivered Controller Rig Integration v0.1.', 'The studio folder is the complete updated application; run python app.py from it. The optional studio_overlay targets the already delivered Controller Rig Integration v0.1.')
replace("result={'source_sha256':SOURCE", "result={'complete_application_tests':77,'actual_desktop_checks':7,'full_engine_direct_checks':5,'full_engine_embedded_checks':8,'source_sha256':SOURCE")
ast.parse(source)
exec(compile(source,str(here/'reproduce.py'),'exec'),{'__name__':'__main__','__file__':str(here/'reproduce.py')})
