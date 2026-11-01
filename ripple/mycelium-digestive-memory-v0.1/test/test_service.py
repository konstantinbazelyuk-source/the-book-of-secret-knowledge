"""Real multi-process SQLite replay accounting with a controlled clock."""
import hashlib
import json
import multiprocessing
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'python'))
import memory_service


def concurrent_store(db_path,barrier,output):
    memory_service.time.time=lambda:12345
    service=memory_service.MemoryService(db_path,{'tenant':'local','owner':'owner','project':'race'})
    original_recall=service.memory.recall
    first=True
    def synchronized_recall(*args,**kwargs):
        nonlocal first
        result=original_recall(*args,**kwargs)
        if first:
            first=False
            barrier.wait(timeout=8)
        return result
    service.memory.recall=synchronized_recall
    key='a'*64
    payload={'cacheKey':key,'verification':'serial-parity','value':123}
    digest=hashlib.sha256(json.dumps(payload,separators=(',',':')).encode()).hexdigest()
    body=json.dumps({'payload':payload,'digest':digest},separators=(',',':'))
    try:
        output.put(service.store_results([{'key':key,'value':body}])[0]['status'])
    finally:
        service.memory.close()


class ServiceTests(unittest.TestCase):
    def test_concurrent_identical_store_counts_one_new_record(self):
        context=multiprocessing.get_context('spawn')
        with tempfile.TemporaryDirectory() as directory:
            db=str(Path(directory)/'memory.sqlite')
            initial=memory_service.MemoryService(db,{'tenant':'local','owner':'owner','project':'race'})
            initial.memory.close()
            barrier=context.Barrier(2);output=context.Queue()
            children=[context.Process(target=concurrent_store,args=(db,barrier,output)) for _ in range(2)]
            for child in children:child.start()
            try:
                statuses=[output.get(timeout=10) for _ in children]
                for child in children:
                    child.join(timeout=10)
                    self.assertEqual(child.exitcode,0)
                self.assertEqual(sorted(statuses),['already_known','stored'])
                service=memory_service.MemoryService(db,{'tenant':'local','owner':'owner','project':'race'})
                try:self.assertEqual(service.memory.health(service.cache_scope)['events'],1)
                finally:service.memory.close()
            finally:
                for child in children:
                    if child.is_alive():child.terminate();child.join()
                output.close()


if __name__=='__main__':unittest.main(verbosity=2)
