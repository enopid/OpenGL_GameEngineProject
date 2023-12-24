import numpy as np

class lights:
    def __init__(self):
        self.lightlist=[]
        self.lightnum=0

    def addlight(self, light):
        self.lightlist.append(light)
        self.lightnum=self.lightnum+1

class light:
    def __init__(self, pos, color):
        self.pos=np.array(pos)
        self.color=np.array(color)