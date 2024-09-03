
import random


_i=50
_time=0
ret=[]
_val=0
while _i > 0:
    _val=_val+random.choice([-3.5,-1,1.5,1.7,2.5])
    _time=_time+random.choice([1.3,0.67,1])
    ret.append([_time,_val])
    _i-=1
print(ret)