from OpenGL.GL import *

vertex_shader_source = """
    #version 330 core
    uniform mat4 uMVMatrix;
    uniform mat4 uPMatrix;
                                       
    layout (location=0) in vec3 aVertex; 
    layout (location=1) in vec3 aNormal;
    layout (location=2) in vec2 aTexCoord;
    
    varying vec2 vTexCoord;                        
    varying vec3 vNormal;  
    varying vec3 vVertexPos; 
                                         
    void main(){
       vTexCoord = aTexCoord;
       vVertexPos=aVertex;
       vNormal=aNormal;                
                                       
       gl_Position = (uPMatrix * uMVMatrix)  * vec4(aVertex, 1.0);
    }
    """

fragment_shader_source1 ="""
    #version 330 core
    #define NUM_LIGHTS 4  

    struct Light {    
        vec3 position;
        vec3 color;
    };  

    uniform Light uLights[NUM_LIGHTS];
                                         
    uniform float umetalness;
    uniform float uroughness;                      
    uniform float uIOR;    

    uniform int uUsePBRtexture;                
    uniform int uUseAlbedotexture;
    uniform int uUseSkybox;
                                       
    uniform vec3 uLightPos;
    uniform vec3 uLightColor;
    uniform vec3 uCameraPos;
                  
    uniform sampler2D sTexture;
    uniform sampler2D sPBRTexture;
    uniform samplerCube sSkyboxTexture; 

    varying vec2 vTexCoord;             
    varying vec3 vNormal;    
    varying vec3 vVertexPos;

    float metalness;
    float roughness;                      
    float IOR;

    float test;

    float pi = 3.1415926535897932384626433832795;               
    float lightintensity = 10.0;   
    vec4 skyboxcolor;
    vec3 basecolor = vec3(0.9529, 0.7882, 0.4078);             
    float ra=0.1;  
    
    void init(){                        
        if (uUseAlbedotexture==1){
            vec4 color = texture2D(sTexture, vTexCoord);    
            basecolor=vec3(color[0],color[1],color[2]); 
        }

        if (uUsePBRtexture==1){
            vec4 PBRValue = texture2D(sPBRTexture, vTexCoord); 
            roughness = PBRValue[0];           
            metalness = PBRValue[1];
            IOR = PBRValue[2];
        }
        else{
            metalness = umetalness;
            roughness = uroughness;
            IOR = uIOR;
        }    
    }

    float cooktorrance(float hov,float noh,float nov,float nol){     
        float F0=pow((1.0-IOR)/(1.0+IOR),2);        
        float F=F0+(1.0-F0)*pow((1-hov),5);
                                            
        float D=pow(roughness,4)/(pi*pow((pow(noh,2)*(pow(roughness,4)-1.0)+1.0),2));
                                            
        float k=pow(roughness+1.0,2)/8.0;                                       
        float G1=nol/(nol*(1.0-k)+k);         
        float G2=nov/(nov*(1.0-k)+k);
        float G=G1*G2;
                        
        return F*D*G/(4.0*nol*nov); 
    }

    vec3 lambertian(float hov,float noh,float nov,float nol){                 
        float dr = (1.0-metalness);

        return dr*basecolor/pi;
    }

    vec3 PBR(vec3 lightColor, vec3 lightPos){
        vec3 vLight=normalize(lightPos - vVertexPos);
        vec3 vView=normalize(uCameraPos - vVertexPos);
        vec3 vHalf=normalize(vLight+vView); 
        vec3 vReflect=reflect(vVertexPos-uCameraPos,vNormal);  
    
        float hov = max(dot(vHalf,vView),0.0001);
        float noh = max(dot(vNormal,vHalf),0.0001);
        float nov = max(dot(vNormal,vView),0.0001);
        float nol = max(dot(vNormal, vLight),0.0001);
               
        vec3 rd = lambertian(hov,noh,nov,nol);

        float rs = cooktorrance(hov,noh,nov,nol); 

        float F0=pow((1.0-IOR)/(1.0+IOR),2);        
        float kd=1-(F0+(1.0-F0)*pow((1-hov),5));

        return (kd*rd*lightColor+rs*lightColor)*nol;
    }          

    void main(){    
        init();      
        vec3 result=vec3(0.0, 0.0, 0.0);

        for(int i = 0; i < NUM_LIGHTS; i++)
            result += PBR(uLights[i].color,uLights[i].position);  
        result += basecolor*ra;

        gl_FragColor = vec4(result,1.0);
    }
    """
        
