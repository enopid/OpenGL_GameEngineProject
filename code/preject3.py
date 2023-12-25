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

program2 = shader.Program(shader.initprogram2())
program2.InitLight()
program2.InitCamera()
program2.InitMaterial()

program3 = shader.Program(shader.initprogram1())
program3.InitLight()
program3.InitCamera()
program3.InitMaterial()
program3.InitTexture()

lightprogram = shader.Program(shader.initlightprogram())
lightprogram.InitLight()
lightprogram.InitCamera()

PBRtexture = load_texture("./texture/image.png")
texture = load_texture("./texture/lamp.png")

glActiveTexture(GL_TEXTURE0)
glBindTexture(GL_TEXTURE_2D, PBRtexture)

glActiveTexture(GL_TEXTURE1)
glBindTexture(GL_TEXTURE_2D, texture)

object1 = OBJ("./model/testsphere2.obj", swapyz=False)
object2 = OBJ("./model/testsphere1.obj", swapyz=False)
object3 = OBJ("./model/lamp.obj", swapyz=False)
lightobj = OBJ("./model/light.obj", swapyz=False)

glViewport(0, 0, width, height)

glEnable(GL_DEPTH_TEST)

class EditorMode:
    EditormodeIndex=0
    EditorModeList=[]
    currentEditormode=None

    def __init__(self,object,lightobj,program):
        self.obj=object
        self.lightobj=lightobj
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
        self.camerapos = [0,0,0]
        self.rotate = self.move = False
        self.sensitivity=0.2;

        self.metarialproperties=MaterialProperties()
        self.lights=lights()
        self.program=program
    

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
    
    def RenderObjcet(self):
        glUseProgram(self.program.program)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, self.obj.vertices)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, self.obj.normals)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 0, self.obj.texcoords)

        self.view_matrix=view(self.camerapos,self.rightvector,self.upvector,self.viewvector)
        self.model_matrix = np.identity(4, dtype=np.float32)
        mv_matrix = np.dot(self.model_matrix, self.view_matrix)
        
        glUniformMatrix4fv(self.program.MVMatrixlocation, 1, GL_FALSE, mv_matrix)
        glUniformMatrix4fv(self.program.PMatrixlocation, 1, GL_FALSE, self.projection_matrix)

        for i in range(self.lights.lightnum):
            light=self.lights.lightlist[i]
            glUniform3fv(self.program.lightslocation[i][0],1,light.pos)
            glUniform3fv(self.program.lightslocation[i][1],1,light.color)

        for _material in self.metarialproperties.materiallist:
            glUniform1f(_material.location,_material.value)

        glUniform3fv(self.program.cameralocation, 1, self.camerapos)

        glDrawArrays(GL_TRIANGLES, 0, len(self.obj.vertices))
    
    def lightsetting(self):
        glUseProgram(lightprogram.program)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, self.lightobj.vertices)

        self.view_matrix=view(self.camerapos,self.rightvector,self.upvector,self.viewvector)
        for i in range(self.lights.lightnum):
            light=self.lights.lightlist[i]
            
            self.model_matrix=translate(light.pos)
            mv_matrix = np.dot(self.model_matrix, self.view_matrix)
            glUniformMatrix4fv(lightprogram.MVMatrixlocation, 1, GL_FALSE, mv_matrix)
            glUniformMatrix4fv(lightprogram.PMatrixlocation, 1, GL_FALSE, self.projection_matrix)

            glUniform3fv(lightprogram.lightslocation[i][1],1,light.color)

            glDrawArrays(GL_TRIANGLES, 0, len(self.lightobj.vertices))

    def Process(self):
        for e in pygame.event.get():
            self.HandlingInput(e)
        self.Rendering()
        self.lightsetting()
        pygame.display.flip()

    def printstate(self):
        os.system('cls')

    def cameramove(self, keys):
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
            self.camerapos[0]-=self.viewvector[0]*self.sensitivity
            self.camerapos[1]-=self.viewvector[1]*self.sensitivity
            self.camerapos[2]-=self.viewvector[2]*self.sensitivity
        elif keys[pygame.K_s]:
            self.camerapos[0]+=self.viewvector[0]*self.sensitivity
            self.camerapos[1]+=self.viewvector[1]*self.sensitivity
            self.camerapos[2]+=self.viewvector[2]*self.sensitivity
        if keys[pygame.K_a]:
            self.camerapos[0]-=self.rightvector[0]*self.sensitivity
            self.camerapos[1]-=self.rightvector[1]*self.sensitivity
            self.camerapos[2]-=self.rightvector[2]*self.sensitivity
        elif keys[pygame.K_d]:
            self.camerapos[0]+=self.rightvector[0]*self.sensitivity
            self.camerapos[1]+=self.rightvector[1]*self.sensitivity
            self.camerapos[2]+=self.rightvector[2]*self.sensitivity
        if keys[pygame.K_q]:
            self.camerapos[0]+=self.upvector[0]*self.sensitivity
            self.camerapos[1]+=self.upvector[1]*self.sensitivity
            self.camerapos[2]+=self.upvector[2]*self.sensitivity
        elif keys[pygame.K_e]:
            self.camerapos[0]-=self.upvector[0]*self.sensitivity
            self.camerapos[1]-=self.upvector[1]*self.sensitivity
            self.camerapos[2]-=self.upvector[2]*self.sensitivity

    def mousemove(self, keyevent):
        if keyevent.type == MOUSEBUTTONDOWN:
            if keyevent.button == 1: self.rotate = True
            elif keyevent.button == 3: self.move = True
        elif keyevent.type == MOUSEBUTTONUP:
            if keyevent.button == 1: self.rotate = False
        elif keyevent.type == MOUSEMOTION:
            i, j = keyevent.rel
            if self.rotate:
                self.rx += i
                self.ry += j

