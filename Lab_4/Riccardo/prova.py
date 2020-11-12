import numpy as np
import time
timeout=time.time()+120
while time.time()< timeout :
    shape, scale = 2., 2.
    a = 10*np.random.gamma(shape, scale, 1)+30
    print(a)
    time.sleep(2)
