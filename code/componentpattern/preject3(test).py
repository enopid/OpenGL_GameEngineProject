import sys, pygame, os
from pygame.locals import *
from pygame.constants import *
from OpenGL.GL import *
from OpenGL.GLU import *

from vector import *
from material import *
from texture import *
import shader
from OBJhandler import *

from PIL import Image

pygame.init()
viewport = (800,600)
width = viewport[0]
height = viewport[1]
pygame.display.set_mode(viewport, OPENGL | DOUBLEBUF)

#init shader
program1 = shader.Program(shader.initprogram1())
program1.InitLight()
program1.InitCamera()
program1.InitMaterial()
program1.InitSkyBox()

program2 = shader.Program(shader.initprogram2())
program2.InitLight()
program2.InitCamera()
program2.InitMaterial()

program3 = shader.Program(shader.initprogram1())
program3.InitLight()
program3.InitCamera()
program3.InitMaterial()
program3.InitTexture()

program4 = shader.Program(shader.initprogram3())
program4.InitLight()
program4.InitCamera()
program4.InitMaterial()
program4.InitSkyBox()

lightprogram = shader.Program(shader.initlightprogram())
lightprogram.InitLight()
lightprogram.InitCamera()

skyboxprogram = shader.Program(shader.initSkyboxprogram())
skyboxprogram.InitSkyBox()
skyboxprogram.InitCamera()

PBRtexture = load_texture("./texture/image.png")
texture = load_texture("./texture/lamp.png")
skybox = load_skycube_texture("./skybox")

glActiveTexture(GL_TEXTURE0)
glBindTexture(GL_TEXTURE_2D, PBRtexture)

glActiveTexture(GL_TEXTURE1)
glBindTexture(GL_TEXTURE_2D, texture)

glBindTexture(GL_TEXTURE_CUBE_MAP, skybox)

object1 = OBJ("./model/testsphere2.obj", swapyz=False)
object2 = OBJ("./model/testsphere1.obj", swapyz=False)
object3 = OBJ("./model/lamp.obj", swapyz=False)
skyboxobj = OBJ("./model/cube.obj", swapyz=False)
lightobj = OBJ("./model/light.obj", swapyz=False)

glViewport(0, 0, width, height)

glEnable(GL_DEPTH_TEST)
glEnable(GL_DEBUG_OUTPUT)

skyboxvertices=[]

class Scene:
    def __init__(self):
        self.objectlist=[]
        self.keys=None
        self.curLog=None
    
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
    
    def Update(self):
        for component in self.components:
            component.Update()
    
    def HandleInput(self,event):
        for component in self.components:
            component.HandleInput(event)
    
    def AddComponent(self, component):
        component.gameobject=self
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
    def __init__(self):
        self.gameobject=None

    def Init(self):
        pass
    
    def Update(self):
        pass

    def HandleInput(self,event):
        pass
    
    def Log(self):
        return [self.__class__.__name__]

class Transform(Component):
    def __init__(self):
        self.__scale=[1,1,1]
        self.__rotation=[0,0,0]
        self.__translation=[0,0,0]
    
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
        return np.dot(self.GetTranslationMatrix(),np.dot(self.GetRotateMatrix(),self.GetScaleMatrix()))
    
    def Log(self):
        temp=super().Log()
        temp.append("---"+"pos : {:0.1f}, {:0.1f}, {:0.1f}".format(self.__translation[0],self.__translation[1],self.__translation[2]))
        temp.append("---"+"scale : {:0.1f}, {:0.1f}, {:0.1f}".format(self.__scale[0],self.__scale[1],self.__scale[2]))
        temp.append("---"+"rotation : {:0.1f}, {:0.1f}, {:0.1f}".format(self.__rotation[0],self.__rotation[1],self.__rotation[2]))
        return temp

class Mesh(Component):
    def __init__(self):
        self.mesh=None
    
    def SetMesh(self,obj):
        self.mesh=obj

    def Log(self):
        temp=super().Log()
        temp.append("---"+"mesh : {}".format(str(self.mesh)))
        return temp

