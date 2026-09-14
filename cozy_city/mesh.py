"""Dependency-free, Z-up mesh recipes. Metres; face colours authored in sRGB.

Primitive construction adapted from octopus7/astra-blender-forest (MIT).
See THIRD_PARTY_NOTICES.md. All polygons are triangulated, flat shaded.
"""
from dataclasses import dataclass, field
from math import cos, sin, pi, sqrt


def rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))


def shade(c, f):
    return tuple(max(0.0, min(1.0, v * f)) for v in c)


def linear(v):
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def sub(a, b):
    return tuple(x-y for x, y in zip(a, b))


def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def unit(a):
    d = sqrt(sum(v*v for v in a))
    if d < 1e-12:
        raise ValueError('Cannot normalize a zero-length vector')
    return tuple(v/d for v in a)


def transform(v, location=(0, 0, 0), angle=0.0, scale=1.0):
    x, y, z = (q*scale for q in v)
    return (x*cos(angle)-y*sin(angle)+location[0],
            x*sin(angle)+y*cos(angle)+location[1], z+location[2])


@dataclass
class Mesh:
    name: str
    category: str = 'Props'
    vertices: list = field(default_factory=list)
    faces: list = field(default_factory=list)
    colors: list = field(default_factory=list)

    def patch(self, vertices, faces, color, rng=None, variation=0.0):
        offset = len(self.vertices)
        self.vertices.extend(tuple(v) for v in vertices)
        for face in faces:
            c = shade(color, 1+rng.uniform(-variation, variation)) if rng else color
            for j in range(1, len(face)-1):
                self.faces.append((offset+face[0], offset+face[j], offset+face[j+1]))
                self.colors.append(c)
        return self

    def box(self, center, size, color, angle=0):
        vs = [transform((x*size[0]/2, y*size[1]/2, z*size[2]/2), center, angle)
              for x, y, z in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),
                              (-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
        return self.patch(vs, [(0,3,2,1),(0,1,5,4),(1,2,6,5),
                              (2,3,7,6),(3,0,4,7),(4,5,6,7)], color)

    def tube(self, a, b, r0, r1, color, n=8):
        axis = unit(sub(b, a))
        helper = (0,0,1) if abs(axis[2]) < .9 else (0,1,0)
        u = unit(cross(axis, helper))
        v = cross(axis, u)
        vs = [tuple(p[k]+r*(u[k]*cos(2*pi*i/n)+v[k]*sin(2*pi*i/n))
                    for k in range(3)) for p, r in ((a,r0),(b,r1)) for i in range(n)]
        if r1 <= 1e-7:
            vs = vs[:n]+[b]
            fs = [tuple(reversed(range(n)))]+[(i,(i+1)%n,n) for i in range(n)]
        else:
            fs = [tuple(reversed(range(n))), tuple(range(n,2*n))]
            fs += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
        return self.patch(vs, fs, color)

    def beam(self, a, b, width, color):
        # Four-sided tube is a compact square beam; width is its diagonal.
        return self.tube(a, b, width/2, width/2, color, 4)

    def ico(self, center, scale, color, rng=None):
        t = (1+sqrt(5))/2
        vs = [unit(v) for v in [(-1,t,0),(1,t,0),(-1,-t,0),(1,-t,0),
              (0,-1,t),(0,1,t),(0,-1,-t),(0,1,-t),(t,0,-1),(t,0,1),(-t,0,-1),(-t,0,1)]]
        fs = [(0,11,5),(0,5,1),(0,1,7),(0,7,10),(0,10,11),(1,5,9),
              (5,11,4),(11,10,2),(10,7,6),(7,1,8),(3,9,4),(3,4,2),
              (3,2,6),(3,6,8),(3,8,9),(4,9,5),(2,4,11),(6,2,10),(8,6,7),(9,8,1)]
        vs = [tuple(center[k]+v[k]*scale[k] for k in range(3)) for v in vs]
        return self.patch(vs, fs, color, rng, .065)

    def merge(self, other, location=(0,0,0), angle=0):
        off = len(self.vertices)
        self.vertices.extend(transform(v, location, angle) for v in other.vertices)
        self.faces.extend(tuple(off+i for i in f) for f in other.faces)
        self.colors.extend(other.colors)
        return self

    def bounds(self):
        return [[min(v[i] for v in self.vertices) for i in range(3)],
                [max(v[i] for v in self.vertices) for i in range(3)]]
