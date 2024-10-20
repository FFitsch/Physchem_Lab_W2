import numpy as np

def group(a,thr):
    x = np.sort(a)
    diff = x[1:]-x[:-1]
    gps = np.concatenate([[0],np.cumsum(diff>=thr)])
    return [x[gps==i] for i in range(gps[-1]+1)]