fragment_shader_source2 ="""
    #version 330 core
    #define NUM_LIGHTS 4  

    struct Light {    
        vec3 position;
        vec3 color;
    };  

    uniform Light uLights[NUM_LIGHTS];
                                         
    uniform float umetalness;
    uniform float uroughness;                      
    uniform float uIOR;    

    uniform int uUsePBRtexture;                
    uniform int uUseAlbedotexture;
                                                                     
    uniform vec3 uLightPos;
    uniform vec3 uLightColor;
    uniform vec3 uCameraPos;
                  
    uniform sampler2D sTexture;
    uniform sampler2D sPBRTexture;

    varying vec2 vTexCoord;             
    varying vec3 vNormal;    
    varying vec3 vVertexPos;

    float metalness;
    float roughness;                      
    float IOR;
    float pi = 3.1415926535897932384626433832795;               
    float lightintensity = 10.0;   
    vec3 basecolor = vec3(0.9529, 0.7882, 0.4078);             
    float ra=0.1;  
    
    void init(){                        
        if (uUseAlbedotexture==1){
            vec4 color = texture2D(sTexture, vTexCoord);    
            basecolor=vec3(color[0],color[1],color[2]); 
        }

        if (uUsePBRtexture==1){
            vec4 PBRValue = texture2D(sPBRTexture, vTexCoord); 
            roughness = PBRValue[0];           
            metalness = PBRValue[1];
            IOR = PBRValue[2];
        }
        else{
            metalness = umetalness;
            roughness = uroughness;
            IOR = uIOR;
        }
        metalness = min((ceil(vTexCoord[0]*10)*9/100+0.1),0.99);
        roughness = min((ceil(vTexCoord[1]*10)*9/100+0.1),0.99);                   
    }

    float cooktorrance(float hov,float noh,float nov,float nol){     
        float F0=pow((1.0-IOR)/(1.0+IOR),2);        
        float F=F0+(1.0-F0)*pow((1-hov),5);
                                            
        float D=pow(roughness,4)/(pi*pow((pow(noh,2)*(pow(roughness,4)-1.0)+1.0),2));
                                            
        float k=pow(roughness+1.0,2)/8.0;                                       
        float G1=nol/(nol*(1.0-k)+k);         
        float G2=nov/(nov*(1.0-k)+k);
        float G=G1*G2;
                        
        return F*D*G/(4.0*nol*nov); 
    }

    vec3 lambertian(float hov,float noh,float nov,float nol){                 
        float dr = (1.0-metalness);

        return dr*basecolor/pi;
    }

    vec3 PBR(vec3 lightColor, vec3 lightPos){
        vec3 vLight=normalize(lightPos - vVertexPos);
        vec3 vView=normalize(uCameraPos - vVertexPos);
        vec3 vHalf=normalize(vLight+vView); 
                           
        float hov = max(dot(vHalf,vView),0.0001);
        float noh = max(dot(vNormal,vHalf),0.0001);
        float nov = max(dot(vNormal,vView),0.0001);
        float nol = max(dot(vNormal, vLight),0.0001);
                                     
        vec3 rd = lambertian(hov,noh,nov,nol);

        float rs = cooktorrance(hov,noh,nov,nol); 

        float F0=pow((1.0-IOR)/(1.0+IOR),2);        
        float kd=1-(F0+(1.0-F0)*pow((1-hov),5));

        return (kd*rd*lightColor+rs*lightColor)*nol;
    }          

    void main(){    
        init();      
        vec3 result=vec3(0.0, 0.0, 0.0);

        for(int i = 0; i < NUM_LIGHTS; i++)
            result += PBR(uLights[i].color,uLights[i].position);  
        result += basecolor*ra;

       gl_FragColor = vec4(result,1.0);
    }
    """

