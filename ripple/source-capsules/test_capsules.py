import unittest, tempfile, json, pathlib, shutil
from restore_capsules import HERE, validate, sha
class CapsuleVerificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.catalog=json.loads((HERE/'SOURCE_CAPSULES.json').read_text())['capsules']
    def test_each_capsule_hash_and_all_file_hashes(self):
        for row in self.catalog:
            p=HERE/'capsules'/pathlib.Path(row['git_path']).name
            with self.subTest(capsule=p.name):self.assertTrue(validate(p,row))
    def test_mutation_detected(self):
        c=self.catalog[0];p=HERE/'capsules'/pathlib.Path(c['git_path']).name
        with tempfile.TemporaryDirectory() as td:
            mutated=pathlib.Path(td)/p.name
            mutated.write_bytes(p.read_bytes().replace(b'A',b'B',1))
            with self.assertRaises(ValueError):validate(mutated,c)
    def test_no_duplicate_capsule_hashes(self):
        self.assertEqual(len({c['archive_sha256'] for c in self.catalog}),len(self.catalog))
    def test_source_only_no_hidden_binary(self):
        for c in self.catalog:
            for f in c['files']:
                self.assertFalse(pathlib.PurePosixPath(f['path']).is_absolute())
                self.assertNotIn('..',pathlib.PurePosixPath(f['path']).parts)
                self.assertLessEqual(f['bytes'],350000)
if __name__=='__main__':unittest.main()
