from . import handlePDB as hpdb

class Selection:
    
    lst = ['serial', 'name', 'resName', 'chainID', 'special']
    
    def __init__(self, **kwargs):
        
        for k in kwargs.keys():
            if k not in self.lst:
                slst = ", ".join(self.lst)
                raise Exception(f'{k} not a valid selection. Use any of the following keywords:\n{slst}')
            else:
                setattr(self, k, kwargs[k])
        
        self.name = 'MOL'
        self.pdb = ''
    
    def todict(self):
        kwargs = {}
        for i in dir(self):
            if i in self.lst:
                kwargs[i] = getattr(self, i)
        
        return kwargs
    
    def __str__(self):
        
        i = 1
        
        s = f" [{self.name}]  \n"
        
        for pdb in self.pdb.splitlines():
            if hpdb.matchLine(pdb, **self.todict()):
                s += f" {i} "
            
            if hpdb.matchLine(pdb, record='ATOM') or hpdb.matchLine(pdb, record='HETATM'): i += 1
        
        return s
    
    def tolist(self):
        i = 1
        
        s = []
        
        for pdb in self.pdb.splitlines():
            if hpdb.matchLine(pdb, **dict(self)):
                s.append(i)
            
            if hpdb.matchLine(pdb, record='ATOM') or hpdb.matchLine(pdb, record='HETATM'): i += 1
        
        return s