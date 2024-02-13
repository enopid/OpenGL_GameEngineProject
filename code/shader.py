from OpenGL.GL import *

vertex_shader_source = """
    #version 330 core
    uniform mat4 uMMatrix;
    uniform mat4 uVMatrix;
    uniform mat4 uPMatrix;
                                       
    layout (location=0) in vec3 aVertex; 
    layout (location=1) in vec3 aNormal;
    layout (location=2) in vec2 aTexCoord;
    
    varying vec2 vTexCoord;                        
    varying vec3 vNormal;  
    varying vec3 vVertexPos; 
                                         
    void main(){
       vTexCoord = aTexCoord;
       vVertexPos = (uMMatrix * vec4(aVertex, 1.0)).xyz;
       vNormal=normalize(aNormal);                
                                       
       gl_Position = (uPMatrix * uVMatrix  * uMMatrix)  * vec4(aVertex, 1.0);
    }
    """

fragment_shader_source ="""
    #version 330 core
    #define NUM_LIGHTS 4  
    #define NUM_MATERIALS 4  
    #define PI 3.14159265358979 

    struct Light {    
        vec3 position;
        vec3 color;
    };  

    struct Material {
        bool useTexture;
        vec3 value;
        sampler2D texture;
    };

    uniform Light uLights[NUM_LIGHTS];
    uniform Material uMaterials[NUM_MATERIALS];
                                       
    uniform vec3 uLightPos;
    uniform vec3 uLightColor;
    uniform vec3 uCameraPos;

    varying vec2 vTexCoord;             
    varying vec3 vNormal;    
    varying vec3 vVertexPos;

    vec3 materials[NUM_MATERIALS];

    vec3 albedo;  
    float metalness;
    float roughness;                      
    float IOR;
                    
    float ra=0.1;  
    
    void init(){   
        for(int i = 0; i < NUM_MATERIALS; i++){
            if(uMaterials[i].useTexture){
                vec4 temp = texture2D(uMaterials[i].texture, vTexCoord);    
                materials[i]=temp.xyz; 
            }
            else{
                materials[i]=uMaterials[i].value;
            }
        }

        albedo=materials[0];            
        metalness=materials[1].x;
        roughness=materials[2].x;                      
        //IOR=materials[3].x;
        IOR=2.0;
    }

    float cooktorrance(float hov,float noh,float nov,float nol){     
        float F0=pow((1.0-IOR)/(1.0+IOR),2);        
        float F=F0+(1.0-F0)*pow((1-hov),5);
                                            
        float D=pow(roughness,4)/(PI*pow((pow(noh,2)*(pow(roughness,4)-1.0)+1.0),2));
                                            
        float k=pow(roughness+1.0,2)/8.0;                                       
        float G1=nol/(nol*(1.0-k)+k);         
        float G2=nov/(nov*(1.0-k)+k);
        float G=G1*G2;
                        
        return F*D*G/(4.0*nol*nov); 
    }

    vec3 lambertian(float hov,float noh,float nov,float nol){                 
        float dr = (1.0-metalness);

        return dr*albedo/PI;
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
        result += albedo*ra;

        gl_FragColor = vec4(result,1.0);
    }
    """

vertex_shader_source = """
    #version 330 core
    uniform mat4 uMMatrix;
    uniform mat4 uVMatrix;
    uniform mat4 uPMatrix;
                                       
    layout (location=0) in vec3 aVertex; 
    layout (location=1) in vec3 aNormal;
    layout (location=2) in vec2 aTexCoord;
    
    varying vec2 vTexCoord;                        
    varying vec3 vNormal;  
    varying vec3 vVertexPos; 
                                         
    void main(){
       vTexCoord = aTexCoord;
       vVertexPos = (uMMatrix * vec4(aVertex, 1.0)).xyz;
       vNormal=normalize(aNormal);                
                                       
       gl_Position = (uPMatrix * uVMatrix  * uMMatrix)  * vec4(aVertex, 1.0);
    }
    """

fragment_shader_source ="""
    #version 330 core
    #define NUM_LIGHTS 4  
    #define NUM_MATERIALS 4  
    #define PI 3.14159265358979 

    struct Light {    
        vec3 position;
        vec3 color;
    };  

    struct Material {
        bool useTexture;
        vec3 value;
        sampler2D texture;
    };

    uniform Light uLights[NUM_LIGHTS];
    uniform Material uMaterials[NUM_MATERIALS];
    uniform samplerCube uSkyboxTexture; 
                                       
    uniform vec3 uLightPos;
    uniform vec3 uLightColor;
    uniform vec3 uCameraPos;

    varying vec2 vTexCoord;             
    varying vec3 vNormal;    
    varying vec3 vVertexPos;

    vec3 materials[NUM_MATERIALS];

    vec3 albedo;  
    float metalness;
    float roughness;                      
    float IOR;
                    
    float ra=0.1;  
    
    void init(){   
        for(int i = 0; i < NUM_MATERIALS; i++){
            if(uMaterials[i].useTexture){
                vec4 temp = texture2D(uMaterials[i].texture, vTexCoord);    
                materials[i]=temp.xyz; 
            }
            else{
                materials[i]=uMaterials[i].value;
            }
        }

        albedo=materials[0];            
        metalness=materials[1].x;
        roughness=materials[2].x;                      
        //IOR=materials[3].x;
        IOR=2.0;
    }

    float cooktorrance(float hov,float noh,float nov,float nol){     
        float F0=pow((1.0-IOR)/(1.0+IOR),2);        
        float F=F0+(1.0-F0)*pow((1-hov),5);
                                            
        float D=pow(roughness,4)/(PI*pow((pow(noh,2)*(pow(roughness,4)-1.0)+1.0),2));
                                            
        float k=pow(roughness+1.0,2)/8.0;                                       
        float G1=nol/(nol*(1.0-k)+k);         
        float G2=nov/(nov*(1.0-k)+k);
        float G=G1*G2;
                        
        return F*D*G/(4.0*nol*nov); 
    }

    vec3 lambertian(float hov,float noh,float nov,float nol){                 
        float dr = (1.0-metalness);

        return dr*albedo/PI;
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

    vec3 Reflect(){
        vec3 vReflect=normalize(reflect(vVertexPos-uCameraPos,vNormal));  
        vec3 result = texture(uSkyboxTexture,vReflect).xyz;
        
        return result;
    }   

    vec3 Refract(){ 
        float ratio = 1.00 / 1.52;
        vec3 I = normalize(vVertexPos-uCameraPos);
        vec3 R = refract(I, normalize(vNormal), ratio);

        vec3 result = texture(uSkyboxTexture,R).xyz;
        
        return result;
    }       

    void main(){    
        init();      
        vec3 result=vec3(0.0, 0.0, 0.0);

        for(int i = 0; i < NUM_LIGHTS; i++)
            result += PBR(uLights[i].color,uLights[i].position);  
        result += albedo*ra;

        gl_FragColor = vec4(result,gl_FragCoord.z);
        //gl_FragColor = vec4(Refract(),1.0);
    }
    """