class MeshRenderer(Component):
    def __init__(self):
        self.mesh=None
        self.camera=None
        self.program=None
        self.lights=[]

    def Init(self):
        self.GetMesh()
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

    def GetMeterial(self):
        if temp:=self.gameobject.scene.GetGameObjectByComponent("Material").GetComponent("Material"):
            self.camera=temp
    
    def SetProgram(self,program):
        self.program=program

    def Update(self):
        glUseProgram(self.program.program)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, self.mesh.mesh.vertices)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, self.mesh.mesh.normals)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 0, self.mesh.mesh.texcoords)

        view_matrix = self.camera.GetViewMatrix()
        projection_matrix = self.camera.GetProjectionMatrix()
        model_matrix = self.gameobject.transform.GetModelMatrix()
        mv_matrix = np.dot(model_matrix, view_matrix)
        
        self.lights=self.gameobject.scene.GetGameObjectsByComponent("Light")
        for i in range(len(self.lights)):
            light=self.lights[i].GetComponent("Light")
            glUniform3fv(self.program.lightslocation[i][0],1, self.lights[i].transform.GetPos())
            glUniform3fv(self.program.lightslocation[i][1],1, light.color)

        glUniformMatrix4fv(self.program.MVMatrixlocation, 1, GL_FALSE, mv_matrix)
        glUniformMatrix4fv(self.program.PMatrixlocation, 1, GL_FALSE, projection_matrix)

        glUniform3fv(self.program.cameralocation, 1, self.camera.gameobject.transform.GetPos())

        glDrawArrays(GL_TRIANGLES, 0, len(self.mesh.mesh.vertices))

class Light(Component):
    def __init__(self):
        self.type=None
        self.color=(1,1,1)
        self.intensity=1

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
    materialproperties={
        "albedo":["uUseAlbedotexture", 0, "sTexture", "uAlbedo"],
        "metalness":["uUsePBRtexture", 1, "sPBRTexture", "umetalness"],
        "roughness":["uUsePBRtexture", 2, "sPBRTexture", "uroughness"],
        "normalmap":[],
    }

    def __init__(self):
        self.type=0
        self.Albedo=None
        self.Metalness=None
        self.roughness=None
        self.normalMap=None

        self.metalnesslocation = None
        self.roughnesslocation = None
        self.IORlocation = None

        self.albedotexturelocation = None
        self.PBRtexturelocation = None

        self.uUsePBRtexture = None
        self.uUseAlbedotexture = None

        self.program = None

    def SetProgram(self,program):
        self.program=program
    
    def LoadTexture(self,filename):
        img = Image.open(filename, 'r').convert("RGB")
        img_data = np.array(img, dtype=np.uint8)
        w, h = img.size

        texture = glGenTextures(1)

        glBindTexture(GL_TEXTURE_2D, texture)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, w, h, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)

        return texture
    
    def BindTexture(self, name,path):
        texture = self.LoadTexture(path)
        glActiveTexture(GL_TEXTURE0+Material.materialproperties[name][1])
        glBindTexture(GL_TEXTURE_2D, texture)
    
    def SetTexture(self, name, path):
        glUseProgram(self.program.program)
        self.BindTexture(name, path)
        buselocation=Material.materialproperties[name][0]
        location=Material.materialproperties[name][2]
        glUniform1i(glGetUniformLocation(self.program.program, buselocation), 1)
        glUniform1i(glGetUniformLocation(self.program.program, location), Material.materialproperties[name][1])

    def SetValue(self, name, value):
        glUseProgram(self.program.program)
        buselocation=Material.materialproperties[name][0]
        location=Material.materialproperties[name][3]
        glUniform1i(glGetUniformLocation(self.program.program, buselocation), 0)
        if isinstance(value,float):
            value=[value,value,value]
        glUniform3fv(glGetUniformLocation(self.program.program, location), 1, value)

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

Scene1=Scene()

box=GameObject("sphere")
box.AddComponent(Mesh())
box.GetComponent("Mesh").SetMesh(object1)
box.AddComponent(MeshRenderer())
box.GetComponent("MeshRenderer").SetProgram(program1)
box.AddComponent(Material())
box.GetComponent("Material").SetProgram(program1)
box.GetComponent("Material").SetValue("albedo", (0.5,0.6,0.7))
box.GetComponent("Material").SetValue("metalness", 0.5)
box.GetComponent("Material").SetValue("roughness", 0.5)


light1=GameObject("light")
light1.AddComponent(Light())
light1.transform.SetPos([0,10,0])

camera=GameObject("camera")
camera.AddComponent(Camera())
camera.AddComponent(CameraMove())
camera.GetComponent("CameraMove").GetCamera()
camera.transform.SetPos([0,0,10])

Scene1.AddGameObject(box)
Scene1.AddGameObject(light1)
Scene1.AddGameObject(camera)

box.GetComponent("MeshRenderer").Init()

clock = pygame.time.Clock()
while 1:
    clock.tick(30)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) #color/depth/accum?/stencil 버퍼 초기화
    glClearColor(0.5,0.5,0.5,1)
    Scene1.HandleInput()
    Scene1.Update()
    Scene1.Log()
    pygame.display.flip()   