import sys, pygame, os
from pygame.locals import *
from pygame.constants import *
from OpenGL.GL import *
from OpenGL.GLU import *

from vector import *
import shader
from OBJhandler import *

from PIL import Image

import json

from enum import Enum

pygame.init()
viewport = (800,600)
width = viewport[0]
height = viewport[1]
pygame.display.set_mode(viewport, OPENGL | DOUBLEBUF)

#init shader
OpaqueShader = shader.Program(shader.initprogram1())
OpaqueShader.InitLight()
OpaqueShader.InitCamera()
OpaqueShader.InitMaterial()
OpaqueShader.InitSkyBox()

testprogram = shader.Program(shader.initBillboardprogram())
testprogram.InitCamera()
testprogram.InitMaterial()

lightprogram = shader.Program(shader.initlightprogram())
lightprogram.InitLight()
lightprogram.InitCamera()

skyboxprogram = shader.Program(shader.initSkyboxprogram())
skyboxprogram.InitSkyBox()
skyboxprogram.InitCamera()

object1 = OBJ("./model/testsphere2.obj", swapyz=False)
object2 = OBJ("./model/testsphere1.obj", swapyz=False)
object3 = OBJ("./model/lamp.obj", swapyz=False)
skyboxobj = OBJ("./model/cube.obj", swapyz=False)
lightobj = OBJ("./model/light.obj", swapyz=False)

glViewport(0, 0, width, height)

glEnable(GL_DEPTH_TEST)
glEnable(GL_DEBUG_OUTPUT)

glEnable(GL_BLEND);  
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);  

skyboxvertices=[]

class Scene:
    def __init__(self, filepath=None):
        self.objectlist=[]
        self.keys=None
        self.curLog=None
        if filepath!=None:
            self.ReadScene(filepath)
    
    def ReadScene(self,filepath):
        self.objectlist=[]
        with open(filepath, 'r') as f:
            jsonData=json.load(f)
            for OBJname in jsonData:
                gameobject=GameObject(OBJname)
                for componentname in jsonData[OBJname]:
                    data=jsonData[OBJname][componentname]
                    temp=eval("{}(data)".format(componentname))
                    gameobject.AddComponent(temp)
                self.AddGameObject(gameobject)

    
    def Update(self):
        for object in self.objectlist:
            object.Update()
    
    def HandleInput(self):
        self.keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                sys.exit()
            for object in self.objectlist:
                object.HandleInput(event)

    def AddGameObject(self,gameobject):
        gameobject.scene=self
        self.objectlist.append(gameobject)
    
    def GetGameObjectByComponent(self,name):
        for gameobject in self.objectlist:
            if gameobject.GetComponent(name):
                return gameobject

    def GetGameObjectsByComponent(self,name):
        gameobjects=[]
        for gameobject in self.objectlist:
            if gameobject.GetComponent(name):
                gameobjects.append(gameobject)
        return gameobjects
    
    def Log(self):
        temp=["Scene"]
        for gameobject in self.objectlist:
            temp.append("+--"+gameobject.name)
            temp.extend([" +--"+i for i in gameobject.Log()])
        if self.curLog!=temp:
            os.system('cls')
            print(*temp,sep="\n")
            self.curLog=temp

class GameObject:
    def __init__(self,name):
        self.components=[]
        self.AddComponent(Transform())
        self.transform=self.components[0]
        self.scene=None
        self.name=name
    
    def ChangeTransform(self,transform):
        self.components[0]=transform
        self.transform=self.components[0]

    
    def Update(self):
        for component in self.components:
            component.Update()
    
    def HandleInput(self,event):
        for component in self.components:
            component.HandleInput(event)
    
    def AddComponent(self, component):
        component.gameobject=self
        component.init()
        if type(component)==Transform and len(self.components):
            self.ChangeTransform(component)
        else:
            self.components.append(component)
    
    def GetComponent(self,name):
        for component in self.components:
            if type(component).__name__ == name:
                return component
        return False
    
    def Log(self):
        temp=[]
        for component in self.components:
            temp.extend(component.Log())
        return temp

class Component:
    def __init__(self,data):
        self.gameobject=None
        if data!=None:
            self.ReadData(data)
    
    def ReadData(self,data):
        pass

    def Init(self):
        pass

    def init(self):
        pass
    
    def Update(self):
        pass

    def HandleInput(self,event):
        pass
    
    def Log(self):
        return [self.__class__.__name__]

