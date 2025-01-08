# OpenGL_GameEngineProject(진행중)

## 프로젝트 개요

### **PBR and Mesh Implementation**
|<img src="https://github.com/user-attachments/assets/c7b163e8-78bb-458e-98b3-e4e23449ced5" alt="" width="400" height="300" style="margin:0; padding:0;">|
|:-----------------:|
|mode1 Ingame|

- 본 프로젝트는 기존 PBR project를 확장시켜 코드전체에 component 패턴을 적용하고 게임엔진의 여러기능을 추가하고 시각화하는 프로젝트입니다.

### **Component Pattern**
- 본 프로젝트는 유니티와 동일하게 scene내에 object가 존재하고 object에 여러 컴포넌트를 달수있는 component pattern을 바탕으로 한다.
- 기본적으로 Scene, GameObject, Componeet의 3가지 클래스가 존재하고 Componeet 클래스를 상속받아 Transform, Mesh, Material, Camera 등의 여러가지 기능의 자식 클래스를 가진다.
- 기본적으로 json내에 정의된 scene내에서 각 gameobject와 object내 컴포넌트가 정의되어 파일실행시 json을 바탕으로 scene 내 정보을 로드한다. <br>
<img src="https://github.com/user-attachments/assets/a335eed7-b326-4f36-8b8d-ff3ce038499a" alt="" width="400" height="400" style="margin:0; padding:0;"> <br>

### **added feature**
- billboard renderer <br>

<img src="https://github.com/user-attachments/assets/c7b163e8-78bb-458e-98b3-e4e23449ced5" alt="" width="400" height="300" style="margin:0; padding:0;"> <br>
> light표시 를 나타내는 아이콘의 경우 billboard renderer를 적용하여 크기자체는 거리에의해 변하지만 방향은 플레이어를 향하도록 고정된것을 확인가능하다. 
- skybox <br>
<img src="https://github.com/user-attachments/assets/6e67e8c9-ce55-4727-9c91-cabad434f34a" alt="" width="400" height="300" style="margin:0; padding:0;"> <br>
> cube의 형태로된 texture로 skybox를 구현해 배경을 띄운모습이다.

- shadow <br>
<img src="https://github.com/user-attachments/assets/bbeeef47-4112-4fb2-b682-554ebf0a7896" alt="" width="400" height="300" style="margin:0; padding:0;"> <br>
> shadow buffer를 추가해 direction light에 그림자가 적용된 모습을 볼수있다.

> (아직 point light의 경우 그림자가 적용되지않았다.)

## 모드 설명 및 조작방법
### 공통 조작방법
    마우스 - 시점조작
    Q/E - 현재 시점에서 위아래 이동
    A/D - 현재 시점에서 좌우 이동
    W/S - 현재 시점에서 앞뒤 이동


## 실행 파일


- [download link](https://github.com/enopid/OpenGL_GameEngineProject/releases/download/refactoring_gameengine/preject3.zip) 
