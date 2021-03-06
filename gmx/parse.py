import mimicpy
import re
import pandas as pd
import numpy as np
from ..dashboard import PlotBoxDF

def xvg(xvg, readlabel=True):
    title = ''
    x = []
    y = []
    
    if readlabel:
        reg = re.compile(r"@\s*title\s*\"(.*?)\"", re.MULTILINE).findall(xvg)
        if reg == []: title = 'Title'
        else: title = reg[0]
            
        reg = re.compile(r"@\s*xaxis\s*label\s*\"(.*?)\"", re.MULTILINE).findall(xvg)
        if reg == []: xlabel = 'X Axis'
        else: xlabel = reg[0]
    
        reg = re.compile(r"@\s*yaxis\s*label\s*\"(.*?)\"", re.MULTILINE).findall(xvg)
        if reg == []: ylabel = 'Y Axis'
        else: ylabel = reg[0]
    
        reg = re.compile(r"@\s*s\w\s*legend\s*\"(.*?)\"", re.MULTILINE)
        
        cols = [ylabel+': '+m.groups()[0] for m in reg.finditer(xvg)]
            
        if cols:
            cols = [xlabel] + cols
        else: cols = [xlabel, ylabel]
            
        reg = re.compile(r"@.*", re.MULTILINE)
        
        ends = [m.end() for m in reg.finditer(xvg)]
        end = max(ends)
                
    else:
        xlabel = 'X'
        ylabel = 'Y'
        
    data = xvg[end+1:]
    ar = np.array(list(map(float, data.split())))
    
    reshaped = np.reshape(ar, (len(ar)//len(cols),len(cols)))
    df = pd.DataFrame(reshaped, columns=cols).set_index([xlabel])
    df.name = title
    return df
    
def errors(file_eval=None):
    
    def _parse(out):
        output = _global.host.read(out)   
        return BaseHandle._notes(output), BaseHandle._gmxerrhdnl(output, dont_raise=True)
    # include ls() in local
    if file_eval is None:
        files = _global.host.cmd.ls(file_eval=lambda a: True if a.endswith('.log') or a.endswith('.out') else False)
    else:
        files = _global.host.cmd.ls(file_eval=file_eval)
        
    for file in files:
        print(f"\n<========{file}========>")
            
        notes, errors = _parse(file)
            
        if notes: print(f"\nThere were note(s)/warning(s):\n\n{notes}")
        if errors: print(f"\nThere were error(s):\n\n{errors}")

def dump(file):
    ext = file.split('.')[-1]
    if ext == 's': cmd = 's'
    elif ext == 'trr' or ext == 'xtc' or ext == 'gro' or ext == 'pdb': cmd = 'f'
    elif ext == 'edr': cmd = 'e'
    elif ext == 'cpt': cmd = 'cp'
    elif ext == 'top': cmd = 'p'
    elif ext == 'mtx': cmd = 'mtx'
    
    kwargs = {cmd:file}
    
    d = BaseHandle()
    out = d.gmx(f'dump', **kwargs)
    return out

@PlotBoxDF
def log(file):
    f = _global.host.read(file)
    x = re.compile(r"^\s*(Step\s*Time)\n(.+)\n(?:\n.+)+\s*Energies\s*\(kJ/mol\)((?:\n.+)+)\s+\n",\
               re.MULTILINE)
    res = x.findall(f)
    
    def c(log_txt):
        colms = []
        vals = []
        n = 15
        colms += log_txt[0].split()
        vals += [float(i) for i in log_txt[1].split()]
        for j,l in enumerate(log_txt[2].splitlines()):
            if j%2 != 0:
                cols = [l[i:i+n].strip() for i in range(0, len(l), n)]
                colms.extend(cols)
            else:
                cols = [float(l[i:i+n].strip()) for i in range(0, len(l), n)]
                vals.extend(cols)
        return (colms, vals)
   
    cols, v1 = c(res[0])
    
    vals = []
    
    for i in res:
        vals.append(c(i)[1])
        
    df = pd.DataFrame(vals, columns=cols)
    df = df.set_index(['Step', 'Time'])
    
    return df