class Transform(Component):
    def __init__(self,data=None):
        self.__scale=[1,1,1]
        self.__rotation=[0,0,0]
        self.__translation=[0,0,0]
        super().__init__(data)
            
    def ReadData(self, data):
        self.__scale=data["scale"]
        self.__rotation=data["rotation"]
        self.__translation=data["translation"]
    
    def GetPos(self):
        return self.__translation
    
    def SetPos(self, pos):
        self.__translation=pos
    
    def GetRotation(self):
        return self.__rotation
    
    def SetRotation(self, rot):
        self.__rotation=rot

    def rotate(self, angle, x, y, z):
        s = math.sin(math.radians(angle))
        c = math.cos(math.radians(angle))
        magnitude = math.sqrt(x*x + y*y + z*z)
        nc = 1 - c
        
        x /= magnitude
        y /= magnitude
        z /= magnitude

        return np.array([
            [     c + x**2 * nc, y * x * nc - z * s, z * x * nc + y * s, 0],
            [y * x * nc + z * s,      c + y**2 * nc, y * z * nc - x * s, 0],
            [z * x * nc - y * s, z * y * nc + x * s,      c + z**2 * nc, 0],
            [                 0,                  0,                  0, 1],
        ])
    
    def GetScaleMatrix(self):
        return np.array([
            [      self.__scale[0],      0,      0,  0],
            [      0,      self.__scale[1],      0,  0],
            [      0,      0,      self.__scale[2],  0],
            [      0,      0,      0,  1]
        ])

    def GetRotateMatrix(self):
        t1=self.rotate(self.__rotation[0], 1, 0, 0)
        t2=self.rotate(self.__rotation[2],0,0,1)
        temp=np.dot(t1, t2)
        return np.dot(self.rotate(self.__rotation[1],0,1,0), temp)
    
    def GetTranslationMatrix(self):
        return np.array([
            [      1,      0,      0,  0],
            [      0,      1,      0,  0],
            [      0,      0,      1,  0],
            [ self.__translation[0], self.__translation[1], self.__translation[2],  1]
        ])

    def GetModelMatrix(self):
        return np.dot(np.dot(self.GetScaleMatrix(),self.GetRotateMatrix()),self.GetTranslationMatrix())
    
    def Log(self):
        temp=super().Log()
        temp.append("---"+"pos : {:0.1f}, {:0.1f}, {:0.1f}".format(self.__translation[0],self.__translation[1],self.__translation[2]))
        temp.append("---"+"scale : {:0.1f}, {:0.1f}, {:0.1f}".format(self.__scale[0],self.__scale[1],self.__scale[2]))
        temp.append("---"+"rotation : {:0.1f}, {:0.1f}, {:0.1f}".format(self.__rotation[0],self.__rotation[1],self.__rotation[2]))
        return temp

class Mesh(Component):
    def __init__(self, data=None):
        self.mesh=None
        super().__init__(data)
            
    def ReadData(self, data):
        self.mesh=OBJ(data["path"], swapyz=False)
    
    def SetMesh(self,obj):
        self.mesh=obj

    def Log(self):
        temp=super().Log()
        temp.append("---"+"mesh : {}".format(str(self.mesh)))
        return temp

