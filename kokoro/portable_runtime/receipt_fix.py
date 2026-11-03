from pathlib import Path

def apply(root: Path) -> None:
    file=root/'studio/kokoro_bridge/portable_session.py'
    s=file.read_text()
    if "self.asset_sha256=manifest['files']['kokoro_runtime.glb']" in s:return
    s=s.replace('        self.timeout=timeout;self._temporary=', "        self.asset_sha256=manifest['files']['kokoro_runtime.glb']\n        self.timeout=timeout;self._temporary=")
    s=s.replace("self.ready.get('blender_required') is not False:","self.ready.get('blender_required') is not False or self.ready.get('asset_sha256')!=self.asset_sha256:")
    old="            self.last_frame=checked['frame'];self.last_time=checked['sim_time_s'];return reply"
    assert old in s
    s=s.replace(old,"""            expected={'asset_sha256':self.asset_sha256,'sim_time_s':checked['sim_time_s'],
              'profile_sha256':checked['profile_sha256'],'applied_joint_positions_rad':checked['joints_rad'],
              'manual_face_controls':checked['face'],'rendered':render,
              'resolution':[checked['camera']['render_width'],checked['camera']['render_height']],
              'view':'external_'+checked['camera']['view'],'display_mode':self.display_mode,
              'feeds_legacy_feedback':False}
            for key,value in expected.items():
                if key not in reply or reply[key]!=value:raise ValueError('Portable receipt field mismatch: '+key)
            if type(reply['rendered']) is not bool or type(reply['feeds_legacy_feedback']) is not bool:
                raise ValueError('Portable receipt flags must be boolean')
            if self.display_mode=='window':
                if reply.get('image_file') is not None or reply.get('image_delivery')!=('direct_browser' if render else 'not_rendered'):
                    raise ValueError('Portable direct delivery mismatch')
            self.last_frame=checked['frame'];self.last_time=checked['sim_time_s'];return reply""")
    file.write_text(s)

if __name__=='__main__':
    import sys
    apply(Path(sys.argv[1]))
