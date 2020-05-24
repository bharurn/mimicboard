import numpy as np

def ids_dist(sele1, sele2, dist=3):
    mol = u.select_atoms(sele1)
    hyd = u.select_atoms(sele2)
    
    hpos = hyd.positions
    mpos = mol.positions
    pos = (mpos[:, np.newaxis] - hpos)
    
    reshaped = pos.reshape(-1, mpos.shape[1])
    dist = np.sum(np.abs(reshaped)**2,axis=1)**(1./2)
    dist = dist.reshape(pos.shape[0], pos.shape[1])
    
    ids = np.where(dist<3)
    vals = dist[ids]
    
    conv = lambda atom: f"{atom.resid+1}{atom.resname}_{atom.name}"
    
    return list(map(conv, mol.atoms[ids[0]])), list(map(conv, hyd.atoms[ids[1]])), vals