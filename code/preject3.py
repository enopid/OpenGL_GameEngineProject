import sys, pygame, os
from pygame.locals import *
from pygame.constants import *
from OpenGL.GL import *
from OpenGL.GLU import *

from vector import *
from texture import *
import shader
from OBJhandler import *

pygame.init()
viewport = (800,600)
width = viewport[0]
height = viewport[1]
pygame.display.set_mode(viewport, OPENGL | DOUBLEBUF) #openGL,doublebuf 사용?

#init shader
program1 = shader.initprogram1()
program2 = shader.initprogram2()
lightprogram = shader.initlightprogram()
program3 = shader.initprogram3()

PBRtexture = load_texture("./texture/image.png")
texture = load_texture("./texture/lamp.png")
    
object1 = OBJ("./model/testsphere2.obj", swapyz=False)
object2 = OBJ("./model/testsphere1.obj", swapyz=False)
object3 = OBJ("./model/lamp.obj", swapyz=False)
light = OBJ("./model/light.obj", swapyz=False)

uMVMatrix1 = glGetUniformLocation(program1, "uMVMatrix")
uPMatrix1 = glGetUniformLocation(program1, "uPMatrix")
ulights1=[]
for i in range(4):
    temp=[]
    temp.append(glGetUniformLocation(program1, "uLights[{}].position".format(i)))
    temp.append(glGetUniformLocation(program1, "uLights[{}].color".format(i)))
    ulights1.append(temp)
uCameraPos1 = glGetUniformLocation(program1, "uCameraPos")
umetalness1 = glGetUniformLocation(program1, "umetalness")
uroughness1 = glGetUniformLocation(program1, "uroughness")
uIOR1 = glGetUniformLocation(program1, "uIOR")

uMVMatrix2 = glGetUniformLocation(program2, "uMVMatrix")
uPMatrix2 = glGetUniformLocation(program2, "uPMatrix")
ulights2=[]
for i in range(4):
    temp=[]
    temp.append(glGetUniformLocation(program2, "uLights[{}].position".format(i)))
    temp.append(glGetUniformLocation(program2, "uLights[{}].color".format(i)))
    ulights2.append(temp)
uCameraPos2 = glGetUniformLocation(program2, "uCameraPos")
uIOR2 = glGetUniformLocation(program2, "IOR")

sTexture3 = glGetUniformLocation(program3, "sTexture")
sPBRTexture3 = glGetUniformLocation(program3, "sTexture")
uMVMatrix3 = glGetUniformLocation(program3, "uMVMatrix")
uPMatrix3 = glGetUniformLocation(program3, "uPMatrix")
ulights3=[]
for i in range(4):
    temp=[]
    temp.append(glGetUniformLocation(program3, "uLights[{}].position".format(i)))
    temp.append(glGetUniformLocation(program3, "uLights[{}].color".format(i)))
    ulights3.append(temp)
uCameraPos3 = glGetUniformLocation(program3, "uCameraPos")

uMVMatrix_l = glGetUniformLocation(lightprogram, "uMVMatrix")
uPMatrix_l = glGetUniformLocation(lightprogram, "uPMatrix")
uLightColor_l = glGetUniformLocation(lightprogram, "uLightColor")

glActiveTexture(GL_TEXTURE0)
glBindTexture(GL_TEXTURE_2D, PBRtexture)
glUniform1i(sPBRTexture3, 0)

glActiveTexture(GL_TEXTURE1)
glBindTexture(GL_TEXTURE_2D, texture)
glUniform1i(sTexture3, 1)


glViewport(0, 0, width, height)

glEnable(GL_DEPTH_TEST)