class MeshRenderer(Component):
    def __init__(self,data=None):
        self.mesh=None
        self.camera=None
        self.program=None
        self.lights=[]
        super().__init__(data)
            
    def ReadData(self, data):
        1
        

    def Init(self):
        self.GetMesh()
        self.GetMaterial()
        self.GetLights()
        self.GetCamera()
    
    def GetLights(self):
        glUseProgram(self.program.program)
        self.lights=self.gameobject.scene.GetGameObjectsByComponent("Light")
        for i in range(len(self.lights)):
            light=self.lights[i].GetComponent("Light")
            glUniform3fv(self.program.lightslocation[i][0],1, self.lights[i].transform.GetPos())
            glUniform3fv(self.program.lightslocation[i][1],1, light.color)

    def GetMesh(self):
        if temp:=self.gameobject.GetComponent("Mesh"):
            self.mesh=temp

    def GetCamera(self):
        if temp:=self.gameobject.scene.GetGameObjectByComponent("Camera").GetComponent("Camera"):
            self.camera=temp

    def GetMaterial(self):
        if temp:=self.gameobject.GetComponent("Material"):
            self.Material=temp
        self.SetProgram(self.Material.program)
    
    def SetProgram(self,program):
        self.program=program

    def Update(self):
        glUseProgram(self.program.program)
        self.Material.UpdateMaterial()

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, self.mesh.mesh.vertices)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, self.mesh.mesh.normals)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 0, self.mesh.mesh.texcoords)

        view_matrix = self.camera.GetViewMatrix()
        projection_matrix = self.camera.GetProjectionMatrix()
        model_matrix = self.gameobject.transform.GetModelMatrix()
        
        self.lights=self.gameobject.scene.GetGameObjectsByComponent("Light")
        for i in range(len(self.lights)):
            light=self.lights[i].GetComponent("Light")
            glUniform3fv(self.program.lightslocation[i][0],1, self.lights[i].transform.GetPos())
            glUniform3fv(self.program.lightslocation[i][1],1, light.color)

        glUniformMatrix4fv(glGetUniformLocation(self.program.program, "uVMatrix"), 1, GL_FALSE, view_matrix)
        glUniformMatrix4fv(glGetUniformLocation(self.program.program, "uMMatrix"), 1, GL_FALSE, model_matrix)
        glUniformMatrix4fv(glGetUniformLocation(self.program.program, "uPMatrix"), 1, GL_FALSE, projection_matrix)

        glUniform3fv(self.program.cameralocation, 1, self.camera.gameobject.transform.GetPos())

        glDrawArrays(GL_TRIANGLES, 0, len(self.mesh.mesh.vertices))

class BillboardRenderer(Component):
    def __init__(self,data=None):
        self.camera=None
        self.program=None
        super().__init__(data)
            
    def ReadData(self, data):
        1
        

    def Init(self):
        self.GetCamera()
        self.GetMaterial()

    def GetCamera(self):
        if temp:=self.gameobject.scene.GetGameObjectByComponent("Camera").GetComponent("Camera"):
            self.camera=temp

    def GetMaterial(self):
        if temp:=self.gameobject.GetComponent("Material"):
            self.Material=temp
        self.SetProgram(self.Material.program)
    
    def SetProgram(self,program):
        self.program=program

    def Update(self):
        glUseProgram(self.program.program)
        self.Material.UpdateMaterial()

        vertices=[
            [1,1,0],
            [1,-1,0],
            [-1,1,0],

            [-1,1,0],
            [1,-1,0],
            [-1,-1,0]
        ]

        texcoords=[
            [1,0],
            [1,1],
            [0,0],
                    
            [0,0],
            [1,1],
            [0,1]
        ]

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, np.array(vertices))
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0,  np.array(texcoords))

        view_matrix = self.camera.GetViewMatrix()
        projection_matrix = self.camera.GetProjectionMatrix()
        model_matrix = np.dot(
            np.dot(self.gameobject.transform.GetScaleMatrix(),np.transpose(self.camera.gameobject.transform.GetRotateMatrix())),
                   self.gameobject.transform.GetTranslationMatrix()
            )

        glUniformMatrix4fv(glGetUniformLocation(self.program.program, "uVMatrix"), 1, GL_FALSE, view_matrix)
        glUniformMatrix4fv(glGetUniformLocation(self.program.program, "uMMatrix"), 1, GL_FALSE, model_matrix)
        glUniformMatrix4fv(glGetUniformLocation(self.program.program, "uPMatrix"), 1, GL_FALSE, projection_matrix)

        glDrawArrays(GL_TRIANGLES, 0, len(vertices))
    

class Light(Component):
    def __init__(self, data=None):
        self.type=None
        self.color=(1,1,1)
        self.intensity=1
        super().__init__(data)

    def init(self):
        self.gameobject.AddComponent(BillboardRenderer())
        self.gameobject.GetComponent("BillboardRenderer").SetProgram(testprogram)

        self.gameobject.AddComponent(Material())
        self.gameobject.GetComponent("Material").SetProgram(testprogram)
        self.gameobject.GetComponent("Material").SetTexture("albedo", "./icon/icon_light.png")
            
    def ReadData(self, data):
        self.type=data["type"]
        self.color=data["color"]
        self.intensity=data["intensity"]
            
    def Update(self):
        return super().Update()

    def Log(self):
        temp=super().Log()
        temp.append("---"+"type : {}".format(str(self.type)))
        temp.append("---"+"color : {}".format(str(self.color)))
        temp.append("---"+"intensity : {}".format(str(self.intensity)))
        return temp