class ObjectMode1(EditorMode):
    def __init__(self, object, lightobj, program):
        super().__init__(object, lightobj, program)
        self.rx, self.ry = (0,0)
        self.camerapos = [0,0,10]

        self.lights.addlight(light([5.0, 12.0, 5.0],[1,0,0]))
        self.lights.addlight(light([-5.0, 12.0, 5.0],[0,1,0]))
        self.lights.addlight(light([-5.0, 12.0, -5.0],[0,0,1]))
        self.lights.addlight(light([5.0, 12.0, -5.0],[1,1,1]))

        self.metarialproperties.addmeterial(MaterialProperty("roughness",0.01,0.01,0.99).bind(self.program.roughnesslocation))
        self.metarialproperties.addmeterial(MaterialProperty("metalness",0.01,0.01,0.99).bind(self.program.metalnesslocation))
        self.metarialproperties.addmeterial(MaterialProperty("IOR",2.0,0.01,10.0).bind(self.program.IORlocation))


    def HandlingInput(self, keyevent):
        keys=super().HandlingInput(keyevent)
        self.mousemove(keyevent)
        self.cameramove(keys)
        if keyevent.type == KEYDOWN and keyevent.key == pygame.K_SPACE:
            self.metarialproperties.next()
            self.printstate()        
        if keys[pygame.K_k]:
            self.metarialproperties.getcurrentmaterial().setvalue(self.metarialproperties.getcurrentmaterial().value+0.01)
            self.printstate()
        elif keys[pygame.K_j]:
            self.metarialproperties.getcurrentmaterial().setvalue(self.metarialproperties.getcurrentmaterial().value-0.01)
            self.printstate()

    def Rendering(self):
        super().Rendering()
        self.RenderObjcet()
        self.lightsetting()  
        
    def RenderObjcet(self):
        super().RenderObjcet()
        glDrawArrays(GL_TRIANGLES, 0, len(self.obj.vertices))

    def printstate(self):
        super().printstate()
        print("press J/K to adjust material paremeter value")
        print("press space to change material paremeter")
        for _material in self.metarialproperties.materiallist:
            sentence=_material.name + " : " + str(round(_material.value,3))
            if _material==self.metarialproperties.getcurrentmaterial():
                sentence+=" <"
            print(sentence)