class EditorMode:
    EditormodeIndex=0
    EditorModeList=[]
    currentEditormode=None

    def __init__(self,object,light):
        self.obj=object
        self.light=light
        EditorMode.EditorModeList.append(self)
        if EditorMode.currentEditormode==None:
            EditorMode.currentEditormode=self

        self.projection_matrix = perspective(45, width/height, 0.1, 500)
        self.model_matrix = np.identity(4, dtype=np.float32)
        self.view_matrix = np.identity(4, dtype=np.float32)
        self.view_matrix[-1, :-1] = (0, 0, 10)
        self.viewvector=[0,0,1]
        self.upvector=[0,1,0]
        self.rightvector=[1,0,0]
        self.xpos = 0
        self.ypos = 0
        self.zpos = 10

        self.metarialproperty=[0.01,0.01,2.0]
        self.metarialpropertymin=[0.01,0.01,0.01]
        self.metarialpropertymax=[0.99,0.99,10.0]
        self.metarialpropertyindex=0

        self.light_pos = []
        self.light_color = []
        self.light_pos.append(np.array([0.0, 0.0, 0.0]))
        self.light_color.append(np.array([0, 1, 1]))

        self.light_pos.append(np.array([0.0, 0.0, 0.0]))
        self.light_color.append(np.array([0, 1, 1]))

        self.light_pos.append(np.array([0.0, 0.0, 0.0]))
        self.light_color.append(np.array([0, 1, 1]))

        self.light_pos.append(np.array([0.0, 0.0, 0.0]))
        self.light_color.append(np.array([0, 1, 1]))

    def HandlingInput(self,e):
        keys = pygame.key.get_pressed()
        if e.type == QUIT:
            sys.exit()
        elif e.type == KEYDOWN and e.key == K_ESCAPE:
            sys.exit()

        if e.type == KEYDOWN and e.key == K_TAB:
            EditorMode.EditormodeIndex+=1
            EditorMode.currentEditormode=EditorMode.EditorModeList[EditorMode.EditormodeIndex%len(EditorMode.EditorModeList)]
            EditorMode.currentEditormode.printstate()
        return keys

    def Rendering(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) #color/depth/accum?/stencil 버퍼 초기화
        glClearColor(0.5,0.5,0.5,1)

    def Camerasetting(self):
        1
    
    def RenderObjcet(self):
        glUseProgram(program1)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, self.obj.vertices)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, self.obj.normals)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 0, self.obj.texcoords)

        self.view_matrix=view((self.xpos,self.ypos,self.zpos),self.rightvector,self.upvector,self.viewvector)
        self.model_matrix = np.identity(4, dtype=np.float32)
        mv_matrix = np.dot(self.model_matrix, self.view_matrix)
        glUniformMatrix4fv(uMVMatrix1, 1, GL_FALSE, mv_matrix)
        glUniformMatrix4fv(uPMatrix1, 1, GL_FALSE, self.projection_matrix)

        for i in range(4):
            glUniform3f(ulights1[i][0],self.light_pos[i][0],self.light_pos[i][1],self.light_pos[i][2])
            glUniform3f(ulights1[i][1],self.light_color[i][0],self.light_color[i][1],self.light_color[i][2])

        glUniform3f(uCameraPos1,self.xpos,self.ypos,self.zpos)

        glUniform1f(umetalness1,self.metarialproperty[0])
        glUniform1f(uroughness1,self.metarialproperty[1])
        glUniform1f(uIOR1,self.metarialproperty[2])

        glDrawArrays(GL_TRIANGLES, 0, len(self.obj.vertices))
    
    def lightsetting(self):
        glUseProgram(lightprogram)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, self.light.vertices)

        self.view_matrix=view((self.xpos,self.ypos,self.zpos),self.rightvector,self.upvector,self.viewvector)
        for i in range(4):
            self.model_matrix=translate(self.light_pos[i])
            mv_matrix = np.dot(self.model_matrix, self.view_matrix)
            glUniformMatrix4fv(uMVMatrix_l, 1, GL_FALSE, mv_matrix)
            glUniformMatrix4fv(uPMatrix_l, 1, GL_FALSE, self.projection_matrix)

            glUniform3f(uLightColor_l,self.light_color[i][0],self.light_color[i][1],self.light_color[i][2])

            glDrawArrays(GL_TRIANGLES, 0, len(self.light.vertices))

    def Process(self):
        for e in pygame.event.get():
            self.HandlingInput(e)
        self.Rendering()
        self.lightsetting()
        pygame.display.flip()

    def printstate(self):
        os.system('cls')

