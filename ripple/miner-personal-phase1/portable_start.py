"""Windows Python embeddable runtime, no external Python installation required."""
import os
import sys
from pathlib import Path
root=Path(__file__).resolve().parent
node=root/'runtime'/'node.exe'
if node.is_file():os.environ['RIPPLE_NODE_BIN']=str(node)
data=Path.home()/'.ripple_antminer_v02'
data.mkdir(exist_ok=True)
log=open(data/'ripple_controller.log','a',encoding='utf8',buffering=1)
sys.stdout=log
sys.stderr=log
from app import main
if __name__=='__main__':main()