"""Original city assets using the upstream's faceted, vertex-colour approach.
Front of every building is -Y; origin is at foundation centre, ground level.
"""
import random
from math import pi, cos, sin
from .mesh import Mesh, rgb, shade

CREAM = rgb('f1e4c7')
WOOD = rgb('80583d')
STONE = rgb('b7b5a0')
GLASS = rgb('496970')
LEAF = rgb('9db75a')
ROOFS = [rgb(h) for h in ('b9674e','547d7a','7a8290','b28a55')]
WALLS = [rgb(h) for h in ('e9d4ac','e4bba7','b8c6ad','d6ceb8')]


def window(m, x, y, z, w=1.1, h=1.5):
    m.box((x,y,z), (w+.22,.15,h+.22), CREAM)
    m.box((x,y-.09,z), (w,.07,h), GLASS)
    m.box((x,y-.14,z), (.065,.07,h), CREAM)
    m.box((x,y-.14,z), (w,.07,.065), CREAM)
    m.box((x,y-.12,z-h/2-.13), (w+.38,.36,.16), STONE)


def gable(m, w, d, z, rise, color):
    w, d = w/2, d/2
    # Closed convex prism. Front/back gables and two roof planes.
    vs = [(-w,-d,z),(w,-d,z),(0,-d,z+rise),
          (-w,d,z),(w,d,z),(0,d,z+rise)]
    m.patch(vs, [(0,1,2),(3,5,4),(0,2,5,3),(1,4,5,2),(0,3,4,1)], color)
    for y in (-d,d):
        m.beam((-w,y,z), (0,y,z+rise), .23, CREAM)
        m.beam((0,y,z+rise), (w,y,z), .23, CREAM)
    m.beam((0,-d-.12,z+rise), (0,d+.12,z+rise), .27, shade(color,.8))


def building(kind, variant=0):
    floors = {'house':2,'shop':2,'apartment':4,'library':3}[kind]
    w, d = {'house':(8.4,8.8),'shop':(10.2,9.2),
            'apartment':(12.0,11.4),'library':(12.8,10.4)}[kind]
    h = floors*2.8
    m = Mesh(f'{kind}_{variant:02d}', 'Buildings')
    wall, roof = WALLS[variant%4], ROOFS[variant%4]
    m.box((0,0,.22),(w+.4,d+.4,.44), STONE)
    m.box((0,0,h/2+.4),(w,d,h), wall)
    for floor in range(floors+1):
        m.box((0,0,.45+floor*2.8),(w+.15,d+.15,.16), CREAM)
    for x in (-w/2+.1,w/2-.1):
        for y in (-d/2+.1,d/2-.1):
            m.box((x,y,h/2+.4),(.3,.3,h), CREAM)
    if kind == 'apartment':
        m.box((0,0,h+.62),(w+.7,d+.7,.38), roof)
        for x in (-w/2,w/2):
            m.box((x,0,h+1.0),(.25,d,.55), CREAM)
        for y in (-d/2,d/2):
            m.box((0,y,h+1.0),(w,.25,.55), CREAM)
        m.box((1.4,1.3,h+1.0),(2.8,2.4,.9), STONE)
    else:
        gable(m,w+.9,d+.9,h+.5,2.45,roof)
        m.box((w*.24,d*.2,h+1.45),(.75,.8,2.4), STONE)
        m.box((w*.24,d*.2,h+2.7),(.95,1.0,.22), CREAM)
    # Four facades, assembled in local coordinates to keep orientation consistent.
    for side in range(4):
        front = Mesh('facade')
        span = w if side%2 == 0 else d
        depth = d if side%2 == 0 else w
        for f in range(floors):
            for x in (-span*.29,span*.29):
                window(front,x,-depth/2-.1,1.9+f*2.8)
        m.merge(front, angle=side*pi/2)
    m.box((0,-d/2-.14,1.6),(1.5,.22,2.4), WOOD)
    m.box((0,-d/2-.27,1.95),(1.05,.07,1.1), GLASS)
    m.box((0,-d/2-.65,.2),(2.5,1.45,.4), STONE)
    m.box((.48,-d/2-.33,1.36),(.10,.07,.10), CREAM)
    if kind in ('shop','library'):
        m.box((0,-d/2-.4,3.0),(w*.78,.25,.7), WOOD)
        m.box((0,-d/2-.55,3.0),(w*.71,.06,.45), roof)
        # Geometry-only striped awning; no external fonts/textures.
        for i in range(8):
            m.box((-w*.39+w*.78*(i+.5)/8,-d/2-.7,2.62),
                  (w*.78/8,1.25,.14), roof if i%2 else CREAM)
        for x in (-w*.4,w*.4):
            m.box((x,-d/2-.55,.55),(1.3,.85,.8), WOOD)
            for j in (-.35,0,.35):
                m.ico((x+j,-d/2-.55,1.05),(.28,.28,.32),
                      rgb('dfa3aa') if variant%2 else LEAF)
    return m