class ObjectMode1(EditorMode):
    def __init__(self, object, light):
        super().__init__(object, light)
        self.rx, self.ry = (0,0)
        self.tx, self.ty = (0,0)
        self.xpos = 0
        self.ypos = 0
        self.zpos = 10
        self.rotate = self.move = False

        self.light_pos = []
        self.light_color = []
        self.light_pos.append(np.array([5.0, 12.0, 5.0]))
        self.light_color.append(np.array([1, 1, 1]))

        self.light_pos.append(np.array([-5.0, 12.0, 5.0]))
        self.light_color.append(np.array([1, 1, 1]))

        self.light_pos.append(np.array([-5.0, 12.0, -5.0]))
        self.light_color.append(np.array([1, 1, 1]))
        
        self.light_pos.append(np.array([5.0, 12.0, -5.0]))
        self.light_color.append(np.array([1, 1, 1]))

        self.sensitivity=0.2;

    def HandlingInput(self, e):
        keys=super().HandlingInput(e)
        self.viewvector=[0,0,1]
        self.upvector=[0,1,0]
        self.rightvector=[1,0,0]
        self.viewvector=rotation_X(-self.ry,self.viewvector)
        self.viewvector=rotation_Y(-self.rx,self.viewvector)
        self.upvector=rotation_X(-self.ry,self.upvector)
        self.upvector=rotation_Y(-self.rx,self.upvector)
        self.rightvector=rotation_X(-self.ry,self.rightvector)
        self.rightvector=rotation_Y(-self.rx,self.rightvector)
        if keys[pygame.K_w]:
            self.xpos-=self.viewvector[0]*self.sensitivity
            self.ypos-=self.viewvector[1]*self.sensitivity
            self.zpos-=self.viewvector[2]*self.sensitivity
        elif keys[pygame.K_s]:
            self.xpos+=self.viewvector[0]*self.sensitivity
            self.ypos+=self.viewvector[1]*self.sensitivity
            self.zpos+=self.viewvector[2]*self.sensitivity
        if keys[pygame.K_a]:
            self.xpos-=self.rightvector[0]*self.sensitivity
            self.ypos-=self.rightvector[1]*self.sensitivity
            self.zpos-=self.rightvector[2]*self.sensitivity
        elif keys[pygame.K_d]:
            self.xpos+=self.rightvector[0]*self.sensitivity
            self.ypos+=self.rightvector[1]*self.sensitivity
            self.zpos+=self.rightvector[2]*self.sensitivity
        if keys[pygame.K_q]:
            self.xpos+=self.upvector[0]*self.sensitivity
            self.ypos+=self.upvector[1]*self.sensitivity
            self.zpos+=self.upvector[2]*self.sensitivity
        elif keys[pygame.K_e]:
            self.xpos-=self.upvector[0]*self.sensitivity
            self.ypos-=self.upvector[1]*self.sensitivity
            self.zpos-=self.upvector[2]*self.sensitivity
        if e.type == KEYDOWN and e.key == pygame.K_SPACE:
            self.metarialpropertyindex=(self.metarialpropertyindex+1)%3
            self.printstate()        
        if keys[pygame.K_k]:
            self.metarialproperty[self.metarialpropertyindex]= (self.metarialproperty[self.metarialpropertyindex]+0.01) if (self.metarialproperty[self.metarialpropertyindex]<self.metarialpropertymax[self.metarialpropertyindex]) else self.metarialpropertymax[self.metarialpropertyindex]
            self.printstate()
        elif keys[pygame.K_j]:
            self.metarialproperty[self.metarialpropertyindex]= (self.metarialproperty[self.metarialpropertyindex]-0.01) if (self.metarialproperty[self.metarialpropertyindex]>self.metarialpropertymin[self.metarialpropertyindex]) else self.metarialpropertymin[self.metarialpropertyindex]
            self.printstate()
        

        if e.type == MOUSEBUTTONDOWN:
            if e.button == 1: self.rotate = True
            elif e.button == 3: self.move = True
        elif e.type == MOUSEBUTTONUP:
            if e.button == 1: self.rotate = False
        elif e.type == MOUSEMOTION:
            i, j = e.rel
            if self.rotate:
                self.rx += i
                self.ry += j

    def Rendering(self):
        super().Rendering()
        self.Camerasetting()
        self.RenderObjcet()
        self.lightsetting()  

    def Camerasetting(self):
        super().Camerasetting()

    def RenderObjcet(self):
        super().RenderObjcet()

    def lightsetting(self):
        super().lightsetting()

    def printstate(self):
        super().printstate()
        print("press J/K to adjust material paremeter value")
        print("press space to change material paremeter")
        test=["metalness", "roughness", "IOR"]
        for i in range(3):
            sentence=test[i] + " : " + str(round(self.metarialproperty[i],3))
            if i==self.metarialpropertyindex:
                sentence+=" <"
            print(sentence)