test_vertex_shader_source = """
    #version 330 core
    layout (location = 0) in vec2 aPos;
    layout (location = 1) in vec2 aTexCoords;

    out vec2 TexCoords;

    void main()
    {
        gl_Position = vec4(aPos.x, aPos.y, 0.0, 1.0); 
        TexCoords = aTexCoords;
    }  
    """

test_fragment_shader_source ="""
    #version 330 core
    out vec4 FragColor;
    
    in vec2 TexCoords;

    uniform sampler2D screenTexture;
    const float offset = 1.0 / 300.0;  
    void main()
    { 
        vec2 offsets[9] = vec2[](
            vec2(-offset,  offset), // top-left
            vec2( 0.0f,    offset), // top-center
            vec2( offset,  offset), // top-right
            vec2(-offset,  0.0f),   // center-left
            vec2( 0.0f,    0.0f),   // center-center
            vec2( offset,  0.0f),   // center-right
            vec2(-offset, -offset), // bottom-left
            vec2( 0.0f,   -offset), // bottom-center
            vec2( offset, -offset)  // bottom-right    
        );

        float kernel[9] = float[](
            0, 0, 0,
            0, 1, 0,
            0, 0, 0
        );
        
        vec3 sampleTex[9];
        for(int i = 0; i < 9; i++)
        {
            sampleTex[i] = vec3(texture(screenTexture, TexCoords.st + offsets[i]));
        }
        vec3 col = vec3(0.0);
        for(int i = 0; i < 9; i++)
            col += sampleTex[i] * kernel[i];
        
        FragColor = vec4(col, 1.0);
        FragColor = vec4(vec3(gl_FragCoord.z), 1.0);
    }
    
    """

Billboard_vertex_shader_source = """
    #version 330 core
    uniform mat4 uMMatrix;
    uniform mat4 uVMatrix;
    uniform mat4 uPMatrix;    
       
    layout (location=0) in vec3 aVertex; 
    layout (location=1) in vec2 vTexcoord;

    varying vec2 TexCoord;  
                                         
    void main(){    
        gl_Position = (uPMatrix * uVMatrix * uMMatrix)  * vec4(aVertex, 1.0);   
        TexCoord=vTexcoord;
    }
    """
 
Billboard_fragment_shader_source ="""
    #version 330 core
    #define NUM_MATERIALS 4  

    struct Material {
        bool useTexture;
        vec3 value;
        sampler2D texture;
    };

    uniform Material uMaterials[NUM_MATERIALS];

    varying vec2 TexCoord;  

    void main(){      
        vec4 texColor=texture(uMaterials[0].texture,TexCoord);
        if (texColor.w < 0.1)
            discard;
       gl_FragColor = texture(uMaterials[0].texture,TexCoord);
    }
    """

skybox_vertex_shader_source = """
    #version 330 core
    uniform mat4 uMMatrix;
    uniform mat4 uVMatrix;
    uniform mat4 uPMatrix;
                                       
    layout (location=0) in vec3 aVertex; 
    
    varying vec3 vTexCoord;     
                                         
    void main(){
       vTexCoord = aVertex;           
       gl_Position = (uPMatrix * uVMatrix  * uMMatrix)  * vec4(aVertex, 1.0);
    }
    """

skybox_fragment_shader_source ="""
    #version 330 core
    uniform samplerCube uSkyboxTexture; 

    varying vec3 vTexCoord;  

    void main(){         
       gl_FragColor = texture(uSkyboxTexture,vTexCoord);
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

def initprogram(vertex_source, fragment_source):
    program = load_program(vertex_source, fragment_source)
    glUseProgram(program)
    glEnableVertexAttribArray(0)
    glEnableVertexAttribArray(1)
    glEnableVertexAttribArray(2)
    return program

def initprogram1():
    program = initprogram(vertex_shader_source, fragment_shader_source)
    return program

def initBillboardprogram():
    program = initprogram(Billboard_vertex_shader_source, Billboard_fragment_shader_source)
    return program

def initSkyboxprogram():
    program = initprogram(skybox_vertex_shader_source, skybox_fragment_shader_source)
    return program

def inittestprogram():
    program = initprogram(test_vertex_shader_source, test_fragment_shader_source)
    return program