import mimicpy
from .parse import xvg

class Analysis(mimicpy.core.base.BaseHandle):
    def gmx(self, cmd, **kwargs):
        host = mimicpy.getHost()
        
        prev_files = host.ls()
        
        super().gmx(cmd, **kwargs)
        
        new_files = host.ls()
        
        extra_files = [n for n in new_files if n not in prev_files]
        
        if len(extra_files) == 1 and extra_files[0].split('.')[1] == 'xvg':
            o = host.read(extra_files[0])
            host.rm(extra_files[0])
            return xvg(o)
        else:
            return extra_files