fragment_shader_source3 ="""
    #version 330 core
    #define NUM_LIGHTS 4  

    struct Light {    
        vec3 position;
        vec3 color;
    };  

    uniform Light uLights[NUM_LIGHTS];
                                         
    uniform float umetalness;
    uniform float uroughness;                      
    uniform float uIOR;    

    uniform int uUsePBRtexture;                
    uniform int uUseAlbedotexture;
    uniform int uUseSkybox;
                                       
    uniform vec3 uLightPos;
    uniform vec3 uLightColor;
    uniform vec3 uCameraPos;
                  
    uniform sampler2D sTexture;
    uniform sampler2D sPBRTexture;
    uniform samplerCube sSkyboxTexture; 

    varying vec2 vTexCoord;             
    varying vec3 vNormal;    
    varying vec3 vVertexPos;

    float metalness;
    float roughness;                      
    float IOR;

    float test;

    float pi = 3.1415926535897932384626433832795;               
    float lightintensity = 10.0;   
    vec4 skyboxcolor;
    vec3 basecolor = vec3(0.9529, 0.7882, 0.4078);             
    float ra=0.1;  
    
    void init(){     
        /*                   
        if (uUseAlbedotexture==1){
            vec4 color = texture2D(sTexture, vTexCoord);    
            basecolor=vec3(color[0],color[1],color[2]); 
        }
        */

        metalness = umetalness;
        roughness = uroughness;
        IOR = uIOR;
    }

    float cooktorrance(float hov,float noh,float nov,float nol){     
        float F0=pow((1.0-IOR)/(1.0+IOR),2);        
        float F=F0+(1.0-F0)*pow((1-hov),5);
                                            
        float D=pow(roughness,4)/(pi*pow((pow(noh,2)*(pow(roughness,4)-1.0)+1.0),2));
                                            
        float k=pow(roughness+1.0,2)/8.0;                                       
        float G1=nol/(nol*(1.0-k)+k);         
        float G2=nov/(nov*(1.0-k)+k);
        float G=G1*G2;
                        
        return F*D*G/(4.0*nol*nov); 
    }

    vec3 lambertian(float hov,float noh,float nov,float nol){                 
        float dr = (1.0-metalness);

        return dr*basecolor/pi;
    }

    vec3 PBR(vec3 lightColor, vec3 lightPos){
        vec3 vLight=normalize(lightPos - vVertexPos);
        vec3 vView=normalize(uCameraPos - vVertexPos);
        vec3 vHalf=normalize(vLight+vView); 
        vec3 vReflect=reflect(vVertexPos-uCameraPos,vNormal);  
    
        float hov = max(dot(vHalf,vView),0.0001);
        float noh = max(dot(vNormal,vHalf),0.0001);
        float nov = max(dot(vNormal,vView),0.0001);
        float nol = max(dot(vNormal, vLight),0.0001);
               
        vec3 rd = lambertian(hov,noh,nov,nol);

        float rs = cooktorrance(hov,noh,nov,nol); 

        float F0=pow((1.0-IOR)/(1.0+IOR),2);        
        float kd=1-(F0+(1.0-F0)*pow((1-hov),5));

        return (kd*rd*lightColor+rs*lightColor)*nol;
    }           

    void main(){    
        init();      
        vec3 result=vec3(0.0, 0.0, 0.0);

        for(int i = 0; i < NUM_LIGHTS; i++)
            result += PBR(uLights[i].color,uLights[i].position);  
        result += basecolor*ra;
        
        vec3 vReflect=reflect(vVertexPos-uCameraPos,vNormal);  

        vec3 temp2=vVertexPos+vReflect;

        result = PBR(texture(sSkyboxTexture,vReflect).xyz,temp2);

        gl_FragColor = vec4(result,1.0);
    }
    """

light_vertex_shader_source = """
    #version 330 core
    uniform mat4 uMVMatrix;
    uniform mat4 uPMatrix;     
       
    layout (location=0) in vec3 aVertex; 
                                         
    void main(){                       
       gl_Position = (uPMatrix * uMVMatrix)  * vec4(aVertex, 1.0);
    }
    """
 
light_fragment_shader_source ="""
    #version 330 core

    #define NUM_LIGHTS 1

    struct Light {    
        vec3 position;
        vec3 color;
    };  

    uniform Light uLights[NUM_LIGHTS]; 

    void main(){         
       gl_FragColor = vec4(uLights[0].color,1.0);
    }
    """

skybox_vertex_shader_source = """
    #version 330 core
    uniform mat4 uMVMatrix;
    uniform mat4 uPMatrix;
                                       
    layout (location=0) in vec3 aVertex; 
    
    varying vec3 vTexCoord;     
                                         
    void main(){
       vTexCoord = aVertex;           
       gl_Position = (uPMatrix * uMVMatrix)  * vec4(aVertex, 1.0);
    }
    """

