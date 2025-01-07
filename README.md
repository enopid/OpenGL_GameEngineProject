# OpenGL_GameEngineProject

## 프로젝트 개요

### **PBR and Mesh Implementation**
|<img src="https://github.com/user-attachments/assets/60c6e663-cb7a-4b38-89d9-1e0a815e13ae" alt="" width="400" height="300" style="margin:0; padding:0;">| <img src="https://github.com/user-attachments/assets/64885aef-bcb3-4e02-b5be-fb8efe359a14" alt="" width="400" height="300" style="margin:0; padding:0;">|
|:-----------------:|:----------------:|
|mode1 Ingame|mode3 |

- 본 프로젝트는 mesh와 texture를 렌더링하는 과정과 PBR을 GLSL을 직접작성하여 구현한 데모 게임엔진 입니다.
- 기본적인 렌더링구현과 간단한 이동을 지원하고 cmd를 통해 현재적용된 패러미터의 수치를 확인가능합니다.
### **PBR**
- roughness, metalness, IOR을 파라미터로 하여 PBR model인 cook-torreance 모델을 GLSL을 작성하여 구현

### **Texture and Mesh Load**
- 로컬 폴더내에 택스쳐를 임포트하여 albedo 텍스쳐와 PBR texture를 가져와 모델에 적용
- obj 형태의 mesh를 임포트하여 렌더링

### 모드 설명 및 조작방법
## 모드별 설명
    모드 1 - 고해상도 단일 오브젝트 PBR 프로퍼티 조정 example
    모드 2 - 복수 오브젝트 metalness/roughness example
    모드 3 - 램프모델 PBR map 구현 example
 
## 공통 조작방법
    tab - 모드변경
    마우스 - 시점조작
    Q/E - 현재 시점에서 위아래 이동
    A/D - 현재 시점에서 좌우 이동
    W/S - 현재 시점에서 앞뒤 이동





## 모드별 조작법
### Mode1
> metalness, roughness, IOR 수치를 조절하며 매테리얼의 특징을 확인가능한 모드이다.
> 하단의 사진은 각 요소를 조절시 나오는 차이를 보여준다.

|<img src="https://github.com/user-attachments/assets/1103012a-dd24-4706-81b6-2af675c3b152" alt="" width="400" height="300" style="margin:0; padding:0;">| <img src="https://github.com/user-attachments/assets/eed5c8c0-8100-432b-b6c2-124078560733" alt="" width="400" height="300" style="margin:0; padding:0;">|
|:-----------------:|:----------------:|
|metalness : 0.07 / **roughness : 0.2** / IOR :2.0|metalness : 0.07 / **roughness : 0.8** / IOR :2.0|
|<img src="https://github.com/user-attachments/assets/87740377-f706-4299-9138-448c30d94c3f" alt="" width="400" height="300" style="margin:0; padding:0;">| <img src="https://github.com/user-attachments/assets/14d34cc4-39d1-49b4-99f6-630f3fdb9bdd" alt="" width="400" height="300" style="margin:0; padding:0;">|
|**metalness : 0.1**/ roughness : 0.2 / IOR : 1.0|**metalness : 0.81**/ roughness : 0.2 / IOR : 1.0|
|<img src="https://github.com/user-attachments/assets/d4c45440-dbe5-49f1-89c5-ad548f6fede4" alt="" width="400" height="300" style="margin:0; padding:0;">| <img src="https://github.com/user-attachments/assets/25c5950a-2518-433d-9601-3e671de10bf0" alt="" width="400" height="300" style="margin:0; padding:0;">|
|metalness : 0.1/ roughness : 0.2 / **IOR : 1.2**|metalness : 0.1/ roughness : 0.2 / **IOR : 6.0**|
    - Space - 매태리얼 프로퍼티 변경
    - J/K - 매태리얼 프로퍼티 조정
### Mode2
> IOR 수치를 조절하며 매테리얼의 특징을 확인가능한 모드이다.
> 왼쪽으로 갈수록 metalness가 커지고 아래로갈수록 loughness가 커진다.
> 하단의 영상은 IOR 수치를 점진적으로 조절한 여상이다. 

https://github.com/user-attachments/assets/4b7e3d28-7989-47c2-b70f-4e800d090851

    - J/K - IOR 조정
### Mode3
> PBR Map과 ALbedo Map을 가져와 PBR이 적용된 램프 매쉬를 렌더링하는 모드이다.



https://github.com/user-attachments/assets/6f7a4014-e937-41be-8976-222704eec3fc



    - 별도의 특이조작 없음

## 실행 파일


- [download link](https://github.com/enopid/OpenGL_GameEngineProject/releases/download/release/exe.zip) 
