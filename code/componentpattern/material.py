class MaterialProperty:
    def __init__(self,name,value,minvalue,maxvalue):
        self.value=value
        self.name=name
        self.maxvalue=maxvalue
        self.minvalue=minvalue
    
    def setvalue(self, value):
        self.value=min(max(value,self.minvalue),self.maxvalue)

    def bind(self, location):
        self.location=location
        return self

class MaterialProperties:
    def __init__(self):
        self.materiallist=[]
        self.materialdict={}
        self.meterialnum=0
        self.currentmaterialindex=0

    def addmeterial(self,_meterial):
        self.materiallist.append(_meterial)
        self.materialdict[_meterial.name]=self.meterialnum
        self.meterialnum=self.meterialnum+1

    def next(self):
        self.currentmaterialindex=(self.currentmaterialindex+1)%self.meterialnum

    def getcurrentmaterial(self):
        return self.materiallist[self.currentmaterialindex]
    
    def getmaterial(self,name):
        return self.materiallist[self.materialdict[name]]