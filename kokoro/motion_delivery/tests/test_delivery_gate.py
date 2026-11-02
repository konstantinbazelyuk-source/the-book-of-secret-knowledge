import unittest, hashlib, math
from delivery_gate import issues, EXPECTED_SOURCE

def fixture():
    # Synthetic validator-test receipt, never presented as a render.
    return {'source_sha256_before':EXPECTED_SOURCE,'source_sha256_after':EXPECTED_SOURCE,
      'action':'KOKORO — blink, jaw and head check','fps':12,'duration_seconds':5,
      'frames':[{'frame':n,'png_sha256':hashlib.sha256(str(n).encode()).hexdigest(),
        'head_z':math.sin(n/6)*.1,'jaw_x':math.sin(n/5)*.12,
        'left_eyelid_y':math.sin(n/4)*.04,'right_eyelid_y':math.sin(n/4)*.04} for n in range(1,61)]}
class GateTests(unittest.TestCase):
    def test_accepts_motion_receipt(self):self.assertEqual(issues(fixture()),[])
    def test_wrong_source(self):
        r=fixture();r['source_sha256_before']='0'*64;self.assertTrue(issues(r))
    def test_modified_source(self):
        r=fixture();r['source_sha256_after']='1'*64;self.assertTrue(issues(r))
    def test_missing_frame(self):
        r=fixture();r['frames'].pop(4);self.assertTrue(issues(r))
    def test_repeated_pixels(self):
        r=fixture()
        for f in r['frames']:f['png_sha256']='a'*64
        self.assertTrue(issues(r))
    def test_static_control(self):
        for control in ['head_z','jaw_x','left_eyelid_y','right_eyelid_y']:
            r=fixture()
            for f in r['frames']:f[control]=0
            self.assertTrue(issues(r),control)
    def test_nan(self):
        r=fixture();r['frames'][4]['jaw_x']=float('nan');self.assertTrue(issues(r))
    def test_wrong_action(self):
        r=fixture();r['action']='unrelated';self.assertTrue(issues(r))
    def test_wrong_duration(self):
        r=fixture();r['duration_seconds']=.01;self.assertTrue(issues(r))
    def test_no_receipt(self):self.assertTrue(issues({}))
if __name__=='__main__':unittest.main()
