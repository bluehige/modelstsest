"""Road-first block planning, repeatable placement, and geometry validation."""
from collections import Counter
from math import pi, isfinite
import random
from .assets import make_library
from .mesh import cross, sub, transform

PRESETS = {
    'city': dict(blocks=5, block_size=44.0, road_width=10.0, margin=10.0),
    'village': dict(blocks=3, block_size=40.0, road_width=7.0, margin=16.0),
}


def config(values=None):
    values = dict(values or {})
    allowed = {'preset','seed','blocks','block_size','road_width','margin','trees','cars'}
    unknown = set(values)-allowed
    if unknown:
        raise ValueError(f'Unknown settings: {sorted(unknown)}')
    preset = values.get('preset','city')
    if preset not in PRESETS:
        raise ValueError('preset must be city or village')
    c = dict(PRESETS[preset], preset=preset, seed=42, trees=True, cars=True)
    c.update(values)
    if type(c['seed']) is not int or not 0 <= c['seed'] <= 2147483647:
        raise ValueError('seed must be an integer from 0 to 2147483647')
    if type(c['blocks']) is not int or c['blocks'] not in (3,5,7):
        raise ValueError('blocks must be 3, 5 or 7')
    for key, lo, hi in [('block_size',38,60),('road_width',7,16),('margin',5,40)]:
        v = c[key]
        if isinstance(v,bool) or not isinstance(v,(int,float)) or not isfinite(v) or not lo <= v <= hi:
            raise ValueError(f'{key} must be a finite number from {lo} to {hi}')
    if type(c['trees']) is not bool or type(c['cars']) is not bool:
        raise ValueError('trees and cars must be true or false')
    c['map_size'] = c['blocks']*c['block_size']+(c['blocks']+1)*c['road_width']+2*c['margin']
    return c


def instance_bounds(mesh, item):
    lo, hi = mesh.bounds()
    pts = [transform((x,y,z),item['location'],item['angle'],item['scale'])
           for x in (lo[0],hi[0]) for y in (lo[1],hi[1]) for z in (lo[2],hi[2])]
    return [[min(p[i] for p in pts) for i in range(3)],
            [max(p[i] for p in pts) for i in range(3)]]


def build_world(values=None):
    c = config(values)
    assets = make_library(c)
    items, lots, pois = [], [], []
    n, b, rw = c['blocks'],c['block_size'],c['road_width']
    pitch = b+rw
    first = -(n*b+(n+1)*rw)/2+rw/2
    roads = [first+i*pitch for i in range(n+1)]
    centers = [(roads[i]+roads[i+1])/2 for i in range(n)]
    def add(asset, x=0, y=0, z=0, angle=0, scale=1.0, zone='infrastructure'):
        it = dict(name=f'CC_{asset}_{len(items):05d}', asset=asset,
                  location=(x,y,z),angle=angle,scale=scale,zone=zone,
                  cell=f'C{int((x+c["map_size"]/2)//50):02d}_{int((y+c["map_size"]/2)//50):02d}')
        items.append(it)
        return it
    add('ground')
    road_rng = random.Random(c['seed']+7001)
    for i, x in enumerate(roads):
        for j, y in enumerate(roads):
            add('junction',x,y)
        for j, y in enumerate(centers):
            add('road',x,y,angle=pi/2)
            if c['cars'] and road_rng.random() < .55:
                add(f'car_{road_rng.randrange(4):02d}',x+rw*.24,y,
                    z=.12,angle=pi/2,zone='traffic')
    for i, x in enumerate(centers):
        for j, y in enumerate(roads):
            add('road',x,y)
            if c['cars'] and road_rng.random() < .55:
                add(f'car_{road_rng.randrange(4):02d}',x,y-rw*.24,z=.12,zone='traffic')
    mid = n//2
    for i, x in enumerate(centers):
        for j, y in enumerate(centers):
            rng = random.Random(c['seed']+i*1009+j*9176)
            zone = 'civic' if (i,j)==(mid,mid) else 'park' if (i,j)==(n-1,n-1) else 'neighbourhood'
            add('block',x,y,zone=zone)
            add('plaza' if zone=='civic' else 'garden',x,y,zone=zone)
            for dx in (-b/2+1.2,b/2-1.2):
                for dy in (-b/2+1.2,b/2-1.2):
                    add('lamp',x+dx,y+dy,z=.18,zone=zone)
            def place_building(asset, dx, dy, angle):
                extent = max(abs(v) for row in assets[asset].bounds() for v in row[:2])
                fit = 1.0 if zone=='civic' else min(1.0,(b/4-3.05)/extent)
                it = add(asset,x+dx,y+dy,z=.22,angle=angle,scale=fit,zone=zone)
                bounds = instance_bounds(assets[asset],it)
                lots.append(dict(instance=it['name'],block=[i,j],bounds=bounds,
                                 block_bounds=[x-b/2+3,y-b/2+3,x+b/2-3,y+b/2-3]))
            if zone == 'civic':
                place_building('townhall',0,b*.18,0)
                add('fountain',x,y-b*.25,z=.24,zone=zone)
                for s in (-1,1):
                    add('bench',x+s*7,y-b*.24,z=.25,angle=-s*pi/2,zone=zone)
                pois.append(dict(id='town_square',name='Town Hall & Fountain',location=[x,y,0]))
            elif zone == 'park':
                add('pond',x,y+3,zone=zone)
                add('path',x,y-b*.28,angle=pi/2,zone=zone)
                for s in (-1,1):
                    add('bench',x+s*8,y-6,z=.25,zone=zone)
                pois.append(dict(id='park',name='Pond Garden',location=[x,y,0]))
                if c['trees']:
                    for dx,dy in [(-13,11),(13,11),(-13,0),(13,0),(-12,-15),(12,-15)]:
                        add(f'tree_{rng.randrange(4):02d}',x+dx,y+dy,z=.22,
                            scale=rng.uniform(.85,1.06),zone=zone)
            else:
                for a, dx in enumerate((-b*.25,b*.25)):
                    for k, dy in enumerate((-b*.25,b*.25)):
                        central = abs(i-mid)+abs(j-mid) <= 2
                        if c['preset']=='city' and central:
                            kind = 'shop' if (i+j+a+k)%2 else 'apartment'
                        else:
                            kind = 'shop' if rng.random()<.22 else 'house'
                        place_building(f'{kind}_{rng.randrange(4):02d}',dx,dy,pi if k else 0)
                # A small shared courtyard; no random clutter in circulation space.
                add('bench',x,y,z=.23,zone=zone)
            if c['trees']:
                for dx,dy in [(0,-b/2+1.5),(0,b/2-1.5),(-b/2+1.5,0),(b/2-1.5,0)]:
                    add(f'tree_{rng.randrange(4):02d}',x+dx,y+dy,z=.18,scale=.83,zone=zone)
    used = {it['asset'] for it in items}
    return dict(config=c,assets={k:v for k,v in assets.items() if k in used},
                instances=items,lots=lots,points_of_interest=pois)