class ObjectMode2(EditorMode):
    def __init__(self, object, light):
        super().__init__(object, light)
        self.rx, self.ry = (180,45)
        self.xpos = 0
        self.ypos = 20
        self.zpos = -20
        self.rotate = self.move = False

        self.light_pos = []
        self.light_color = []
        self.light_pos.append(np.array([20.0, 50.0, 20.0]))
        self.light_color.append(np.array([1, 1, 1]))

        self.light_pos.append(np.array([-20.0, 50.0, 20.0]))
        self.light_color.append(np.array([1, 1, 1]))

        self.light_pos.append(np.array([-20.0, 50.0, -20.0]))
        self.light_color.append(np.array([1, 1, 1]))
        
        self.light_pos.append(np.array([20.0, 50.0, -20.0]))
        self.light_color.append(np.array([1, 1, 1]))

        self.sensitivity=0.2;
        self.IOR=2.0;

    def HandlingInput(self, e):
        keys=super().HandlingInput(e)
        self.viewvector=[0,0,1]
        self.upvector=[0,1,0]
        self.rightvector=[1,0,0]
        self.viewvector=rotation_X(-self.ry,self.viewvector)
        self.viewvector=rotation_Y(-self.rx,self.viewvector)
        self.upvector=rotation_X(-self.ry,self.upvector)
        self.upvector=rotation_Y(-self.rx,self.upvector)
        self.rightvector=rotation_X(-self.ry,self.rightvector)
        self.rightvector=rotation_Y(-self.rx,self.rightvector)
        if keys[pygame.K_w]:
            self.xpos-=self.viewvector[0]*self.sensitivity
            self.ypos-=self.viewvector[1]*self.sensitivity
            self.zpos-=self.viewvector[2]*self.sensitivity
        elif keys[pygame.K_s]:
            self.xpos+=self.viewvector[0]*self.sensitivity
            self.ypos+=self.viewvector[1]*self.sensitivity
            self.zpos+=self.viewvector[2]*self.sensitivity
        if keys[pygame.K_a]:
            self.xpos-=self.rightvector[0]*self.sensitivity
            self.ypos-=self.rightvector[1]*self.sensitivity
            self.zpos-=self.rightvector[2]*self.sensitivity
        elif keys[pygame.K_d]:
            self.xpos+=self.rightvector[0]*self.sensitivity
            self.ypos+=self.rightvector[1]*self.sensitivity
            self.zpos+=self.rightvector[2]*self.sensitivity
        if keys[pygame.K_q]:
            self.xpos+=self.upvector[0]*self.sensitivity
            self.ypos+=self.upvector[1]*self.sensitivity
            self.zpos+=self.upvector[2]*self.sensitivity
        elif keys[pygame.K_e]:
            self.xpos-=self.upvector[0]*self.sensitivity
            self.ypos-=self.upvector[1]*self.sensitivity
            self.zpos-=self.upvector[2]*self.sensitivity

        if e.type == KEYDOWN and e.key == pygame.K_SPACE:
            self.printstate()        

        if keys[pygame.K_k]:
            self.IOR+=0.01
            self.IOR=max(min(self.IOR,10.0),0.01)
            self.printstate()
        elif keys[pygame.K_j]:
            self.IOR-=0.01
            self.IOR=max(min(self.IOR,10.0),0.01)
            self.printstate()
        

        if e.type == MOUSEBUTTONDOWN:
            if e.button == 1: self.rotate = True
            elif e.button == 3: self.move = True
        elif e.type == MOUSEBUTTONUP:
            if e.button == 1: self.rotate = False
        elif e.type == MOUSEMOTION:
            i, j = e.rel
            if self.rotate:
                self.rx += i
                self.ry += j

    def Rendering(self):
        super().Rendering()
        self.Camerasetting()
        self.RenderObjcet()
        self.lightsetting()  

    def Camerasetting(self):
        super().Camerasetting()

    def RenderObjcet(self):
        glUseProgram(program2)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, self.obj.vertices)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, self.obj.normals)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 0, self.obj.texcoords)

        self.view_matrix=view((self.xpos,self.ypos,self.zpos),self.rightvector,self.upvector,self.viewvector)
        self.model_matrix = np.identity(4, dtype=np.float32)
        mv_matrix = np.dot(self.model_matrix, self.view_matrix)
        glUniformMatrix4fv(uMVMatrix2, 1, GL_FALSE, mv_matrix)
        glUniformMatrix4fv(uPMatrix2, 1, GL_FALSE, self.projection_matrix)

        for i in range(4):
            glUniform3f(ulights2[i][0],self.light_pos[i][0],self.light_pos[i][1],self.light_pos[i][2])
            glUniform3f(ulights2[i][1],self.light_color[i][0],self.light_color[i][1],self.light_color[i][2])

        glUniform3f(uCameraPos2,self.xpos,self.ypos,self.zpos)
        glUniform1f(uIOR2,self.IOR)

        glDrawArrays(GL_TRIANGLES, 0, len(self.obj.vertices))

    def lightsetting(self):
        super().lightsetting()

    def printstate(self):
        super().printstate()
        print("press J/K to adjust IOR value")
        print("current IOR value is {}".format(round(self.IOR,3)))
        print("metalness : x-axis / rougness : y-axis")
        print("righttop is (0,0) / leftbottom is (1,1)")
        print("metalness : x-axis / rougness : y-axis")
        print("<-metalness-------------")
        sentence="-----------------------"
        for i in "loughness|V":
            print(sentence+i)

