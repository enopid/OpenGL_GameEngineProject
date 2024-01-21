import sys, pygame, os
from pygame.locals import *
from pygame.constants import *
from OpenGL.GL import *
from OpenGL.GLU import *

from vector import *
from light import *
from material import *
from texture import *
import shader
from OBJhandler import *

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
    
    def Update(self):
        for object in self.objectlist:
            object.update()
    
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

class GameObject:
    def __init__(self):
        self.components=[]
        self.AddComponent(Transform())
        self.Transform=self.components[0]
        self.scene=None
    
    def Update(self):
        for component in self.components:
            component.Update()
    
    def AddComponent(self, component):
        component.gameobject=self
        self.components.append(component)
    
    def GetComponent(self,name):
        for component in self.components:
            if type(component).__name__ == name:
                return component
        return False

class Component:
    def __init__(self):
        self.gameobject=None
    
    def Update(self):
        pass

class Transform(Component):
    def __init__(self):
        self.__scale=[1,1,1]
        self.__rotation=[0,0,0]
        self.__translation=[0,0,0]
    
    def GetPos(self):
        return self.__translation

    def GetModelMatrix(self):
        return np.array([
            [       self.__scale[0],                     0,                     0,  0],
            [                     0,       self.__scale[1],                     0,  0],
            [                     0,                     0,       self.__scale[2],  0],
            [ self.__translation[0], self.__translation[1], self.__translation[2],  1]
        ])

class Mesh(Component):
    def __init__(self):
        self.mesh=None
    
    def SetMesh(self,obj):
        self.mesh=obj

class MeshRenderer(Component):
    def __init__(self):
        self.mesh=None
        self.camera=None
        self.program=None
        self.lights=[]
    
    def GetLights(self):
        self.lights=self.gameobject.scene.GetGameObjectsByComponent("Light")
        glUseProgram(self.program.program)
        for i in range(len(self.lights)):
            light=self.lights[i].GetComponent("Light")
            glUniform3fv(self.program.lightslocation[i][0],1, self.lights[i].transform.GetPos())
            glUniform3fv(self.program.lightslocation[i][1],1, light.color)

    def GetMesh(self):
        if temp:=self.gameobject.GetComponent("Mesh"):
            self.mesh=temp

    def GetCamera(self):
        if temp:=self.gameobject.GetComponent("Camera"):
            self.camera=temp

        glUniform3fv(self.program.cameralocation, 1, self.camera)
    
    def SetProgram(self,program):
        self.program=program

    def Update(self):
        glUseProgram(self.program.program)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, self.obj.vertices)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, self.obj.normals)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 0, self.obj.texcoords)

        view_matrix = self.camera.GetViewMatrix()
        projection_matrix = self.camera.GetProjectionMatrix()
        model_matrix = self.gameobject.transform.GetModelMatrix()
        mv_matrix = np.dot(model_matrix, view_matrix)
        
        glUniformMatrix4fv(self.program.MVMatrixlocation, 1, GL_FALSE, mv_matrix)
        glUniformMatrix4fv(self.program.PMatrixlocation, 1, GL_FALSE, projection_matrix)

        for _material in self.metarialproperties.materiallist:
            glUniform1f(_material.location,_material.value)

        glUniform3fv(self.program.cameralocation, 1, self.camera.pos)

        glDrawArrays(GL_TRIANGLES, 0, len(self.obj.vertices))

class Light(Component):
    def __init__(self):
        self.type=None
        self.color=(1,1,1)
        self.intensity=1

class Camera(Component):
    def __init__(self):
        self.type=None
    
    def GetViewMatrix(self):
        return view(self.camerapos,self.rightvector,self.upvector,self.viewvector)

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

class Material(Component):
    def __init__(self):
        self.type=None

Scene1=Scene()
box=GameObject()
box.AddComponent(Mesh())
box.GetComponent("Mesh").SetMesh(object1)
box.AddComponent(MeshRenderer())
box.GetComponent("MeshRenderer").SetProgram(program1)
light1=GameObject()
light1.AddComponent(Light())
camera=GameObject()
camera.AddComponent(Camera())
Scene1.AddGameObject(box)
Scene1.AddGameObject(light1)
Scene1.AddGameObject(camera)
        
clock = pygame.time.Clock()
while 1:
    clock.tick(30)
    Scene1.Update()