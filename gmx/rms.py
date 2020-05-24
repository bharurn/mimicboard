from ..dashboard import PlotBoxDF
from mimicpy.simulate import BaseHandle
from .parse import xvg
import mimicpy._global as _global
import os

# rms calculation using gromacs

@PlotBoxDF
def d(top, trr, selections):
    gmx_hndl = BaseHandle()
    df_l = None
    for l in trr:
        df = None
        for s in selections:
            if isinstance(s, str):
                gmx_hndl.gmx('rms', s=top, f=l, o="temp.xvg", stdin=f'{s}\n{s}', noverbose=True)
                nm = s
            else:
                _global.host.write(str(s), "index.ndx")
                gmx_hndl.gmx('rms', s=top, f=l, o="temp.xvg", n="index.ndx", noverbose=True)
                os.remove("index.ndx")
                nm = s.name
                
            _df = xvg(_global.host.read("temp.xvg"), readlabel=False)
            os.remove("temp.xvg")
            if df is None:
                df = _df
                df = df.rename(columns={"Y": nm})
            else:
                df[s] = _df['Y']
        if df_l is None: df_l = df
        else: df_l.append(df)
    return df_l.set_index(['Time'])

@PlotBoxDF(x_axis=['ID'])
def f(top, trr, selection):
    gmx_hndl = BaseHandle()
    df_l = None
    for l in trr:
        df = None
        for s in selection:
            if isinstance(s, str):
                gmx_hndl.gmx('rmsf', s=top, f=l, o="temp.xvg", stdin=f'{s}', noverbose=True)
            else:
                _global.host.write(str(s), "index.ndx")
                gmx_hndl.gmx('rms', s=top, f=l, o="temp.xvg", n="index.ndx", noverbose=True)
                os.remove("index.ndx")
                
            _df = xvg(_global.host.read("temp.xvg"), readlabel=False)
            os.remove("temp.xvg")
            if df is None:
                df = _df
                df = df.rename(columns={"Y": s.name})
            else:
                df[s] = _df['Y']
        if df_l is None: df_l = df
        else: df_l.append(df)
    return df_l.set_index(['ID'])
