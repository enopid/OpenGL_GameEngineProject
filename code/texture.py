from OpenGL.GL import *
import numpy as np
from PIL import Image

def load_texture(filename):
    img = Image.open(filename, 'r').convert("RGB")
    img_data = np.array(img, dtype=np.uint8)
    w, h = img.size

    texture = glGenTextures(1)

    glBindTexture(GL_TEXTURE_2D, texture)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, w, h, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)

    return texture

def load_skycube_texture(foldername):
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_CUBE_MAP, texture)
    filenames=["right","left","top","bottom","front","back"]

    for i in range(6):
        filename=foldername+"/"+filenames[i]+".jpg"
        img = Image.open(filename, 'r').convert("RGB")
        img_data = np.array(img, dtype=np.uint8)
        w, h = img.size

        glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, GL_RGB, w, h, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
        
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

    return texture  