class Camera(Component):
    def __init__(self):
        self.type=0
        self.rightvector=None
        self.upvector=None
        self.viewvector=None
    
    def GetUVWVector(self):
        rotationmatrix = self.gameobject.transform.GetRotateMatrix()
        self.rightvector=np.dot(rotationmatrix,np.array([1,0,0,0]))
        self.upvector=np.dot(rotationmatrix,np.array([0,1,0,0]))
        self.viewvector=np.dot(rotationmatrix,np.array([0,0,1,0]))

    def GetViewMatrix(self):
        self.GetUVWVector()
        
        return view(self.gameobject.transform.GetPos(),self.rightvector,self.upvector,self.viewvector)

    def GetProjectionMatrix(self):
        if self.type==0:
            return perspective(45, width/height, 0.1, 500)
        elif self.type==1:
            return perspective(45, width/height, 0.1, 500)
    
    def perspective(fovy, aspect, z_near, z_far):
        f = 1 / math.tan(math.radians(fovy) / 2)
        return np.array([
            [f / aspect,  0,                                   0,  0],
            [          0, f,                                   0,  0],
            [          0, 0, (z_far + z_near) / (z_near - z_far), -1],
            [          0, 0, (2*z_far*z_near) / (z_near - z_far),  0]
        ])
    
    def orthogonal(aspect, z_near, z_far):
        return np.array([
            [1 / aspect,  0,                                   0,  0],
            [          0, 1,                                   0,  0],
            [          0, 0, (z_far + z_near) / (z_near - z_far), -1],
            [          0, 0, (2*z_far*z_near) / (z_near - z_far),  0]
        ])

    def Log(self):
        temp=super().Log()
        temp.append("---"+"type : {}".format(str(self.type)))
        return temp

class Material(Component):
    materialTable={
        "albedo": 0,
        "metalness": 1,
        "roughness": 2,
        "ior": 3,
    }
    ID=0

    class MaterialProperty:
        def __init__(self, value=0):
            self.useTexture=False
            self.value=value
            self.texturePath=None
            self.textureID=Material.ID
            Material.ID+=1

    def __init__(self, data=None):
        self.type="Opaque"

        self.materialProperties=[]
        for i in range(4):
            self.materialProperties.append(Material.MaterialProperty())

        self.program = None
        super().__init__(data)
            
    def ReadData(self, data):
        self.type=data["type"]
        
        if self.type=="Opaque":
            self.SetProgram(OpaqueShader)

        for material in Material.materialTable:
            if material in data:
                if data[material]["usetexture"]:
                    self.SetTexture(material, data[material]["texturepath"])
                else:
                    self.SetValue(material, data[material]["value"])
    
    def UpdateMaterial(self):
        for material in Material.materialTable:
            if self.materialProperties[Material.materialTable[material]].useTexture:
                self.UpdateTexture(material)
            else:
                self.UpdateValue(material)

    def SetProgram(self,program):
        self.program=program
    
    def LoadTexture(self,filename):
        img = Image.open(filename, 'r').convert("RGBA")
        img_data = np.array(img, dtype=np.uint8)
        w, h = img.size

        texture = glGenTextures(1)

        glBindTexture(GL_TEXTURE_2D, texture)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)

        return texture
    
    def BindTexture(self, name, path):
        material=self.materialProperties[Material.materialTable[name]]
        glActiveTexture(GL_TEXTURE0+material.textureID)
        self.LoadTexture(path)

        material.useTexture=True
        material.texturePath=path
    
    def SetTexture(self, name, path):
        glUseProgram(self.program.program)
        self.BindTexture(name, path)
        material=self.materialProperties[Material.materialTable[name]]

        self.UpdateTexture(name)
    
    def UpdateTexture(self,name):
        material=self.materialProperties[Material.materialTable[name]]
        glUniform1i(glGetUniformLocation(self.program.program, "uMaterials[{}].useTexture".format(Material.materialTable[name])), material.useTexture)
        glUniform1i(glGetUniformLocation(self.program.program, "uMaterials[{}].texture".format(Material.materialTable[name])), material.textureID)

    def SetValue(self, name, value):
        glUseProgram(self.program.program)
        material=self.materialProperties[Material.materialTable[name]]
        material.useTexture=False
        if isinstance(value,float):
            value=[value,value,value]
        material.value=value

        self.UpdateValue(name)
    
    def UpdateValue(self,name):
        material=self.materialProperties[Material.materialTable[name]]

        glUniform1i(glGetUniformLocation(self.program.program, "uMaterials[{}].useTexture".format(Material.materialTable[name])), material.useTexture)
        glUniform3fv(glGetUniformLocation(self.program.program, "uMaterials[{}].value".format(Material.materialTable[name])), 1, material.value)

    def Log(self):
        temp=super().Log()
        temp.append("---"+"type : {}".format(str(self.type)))
        return temp

