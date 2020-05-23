from .dashboard import PlotBoxDF
from ..core.base import BaseCalc
from .parse import xvg
import mimicpy._global as _global
import os

@PlotBoxDF
def d(top, trr, selections):
    df_l = None
    for l in trr:
        df = None
        for s in selections:
            if isinstance(s, str):
                BaseCalc.gmx('rms', s=top, f=l, o="temp.xvg", stdin=f'{s}\n{s}', noverbose=True)
                nm = s
            else:
                _global.host.write(str(s), "index.ndx")
                BaseCalc.gmx('rms', s=top, f=l, o="temp.xvg", n="index.ndx", noverbose=True)
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
    df_l = None
    for l in trr:
        df = None
        for s in selection:
            if isinstance(s, str):
                BaseCalc.gmx('rmsf', s=top, f=l, o="temp.xvg", stdin=f'{s}', noverbose=True)
            else:
                _global.host.write(str(s), "index.ndx")
                BaseCalc.gmx('rms', s=top, f=l, o="temp.xvg", n="index.ndx", noverbose=True)
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