def townhall():
    m = building('library',0)
    m.name = 'townhall'
    m.box((0,0,13.0),(4.4,4.4,8.2), WALLS[0])
    m.box((0,0,16.9),(5.0,5.0,.38), CREAM)
    m.tube((0,0,17.1),(0,0,20.5),3.5,0,ROOFS[1],4)
    for side in range(4):
        clock = Mesh('clock')
        clock.tube((0,-2.23,15.0),(0,-2.4,15.0),1.0,1.0,CREAM,12)
        clock.box((0,-2.52,15.27),(.09,.08,.65), WOOD)
        clock.box((.23,-2.53,15.0),(.55,.08,.09), WOOD)
        m.merge(clock,angle=side*pi/2)
    return m


def tree(variant):
    r = random.Random(100+variant)
    m = Mesh(f'tree_{variant:02d}','Trees')
    h = (5.7,6.5,5.1,7.1)[variant]
    m.tube((0,0,0),(.12,0,h*.68),.28,.11,WOOD,7)
    for i in range(3):
        a = i*2*pi/3+.3
        m.tube((0,0,h*.35),(cos(a),sin(a),h*.65),.14,.06,WOOD,6)
        m.ico((cos(a)*.85,sin(a)*.85,h*.65),(1.55,1.5,1.65),
              shade(LEAF,.91+variant*.025),r)
    m.ico((0,0,h*.81),(1.85,1.7,1.9),LEAF,r)
    return m


def lamp():
    m = Mesh('lamp','StreetFurniture')
    m.tube((0,0,0),(0,0,.25),.32,.24,STONE,8)
    m.tube((0,0,.25),(0,0,4.2),.10,.075,GLASS,6)
    m.box((0,0,4.25),(.55,.55,.75),rgb('f7d99a'))
    m.tube((0,0,4.65),(0,0,5.0),.5,0,GLASS,4)
    return m


def bench():
    m = Mesh('bench','StreetFurniture')
    for x in (-.75,.75):
        m.box((x,0,.28),(.15,.65,.56),GLASS)
        m.box((x,.27,.75),(.12,.12,1.3),GLASS)
    for y in (-.23,0,.23):
        m.box((0,y,.58),(2.0,.18,.10),WOOD)
    for z in (.9,1.16):
        m.box((0,.29,z),(2.0,.12,.2),WOOD)
    return m


def fountain():
    m = Mesh('fountain','Landmarks')
    m.tube((0,0,0),(0,0,.32),3.4,3.4,STONE,16)
    m.tube((0,0,.33),(0,0,.58),3.05,3.05,CREAM,16)
    m.tube((0,0,.59),(0,0,.61),2.72,2.72,rgb('69afb0'),16)
    m.tube((0,0,.61),(0,0,2.3),.4,.25,STONE,8)
    m.tube((0,0,2.3),(0,0,2.5),1.35,1.1,CREAM,12)
    m.tube((0,0,2.51),(0,0,2.54),.94,.94,rgb('69afb0'),12)
    return m


def car(variant):
    m = Mesh(f'car_{variant:02d}','Vehicles')
    color = [rgb(h) for h in ('c97961','d9b45f','799b96','d8d6c2')][variant]
    m.box((0,0,.65),(4.0,1.8,.75),color)
    m.box((-.15,0,1.27),(2.15,1.65,.7),GLASS)
    m.box((-.15,0,1.65),(2.28,1.78,.14),color)
    for x in (-1.15,1.15):
        for y in (-.93,.93):
            m.tube((x,y-.12,.47),(x,y+.12,.47),.4,.4,GLASS,10)
    for y in (-.58,.58):
        m.box((2.03,y,.7),(.08,.35,.24),CREAM)
    return m


def make_library(cfg):
    b, r = cfg['block_size'], cfg['road_width']
    assets = {}
    def add(m):
        assets[m.name] = m
        return m
    for kind in ('house','shop','apartment'):
        for v in range(4):
            add(building(kind,v))
    add(building('library',2)); add(townhall())
    for v in range(4):
        add(tree(v)); add(car(v))
    add(lamp()); add(bench()); add(fountain())
    add(Mesh('ground','Ground').box((0,0,-.55),(cfg['map_size'],cfg['map_size'],1),rgb('9cac75')))
    add(Mesh('block','Ground').box((0,0,.09),(b,b,.18),rgb('ded3b9')))
    add(Mesh('garden','Ground').box((0,0,.19),(b-6,b-6,.06),rgb('aabb7a')))
    add(Mesh('plaza','Ground').box((0,0,.2),(b-5,b-5,.08),rgb('c9bda6')))
    road = add(Mesh('road','Roads').box((0,0,.025),(b,r,.15),rgb('737e7b')))
    for x in range(-int(b/2)+5,int(b/2)-4,6):
        road.box((x,0,.104),(2.7,.15,.008),CREAM)
    for x in (-b/2+1.7,b/2-1.7):
        for j in range(int(r)-2):
            road.box((x,-(int(r)-3)/2+j,.104),(2.0,.47,.008),CREAM)
    add(Mesh('junction','Roads').box((0,0,.025),(r,r,.15),rgb('737e7b')))
    pond = add(Mesh('pond','Landmarks'))
    pond.tube((0,0,.23),(0,0,.3),6.6,6.6,STONE,12)
    pond.tube((0,0,.31),(0,0,.33),6.1,6.1,rgb('69afb0'),12)
    path = add(Mesh('path','Ground'))
    path.box((0,0,.245),(2.8,b-6,.04),rgb('dbcbaa'))
    return assets
