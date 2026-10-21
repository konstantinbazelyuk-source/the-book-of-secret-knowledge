import asyncio
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from miner import (GENESIS_HEADER, GENESIS_HASH, sha256d, block_hash,
                   target_from_bits, target_for_difficulty, Work, header_prefix,
                   scan_nonces, wordswap, StratumMiner, DIFF1_TARGET, benchmark, run_with_retries)


class MathematicalTests(unittest.TestCase):
    def test_bitcoin_genesis_80_byte_known_answer(self):
        self.assertEqual(len(GENESIS_HEADER), 80)
        self.assertEqual(block_hash(GENESIS_HEADER), GENESIS_HASH)
        proof = int.from_bytes(sha256d(GENESIS_HEADER), 'little')
        self.assertLessEqual(proof, target_from_bits(0x1d00ffff))
        self.assertEqual(target_from_bits(0x1d00ffff), DIFF1_TARGET)

    def test_header_layout_and_nonces(self):
        w = Work('a','00'*32,'aa','bb',(), '20000000', '207fffff', '5f5e1000',
                 True,'cafe',4,'1e-9')
        prefix = header_prefix(w, 17)
        self.assertEqual(len(prefix), 76)
        self.assertEqual(prefix[:4].hex(), '00000020')
        self.assertEqual(prefix[36:68], sha256d(bytes.fromhex('aacafe00000011bb')))
        self.assertEqual(prefix[68:72].hex(), '00105e5f')
        self.assertEqual(prefix[72:76].hex(), 'ffff7f20')
        count, matches = scan_nonces(prefix, 0, 100, (1<<256)-1, 1)
        self.assertEqual(count, 100)
        self.assertEqual(len(matches), 100)
        self.assertEqual(matches[0][1], block_hash(prefix + b'\x00\x00\x00\x00'))
        self.assertEqual(scan_nonces(prefix, 0, 100, 0, 0)[0], 100)

    def test_byte_order_and_difficulty(self):
        self.assertEqual(wordswap('01020304'*8), bytes.fromhex('04030201'*8))
        self.assertEqual(target_for_difficulty('1'), DIFF1_TARGET)
        self.assertEqual(target_for_difficulty('2'), DIFF1_TARGET//2)
        self.assertEqual(target_for_difficulty('1e-15'), (1<<256)-1)
        for invalid in ['0', '-1', 'NaN', 'Infinity']:
            with self.assertRaises(ValueError): target_for_difficulty(invalid)
        with self.assertRaises(ValueError): target_from_bits(0x1d80ffff)

    def test_benchmark_performs_hashes(self):
        result = benchmark(100)
        self.assertEqual(result['hashes'], 100)
        self.assertGreater(result['hashes_per_second'], 0)


class RetryTests(unittest.IsolatedAsyncioTestCase):
    async def test_bounded_pool_reconnect(self):
        from unittest.mock import patch, AsyncMock
        counter=[0]
        class MockMiner:
            async def run(self):
                counter[0]+=1
                if counter[0]==1:raise ConnectionError('local pool outage')
                return {'ok':True}
        with patch('miner.asyncio.sleep', new_callable=AsyncMock) as sleep:
            result=await run_with_retries(lambda:MockMiner(), max_retries=1)
        self.assertEqual(result,{'ok':True})
        self.assertEqual(counter[0],2)
        sleep.assert_awaited_once_with(2)

class PoolLoopbackTests(unittest.IsolatedAsyncioTestCase):
    async def test_local_pool_receives_verifiable_share(self):
        got = asyncio.Event()
        seen = []
        async def mock_pool(reader, writer):
            try:
                while line := await reader.readline():
                    import json
                    item = json.loads(line)
                    if item['method'] == 'mining.subscribe':
                        reply = {'id': item['id'], 'result': [[['mining.notify','id']], 'cafe', 4], 'error': None}
                        writer.write((json.dumps(reply)+'\n').encode())
                        await writer.drain()
                    elif item['method'] == 'mining.authorize':
                        for packet in [
                            {'id':item['id'],'result':True,'error':None},
                            {'id':None,'method':'mining.set_difficulty','params':[1e-6]},
                            {'id':None,'method':'mining.notify','params':['job1','00'*32,'aa','bb',[],
                                      '20000000','207fffff','5f5e1000', True]}
                        ]:
                            writer.write((json.dumps(packet)+'\n').encode())
                        await writer.drain()
                    elif item['method'] == 'mining.submit':
                        params = item['params']
                        w = Work('job1','00'*32,'aa','bb',(), '20000000','207fffff','5f5e1000',
                                 True,'cafe',4,'1e-6')
                        nonce = int(params[4],16)
                        ex2 = int(params[2],16)
                        candidate = header_prefix(w, ex2) + nonce.to_bytes(4, 'little')
                        valid = int.from_bytes(sha256d(candidate), 'little') <= target_for_difficulty('1e-6')
                        seen.append((params,valid))
                        writer.write((json.dumps({'id':item['id'],'result':valid,'error':None})+'\n').encode())
                        await writer.drain()
                        got.set()
            finally:
                writer.close()
                await writer.wait_closed()
        server = await asyncio.start_server(mock_pool, '127.0.0.1', 0)
        port = server.sockets[0].getsockname()[1]
        try:
            miner = StratumMiner('127.0.0.1', port, 'test.worker', 'x',
                                 duration=1.7, workers=1, chunk=200, quiet=True)
            stats = await asyncio.wait_for(miner.run(), timeout=15)
            self.assertTrue(got.is_set())
            self.assertGreater(stats['hashes'], 0)
            self.assertGreater(stats['shares_submitted'], 0)
            self.assertTrue(all(correct for _, correct in seen))
            self.assertGreater(stats['accepted'],0)
        finally:
            server.close()
            await server.wait_closed()


if __name__ == '__main__': unittest.main()