class ObjectMode2(EditorMode):
    def __init__(self, object, lightobj, program):
        super().__init__(object, lightobj, program)
        self.rx, self.ry = (180,45)
        self.camerapos = [0,20,-20]
        self.rotate = self.move = False
        
        self.lights.addlight(light([20.0, 50.0, 20.0],[1,0,0]))
        self.lights.addlight(light([-20.0, 50.0, 20.0],[0,0,1]))
        self.lights.addlight(light([-20.0, 50.0, -20.0],[0,1,0]))
        self.lights.addlight(light([20.0, 50.0, -20.0],[1,1,1]))

        self.metarialproperties.addmeterial(MaterialProperty("IOR",2.0,0.01,10.0).bind(self.program.IORlocation))

        self.sensitivity=0.2;

    def HandlingInput(self, keyevent):
        keys=super().HandlingInput(keyevent)
        
        self.cameramove(keys)
        self.mousemove(keyevent)

        if keyevent.type == KEYDOWN and keyevent.key == pygame.K_SPACE:
            self.printstate()        

        if keys[pygame.K_k]:
            _IOR=self.metarialproperties.getmaterial("IOR")
            _IOR.setvalue(_IOR.value+0.01)
            self.printstate()
        elif keys[pygame.K_j]:
            _IOR=self.metarialproperties.getmaterial("IOR")
            _IOR.setvalue(_IOR.value-0.01)
            self.printstate()

    def Rendering(self):
        super().Rendering()
        self.RenderObjcet()
        self.lightsetting()  

    def RenderObjcet(self):
        super().RenderObjcet()

        glDrawArrays(GL_TRIANGLES, 0, len(self.obj.vertices))

    def printstate(self):
        super().printstate()
        _IOR=self.metarialproperties.getmaterial("IOR")
        print("press J/K to adjust IOR value")
        print("current IOR value is {}".format(round(_IOR.value,3)))
        print("metalness : x-axis / rougness : y-axis")
        print("righttop is (0,0) / leftbottom is (1,1)")
        print("metalness : x-axis / rougness : y-axis")
        print("<-metalness-------------")
        sentence="-----------------------"
        for i in "loughness|V":
            print(sentence+i)

class ObjectMode3(EditorMode):
    def __init__(self, object, lightobj, program):
        super().__init__(object, lightobj, program)
        self.rx, self.ry = (180,45)
        self.camerapos = [0,20,-20]
        self.rotate = self.move = False
        
        self.lights.addlight(light([10.0, 10.0, 10.0],[1,1,1]))
        self.lights.addlight(light([-10.0, 0.0, 10.0],[1,1,1]))
        self.lights.addlight(light([-10.0, 10.0, -10.0],[1,1,1]))
        self.lights.addlight(light([10.0, 0.0, -10.0],[1,1,1]))

    def HandlingInput(self, keyevent):
        keys=super().HandlingInput(keyevent)
        self.cameramove(keys)
        self.mousemove(keyevent)
        if keyevent.type == KEYDOWN and keyevent.key == pygame.K_SPACE:
            self.printstate()    

    def Rendering(self):
        super().Rendering()
        self.RenderObjcet()
        self.lightsetting()  

    def RenderObjcet(self):
        super().RenderObjcet()
        glUniform1i(self.program.PBRtexturelocation, 0)
        glUniform1i(self.program.albedotexturelocation, 1)
        glDrawArrays(GL_TRIANGLES, 0, len(self.obj.vertices))

    def printstate(self):
        super().printstate()
        print("lamp model example using diffuse/metalness/roughness map")


ObjectMode1(object1,lightobj,program1)
ObjectMode2(object2,lightobj,program2)
ObjectMode3(object3,lightobj,program3)
        
clock = pygame.time.Clock()
EditorMode.currentEditormode.printstate()
while 1:
    clock.tick(30)
    EditorMode.currentEditormode.Process()