class ObjectMode3(EditorMode):
    def __init__(self, object, light):
        super().__init__(object, light)
        self.rx, self.ry = (180,45)
        self.xpos = 0
        self.ypos = 20
        self.zpos = -20
        self.rotate = self.move = False

        self.light_pos = []
        self.light_color = []
        self.light_pos.append(np.array([10.0, 10.0, 10.0]))
        self.light_color.append(np.array([1, 1, 1]))

        self.light_pos.append(np.array([-10.0, 0.0, 10.0]))
        self.light_color.append(np.array([1, 1, 1]))

        self.light_pos.append(np.array([-10.0, 10.0, -10.0]))
        self.light_color.append(np.array([1, 1, 1]))
        
        self.light_pos.append(np.array([10.0, 0.0, -10.0]))
        self.light_color.append(np.array([1, 1, 1]))

        self.sensitivity=0.2;

    def HandlingInput(self, e):
        keys=super().HandlingInput(e)
        self.viewvector=[0,0,1]
        self.upvector=[0,1,0]
        self.rightvector=[1,0,0]
        self.viewvector=rotation_X(-self.ry,self.viewvector)
        self.viewvector=rotation_Y(-self.rx,self.viewvector)
        self.upvector=rotation_X(-self.ry,self.upvector)
        self.upvector=rotation_Y(-self.rx,self.upvector)
        self.rightvector=rotation_X(-self.ry,self.rightvector)
        self.rightvector=rotation_Y(-self.rx,self.rightvector)
        if keys[pygame.K_w]:
            self.xpos-=self.viewvector[0]*self.sensitivity
            self.ypos-=self.viewvector[1]*self.sensitivity
            self.zpos-=self.viewvector[2]*self.sensitivity
        elif keys[pygame.K_s]:
            self.xpos+=self.viewvector[0]*self.sensitivity
            self.ypos+=self.viewvector[1]*self.sensitivity
            self.zpos+=self.viewvector[2]*self.sensitivity
        if keys[pygame.K_a]:
            self.xpos-=self.rightvector[0]*self.sensitivity
            self.ypos-=self.rightvector[1]*self.sensitivity
            self.zpos-=self.rightvector[2]*self.sensitivity
        elif keys[pygame.K_d]:
            self.xpos+=self.rightvector[0]*self.sensitivity
            self.ypos+=self.rightvector[1]*self.sensitivity
            self.zpos+=self.rightvector[2]*self.sensitivity
        if keys[pygame.K_q]:
            self.xpos+=self.upvector[0]*self.sensitivity
            self.ypos+=self.upvector[1]*self.sensitivity
            self.zpos+=self.upvector[2]*self.sensitivity
        elif keys[pygame.K_e]:
            self.xpos-=self.upvector[0]*self.sensitivity
            self.ypos-=self.upvector[1]*self.sensitivity
            self.zpos-=self.upvector[2]*self.sensitivity

        if e.type == KEYDOWN and e.key == pygame.K_SPACE:
            self.printstate()    
        

        if e.type == MOUSEBUTTONDOWN:
            if e.button == 1: self.rotate = True
            elif e.button == 3: self.move = True
        elif e.type == MOUSEBUTTONUP:
            if e.button == 1: self.rotate = False
        elif e.type == MOUSEMOTION:
            i, j = e.rel
            if self.rotate:
                self.rx += i
                self.ry += j

    def Rendering(self):
        super().Rendering()
        self.Camerasetting()
        self.RenderObjcet()
        self.lightsetting()  

    def Camerasetting(self):
        super().Camerasetting()

    def RenderObjcet(self):
        glUseProgram(program3)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, self.obj.vertices)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, self.obj.normals)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 0, self.obj.texcoords)

        self.view_matrix=view((self.xpos,self.ypos,self.zpos),self.rightvector,self.upvector,self.viewvector)
        self.model_matrix = np.identity(4, dtype=np.float32)
        mv_matrix = np.dot(self.model_matrix, self.view_matrix)
        glUniformMatrix4fv(uMVMatrix3, 1, GL_FALSE, mv_matrix)
        glUniformMatrix4fv(uPMatrix3, 1, GL_FALSE, self.projection_matrix)

        for i in range(4):
            glUniform3f(ulights3[i][0],self.light_pos[i][0],self.light_pos[i][1],self.light_pos[i][2])
            glUniform3f(ulights3[i][1],self.light_color[i][0],self.light_color[i][1],self.light_color[i][2])

        glUniform3f(uCameraPos3,self.xpos,self.ypos,self.zpos)

        glDrawArrays(GL_TRIANGLES, 0, len(self.obj.vertices))

    def lightsetting(self):
        super().lightsetting()

    def printstate(self):
        super().printstate()
        print("lamp model example using diffuse/metalness/roughness map")

ObjectMode1(object1,light)
ObjectMode2(object2,light)
ObjectMode3(object3,light)
        
clock = pygame.time.Clock()
EditorMode.currentEditormode.printstate()
while 1:
    clock.tick(30)
    EditorMode.currentEditormode.Process()