skybox_fragment_shader_source ="""
    #version 330 core
    uniform samplerCube sSkyboxTexture; 

    varying vec3 vTexCoord;  

    void main(){         
       gl_FragColor = texture(sSkyboxTexture,vTexCoord);
    }
    """

def load_program(vertex_source, fragment_source):
    vertex_shader = load_shader(GL_VERTEX_SHADER, vertex_source)
    fragment_shader = load_shader(GL_FRAGMENT_SHADER, fragment_source)

    program = glCreateProgram()

    glAttachShader(program, vertex_shader) #shader 프로그램에 할당
    glAttachShader(program, fragment_shader) #shader 프로그램에 할당

    glLinkProgram(program)

    print(glGetProgramiv(program, GL_LINK_STATUS))


    return program

def load_shader(shader_type, source):
    shader = glCreateShader(shader_type)

    glShaderSource(shader, source)
    glCompileShader(shader)

    if glGetShaderiv(shader, GL_COMPILE_STATUS, None) == GL_FALSE:
        info_log = glGetShaderInfoLog(shader)
        print(info_log)
        glDeleteProgram(shader)
        return 0

    return shader

def initprogram1():
    program = load_program(vertex_shader_source, fragment_shader_source1)
    glUseProgram(program)
    glEnableVertexAttribArray(0)
    glEnableVertexAttribArray(1)
    glEnableVertexAttribArray(2)
    return program

def initprogram2():
    program = load_program(vertex_shader_source, fragment_shader_source2)
    glUseProgram(program)
    glEnableVertexAttribArray(0)
    glEnableVertexAttribArray(1)
    glEnableVertexAttribArray(2)
    return program

def initprogram3():
    program = load_program(vertex_shader_source, fragment_shader_source3)
    glUseProgram(program)
    glEnableVertexAttribArray(0)
    glEnableVertexAttribArray(1)
    glEnableVertexAttribArray(2)
    return program

def initlightprogram():
    program = load_program(light_vertex_shader_source, light_fragment_shader_source)
    glUseProgram(program)
    glEnableVertexAttribArray(0)
    glEnableVertexAttribArray(1)
    glEnableVertexAttribArray(2)
    return program

def initSkyboxprogram():
    program = load_program(skybox_vertex_shader_source, skybox_fragment_shader_source)
    glUseProgram(program)
    glEnableVertexAttribArray(0)
    glEnableVertexAttribArray(1)
    glEnableVertexAttribArray(2)
    return program

class Program:
    def __init__(self,program):
        self.program=program
        self.lightslocation=[]

        self.cameralocation=None
        self.MVMatrixlocation=None
        self.PMatrixlocation=None

        self.metalnesslocation=None
        self.roughnesslocation=None
        self.IORlocation=None
    
    def InitLight(self):
        self.lightslocation=[]
        for i in range(4):
            temp=[]
            temp.append(glGetUniformLocation(self.program, "uLights[{}].position".format(i)))
            temp.append(glGetUniformLocation(self.program, "uLights[{}].color".format(i)))
            self.lightslocation.append(temp)

    def InitCamera(self):
        self.cameralocation = glGetUniformLocation(self.program, "uCameraPos")
        self.MVMatrixlocation = glGetUniformLocation(self.program, "uMVMatrix")
        self.PMatrixlocation = glGetUniformLocation(self.program, "uPMatrix")

    def InitMaterial(self):
        self.metalnesslocation = glGetUniformLocation(self.program, "umetalness")
        self.roughnesslocation = glGetUniformLocation(self.program, "uroughness")
        self.IORlocation = glGetUniformLocation(self.program, "uIOR")

    def InitTexture(self):
        self.albedotexturelocation = glGetUniformLocation(self.program, "sTexture")
        self.PBRtexturelocation = glGetUniformLocation(self.program, "sPBRTexture")

        self.uUsePBRtexture = glGetUniformLocation(self.program, "uUsePBRtexture")
        self.uUseAlbedotexture = glGetUniformLocation(self.program, "uUseAlbedotexture")
        glUniform1i(self.uUsePBRtexture, 1)
        glUniform1i(self.uUseAlbedotexture, 1)
    
    def InitSkyBox(self):
        self.skyboxtexturelocation = glGetUniformLocation(self.program, "sSkyboxTexture")

        self.uUseSkybox = glGetUniformLocation(self.program, "uUseSkybox")
        glUniform1i(self.uUseSkybox, 1)