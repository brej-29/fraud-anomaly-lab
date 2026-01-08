import numpy as np
import pandas as pd
from evaluation.run import temporal_split, metrics, curve

def test_temporal_boundaries_do_not_share_timestamps():
    frame = pd.DataFrame({'Time':[0,1,2,3,4,5,5,5,8,9], 'Class':[0]*10})
    train,val,test = temporal_split(frame,.6,.2)
    assert train.Time.max() < val.Time.min() < test.Time.min()
    assert sum(map(len,(train,val,test))) == len(frame)

def test_known_counts_and_curves():
    y=np.array([1,0,1,0]*100)
    scores=np.arange(len(y),dtype=float)
    m=metrics(y,scores,10)
    assert m['caught']==5 and m['precision']==.5 and m['missed']==195
    for p in curve(y,scores,np.ones(len(y))):
        assert p['caught']==metrics(y,scores,p['k'])['caught']
        assert p['selectedAmount']==p['k']