def stats(world):
    counts = Counter(i['asset'] for i in world['instances'])
    return dict(map_size_m=world['config']['map_size'],
                instances=len(world['instances']),unique_meshes=len(world['assets']),
                unique_triangles=sum(len(m.faces) for m in world['assets'].values()),
                placed_triangles=sum(len(world['assets'][k].faces)*v for k,v in counts.items()),
                buildings=len(world['lots']),
                categories=dict(Counter(world['assets'][i['asset']].category for i in world['instances'])))


def validate_world(world):
    errors = []
    for key, m in world['assets'].items():
        if not m.faces or len(m.faces)!=len(m.colors):
            errors.append(f'{key}: missing faces or colour count mismatch')
        for v in m.vertices:
            if len(v)!=3 or not all(isfinite(q) for q in v):
                errors.append(f'{key}: non-finite vertex')
        for f in m.faces:
            if len(f)!=3 or not all(type(i) is int and 0<=i<len(m.vertices) for i in f):
                errors.append(f'{key}: invalid triangle'); continue
            a,bb,cc = (m.vertices[i] for i in f)
            if sum(v*v for v in cross(sub(bb,a),sub(cc,a))) < 1e-14:
                errors.append(f'{key}: degenerate triangle')
        for col in m.colors:
            if len(col)!=3 or not all(isfinite(v) and 0<=v<=1 for v in col):
                errors.append(f'{key}: invalid colour')
    names = set()
    for it in world['instances']:
        if it['name'] in names: errors.append('Duplicate instance name')
        names.add(it['name'])
        if it['asset'] not in world['assets']: errors.append('Missing asset reference')
        if not all(isfinite(v) for v in (*it['location'],it['angle'],it['scale'])) or it['scale']<=0:
            errors.append('Invalid transform')
    for lot in world['lots']:
        lo,hi = lot['bounds']; x0,y0,x1,y1 = lot['block_bounds']
        if lo[0]<x0-1e-6 or lo[1]<y0-1e-6 or hi[0]>x1+1e-6 or hi[1]>y1+1e-6:
            errors.append(f'{lot["instance"]}: building encroaches on sidewalk/road')
    for a,lot in enumerate(world['lots']):
        lo,hi=lot['bounds']
        for other in world['lots'][a+1:]:
            if lot['block']!=other['block']: continue
            lo2,hi2=other['bounds']
            if min(hi[0],hi2[0])-max(lo[0],lo2[0])>1e-6 and min(hi[1],hi2[1])-max(lo[1],lo2[1])>1e-6:
                errors.append(f'{lot["instance"]}: overlapping building footprint')
    return errors
