import mimicpy
from .parse import xvg
import pandas as pd

class Analysis(mimicpy.core.base.BaseHandle):
    def __init__(self, status=None):
        super().__init__(status)
        self.xvg = mimicpy.utils.logger.LogString()
        self.logger.add(xvg=self.xvg)
        
    def _xvg_df(self, cmd, prev_files):
        host = mimicpy.getHost()
        
        new_files = host.ls()
        
        extra_files = [n for n in new_files if n not in prev_files]
        
        if len(extra_files) == 1 and extra_files[0].split('.')[1] == 'xvg':
            o = host.read(extra_files[0])
            self.logger.write('xvg', f"============Running {cmd}============\n")
            self.logger.write('xvg', o)
            host.rm(extra_files[0])
            return xvg(o)
        else:
            return extra_files
    
    def gmx(self, cmd, **kwargs):
        
        prev_files = mimicpy.getHost().ls()
        
        if 's' not in kwargs: kwargs['s'] = self.getcurrent('tpr')
        if 'f' not in kwargs: kwargs['f'] = self.gethistory('trr')
        
        _kwargs = kwargs.copy()
        del _kwargs['f']
        
        df = pd.DataFrame()
        
        for trr in kwargs['f']:
            super().gmx(cmd, f=trr, **_kwargs)
            if df.empty: df = self._xvg_df(cmd, prev_files)
            else: df = df.append(self._xvg_df(cmd, prev_files))
        
        return df.sort_index(axis = 0)
        