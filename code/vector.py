from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import numpy as np

def calculate_normal(v1,v2,v3):
    vector1 = np.array(v2) - np.array(v1)
    vector2 = np.array(v3) - np.array(v1)
    cross_product = np.cross(vector1, vector2)
    normalized_cross_product = cross_product / np.linalg.norm(cross_product)
    return normalized_cross_product

def rotation_Y(angle,vectorarray):
    angle = math.radians(angle)

    yaw_rotation_matrix = np.array([[math.cos(angle), 0, math.sin(angle)],
                                   [0, 1, 0],
                                   [-math.sin(angle), 0, math.cos(angle)]])

    vectorarray = (np.dot(yaw_rotation_matrix, np.array(vectorarray))).tolist()

    return vectorarray

def rotation_X(angle,vectorarray):
    angle = math.radians(angle)

    yaw_rotation_matrix = np.array([[1, 0, 0],
                                   [0,math.cos(angle), -math.sin(angle)],
                                   [0, math.sin(angle), math.cos(angle)]])

    vectorarray = (np.dot(yaw_rotation_matrix, np.array(vectorarray))).tolist()

    return vectorarray

def rotation_Z(angle,vectorarray):
    angle = math.radians(angle)

    yaw_rotation_matrix = np.array([[math.cos(angle), -math.sin(angle), 0],
                                   [math.sin(angle), math.cos(angle), 0],
                                   [0, 0, 1]])

    vectorarray = (np.dot(yaw_rotation_matrix, np.array(vectorarray))).tolist()
    
    return vectorarray

def perspective(fovy, aspect, z_near, z_far):
    f = 1 / math.tan(math.radians(fovy) / 2)
    return np.array([
        [f / aspect,  0,                                   0,  0],
        [          0, f,                                   0,  0],
        [          0, 0, (z_far + z_near) / (z_near - z_far), -1],
        [          0, 0, (2*z_far*z_near) / (z_near - z_far),  0]
    ])

def view(pos, u, v, w):
    if u==[]:
        u=np.cross(v,w)
    
    rotation=np.array([
        [   u[0], v[0],     w[0],  0],
        [   u[1], v[1],     w[1],  0],
        [   u[2], v[2],     w[2],  0],
        [      0,    0,        0,  1]
    ])
    translatation=np.array([
        [      1,      0,      0,  0],
        [      0,      1,      0,  0],
        [      0,      0,      1,  0],
        [ -pos[0], -pos[1], -pos[2],  1]
    ])
    return np.dot(translatation,rotation)

def rotate(angle, x, y, z):
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

def translate(pos):
    return np.array([
        [      1,      0,      0,  0],
        [      0,      1,      0,  0],
        [      0,      0,      1,  0],
        [ pos[0], pos[1], pos[2],  1]
    ])
    
def orthogonal(left,right,bottom,top, z_near, z_far):
    return np.array([
        [             2/(right-left),                          0,                                 0,  0],
        [                          0,             2/(top-bottom),                                 0,  0],
        [                          0,                          0,                 -2/(z_far-z_near),  0],
        [ -(right+left)/(right-left), -(top+bottom)/(top-bottom), (z_far+z_near) / (z_near - z_far),  1]
    ])