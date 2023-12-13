from OpenGL.GL import *
import numpy as np

class OBJ:
    def __init__(self, filename, swapyz=False):
        """Loads a Wavefront OBJ file. """
        self._vertices = []
        self._normals = []
        self._texcoords = []

        self._vertex_triangles=[]
        self._texture_triangles=[]
        self._normal_triangles=[]

        for line in open(filename, "r"):
            if line.startswith('#'): continue
            values = line.split()
            if not values: continue
            if values[0] == 'v':
                v = [*map(float, values[1:4])]
                if swapyz:
                    v = [v[0], v[2], v[1]]
                self._vertices.append(v)
            elif values[0] == 'vn':
                v = [*map(float, values[1:4])]
                if swapyz:
                    v = [v[0], v[2], v[1]]
                self._normals.append(v)
            elif values[0] == 'vt':
                self._texcoords.append([*map(float, values[1:3])])
            elif values[0] == 'f':
                face = []
                texcoords = []
                norms = []
                for v in values[1:]:
                    w = v.split('/')
                    face.append(int(w[0]))
                    if len(w) >= 2 and len(w[1]) > 0:
                        texcoords.append(int(w[1]))
                    else:
                        texcoords.append(0)
                    if len(w) >= 3 and len(w[2]) > 0:
                        norms.append(int(w[2]))
                    else:
                        norms.append(0)

                self._vertex_triangles.append(face)
                self._texture_triangles.append(texcoords)
                self._normal_triangles.append(norms)
        
        self.vertices = np.array([
            self._vertices[index-1]
            for indices in self._vertex_triangles
            for index in indices
        ])

        self.normals = np.array([
            self._normals[index-1]
            for indices in self._normal_triangles
            for index in indices
        ])

        self.texcoords = np.array([
            self._texcoords[index-1]
            for indices in self._texture_triangles
            for index in indices
        ])