class CameraMove(Component):
    def __init__(self):
        self.camera=None
        self.sensitivity=0.1
        self.rotate=False

    def GetCamera(self):
        if temp:=self.gameobject.GetComponent("Camera"):
            self.camera=temp

    def Move(self):
        if self.gameobject.scene.keys[pygame.K_w]:
            temp=self.gameobject.transform.GetPos()
            temp=[temp[i]-self.camera.viewvector[i]*self.sensitivity for i in range(3)]
            self.gameobject.transform.SetPos(temp)
        elif self.gameobject.scene.keys[pygame.K_s]:
            temp=self.gameobject.transform.GetPos()
            temp=[temp[i]+self.camera.viewvector[i]*self.sensitivity for i in range(3)]
            self.gameobject.transform.SetPos(temp)
        if self.gameobject.scene.keys[pygame.K_a]:
            temp=self.gameobject.transform.GetPos()
            temp=[temp[i]-self.camera.rightvector[i]*self.sensitivity for i in range(3)]
            self.gameobject.transform.SetPos(temp)
        elif self.gameobject.scene.keys[pygame.K_d]:
            temp=self.gameobject.transform.GetPos()
            temp=[temp[i]+self.camera.rightvector[i]*self.sensitivity for i in range(3)]
            self.gameobject.transform.SetPos(temp)
        if self.gameobject.scene.keys[pygame.K_q]:
            temp=self.gameobject.transform.GetPos()
            temp=[temp[i]-self.camera.upvector[i]*self.sensitivity for i in range(3)]
            self.gameobject.transform.SetPos(temp)
        elif self.gameobject.scene.keys[pygame.K_e]:
            temp=self.gameobject.transform.GetPos()
            temp=[temp[i]+self.camera.upvector[i]*self.sensitivity for i in range(3)]
            self.gameobject.transform.SetPos(temp)
    
    def HandleInput(self, event):
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1: self.rotate = True
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1: self.rotate = False
        elif event.type == MOUSEMOTION:
            i, j = event.rel
            if self.rotate:
                temp=self.gameobject.transform.GetRotation()
                temp[0]-=j
                temp[1]-=i
                self.gameobject.transform.SetRotation(temp)

    def Update(self):
        self.Move()

Scene1=Scene("./save/Scene1.json")

light1=GameObject("light")
Scene1.AddGameObject(light1)
light1.AddComponent(Light())
light1.transform.SetPos([5,3,-3])

light2=GameObject("light")
Scene1.AddGameObject(light2)
light2.AddComponent(Light())
light2.transform.SetPos([5,3,3])

camera=GameObject("camera")
Scene1.AddGameObject(camera)
camera.AddComponent(Camera())
camera.AddComponent(CameraMove())
camera.GetComponent("CameraMove").GetCamera()
camera.transform.SetPos([0,0,10])



for gameobject in Scene1.GetGameObjectsByComponent("MeshRenderer"):
    gameobject.GetComponent("MeshRenderer").Init()
    
for gameobject in Scene1.GetGameObjectsByComponent("BillboardRenderer"):
    gameobject.GetComponent("BillboardRenderer").Init()

clock = pygame.time.Clock()
while 1:
    clock.tick(30)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) #color/depth/accum?/stencil 버퍼 초기화
    glClearColor(0.5,0.5,0.5,1)
    Scene1.HandleInput()
    Scene1.Update()
    Scene1.Log()
    pygame.display.flip()   