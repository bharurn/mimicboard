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
            self.logger.write('xvg', f"==>XVG raw output from gmx {cmd}\n")
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

def distributeFrames(u, start, end, pkl_file):
    def wrapper(func):
        
        ###imports
        from mpi4py import MPI
        import time

        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        size = comm.Get_size()
        
        ###
        
        ###load files on rank 0
        if rank == 0:
            from tqdm import tqdm
            pbar = tqdm(desc=f"Starting", bar_format='{l_bar}{bar}|')
        else:
            files = None
        ###
        
        ###calculate start and end frames for each rank
        if end == -1: end_ = len(u.trajectory)
        else: end_ = end
        perrank = end_//size
        rank_start = start + rank*perrank
        rank_end = start + (rank+1)*perrank
        ###
        
        ###start calculating
        comm.Barrier()

        x = []
        
        if rank == 0:
            pbar.total=rank_end-rank_start
            pbar.desc = f"Calculating {rank_end-rank_start} frames on each rank"
        
        for i in range(rank_start, rank_end):
            u.trajectory[i]
            x.append((i,func(u)))
            if rank == 0: pbar.update(1)
    
        if rank == 0: pbar.close()
        ###
        
        ###gather results into rank 0
        result = comm.gather(x,root=0)

        if rank == 0:
            flat = [item for sublist in result for item in sublist]
            
            ##calculate extra frames not equally divided among ranks
            l = len(flat)
            if l < end_:
                pbar = tqdm(total=end_-l, desc=f"Calculating {end_-l} extra frames on rank 0", bar_format='{l_bar}{bar}|')
                
                for i in range(l, end_):
                    u.trajectory[i]
                    flat.append((i,func(u)))
                    pbar.update(1)
            ##
        
            x = [i[1] for i in sorted(flat, key=lambda x: x[0])] # flatten nested list
            
            if pkl_file != None: # pickle results    
                print("Pickling..")
                import pickle
                pickle.dump(x, open(pkl_file, 'wb'))
        ###
                
    return wrapper
        