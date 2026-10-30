#!/usr/bin/env python3
"""ModCentral 1.4.0: clean option 5 icons in GUI; compact, correctly UV-mapped 3D models in hand."""
from pathlib import Path
import base64
import json
import struct
import zlib
from collections import deque
from option5_sprites import DATA, NAMES

ROOT = Path("src/main/resources/assets/modcentral")
RAW = zlib.decompress(base64.b85decode(DATA))
ncolors = RAW[0]
assert ncolors == 64
palette = [tuple(RAW[1+3*k:1+3*k+3]) for k in range(ncolors)]
indices = RAW[1+3*ncolors:]
assert len(indices) == 8*1024
ALPHA = (0,0,0,0)

def json_write(path, val):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(val, ensure_ascii=False, indent=2), encoding="utf-8")

def save_png(path, picture):
    height = len(picture)
    width = len(picture[0])
    assert width == height == 32
    rows = b"".join(b"\0"+b"".join(bytes(p) for p in row) for row in picture)
    def chunk(tag, payload):
        return (struct.pack(">I",len(payload))+tag+payload+
                struct.pack(">I",zlib.crc32(tag+payload)&0xffffffff))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",struct.pack(">IIBBBBB",32,32,8,6,0,0,0))+
                     chunk(b"IDAT",zlib.compress(rows,9))+chunk(b"IEND",b""))

TOOLS = ["espada_cristal_azul","machado_cristal_azul","picareta_cristal_azul",
         "pa_cristal_azul","enxada_cristal_azul"]
TOOL_NAMES = set(TOOLS)
PIXEL_ICE = (208,239,255,255)
EDGE_ICE = (101,156,194,255)
EDGE_METAL = (53,69,88,255)

def clean_swatch(rgb):
    """Limit dithering to a deliberate ice/silver palette, preserving shaded pixels."""
    r,g,b = rgb
    luminance = (r*3+g*5+b*2)//10
    if luminance < 47:
        return (23,35,54,255)
    if luminance < 76:
        return (44,62,87,255)
    cold = b > r + 15
    if cold and luminance < 113:
        return (51,95,151,255)
    if cold and luminance < 151:
        return (83,143,204,255)
    if cold and luminance < 187:
        return (124,190,234,255)
    if cold and luminance < 218:
        return (172,221,249,255)
    if luminance < 112:
        return (89,105,127,255)
    if luminance < 152:
        return (129,149,175,255)
    if luminance < 198:
        return (190,206,221,255)
    return (234,247,255,255)

def large_components(mask):
    """Remove only isolated pixel noise in the 16x16 inventory icons."""
    seen=set()
    components=[]
    for y in range(16):
        for x in range(16):
            if not mask[y][x] or (x,y) in seen:
                continue
            q=deque([(x,y)])
            seen.add((x,y))
            component=[]
            while q:
                xx,yy=q.popleft()
                component.append((xx,yy))
                for dx,dy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)):
                    a,b=xx+dx,yy+dy
                    if 0<=a<16 and 0<=b<16 and mask[b][a] and (a,b) not in seen:
                        seen.add((a,b))
                        q.append((a,b))
            components.append(component)
    if not components:
        return mask
    largest=max(len(c) for c in components)
    keep={point for c in components if len(c)>=max(2,largest//12) for point in c}
    return [[mask[y][x] and (x,y) in keep for x in range(16)] for y in range(16)]

def sharpen_item(original):
    # 32px noisy artwork -> aligned 16px sprites -> 32px nearest scaling.
    small=[[ALPHA for _ in range(16)] for _ in range(16)]
    counts=[[0]*16 for _ in range(16)]
    for y in range(16):
        for x in range(16):
            swatch=[original[y*2+dy][x*2+dx] for dy in (0,1) for dx in (0,1)]
            nonempty=[c for c in swatch if c[3] > 0]
            counts[y][x]=len(nonempty)
            if len(nonempty)>=2:
                mean=tuple(round(sum(c[k] for c in nonempty)/len(nonempty)) for k in range(3))
                small[y][x]=clean_swatch(mean)
    mask=large_components([[counts[y][x]>=2 for x in range(16)] for y in range(16)])
    for y in range(16):
        for x in range(16):
            if not mask[y][x]:
                small[y][x]=ALPHA
    # Crisp original-sized 32x32 with no ghost pixels.
    output=[[small[y//2][x//2] for x in range(32)] for y in range(32)]
    return output,small

images={}
small_pixels={}
for i,name in enumerate(NAMES):
    raw=indices[i*1024:(i+1)*1024]
    original=[[ALPHA if raw[y*32+x]==0 else (*palette[raw[y*32+x]-1],255)
              for x in range(32)] for y in range(32)]
    if name in TOOL_NAMES or name=="cristal_azul":
        refined,small=sharpen_item(original)
        small_pixels[name]=small
    else:
        refined=original
    images[name]=refined
    subfolder="block" if name.startswith("minerio_") else "item"
    save_png(ROOT/("textures/"+subfolder+"/"+name+".png"),refined)

# A side material atlas is deliberately uniform. Using the front art on the
# sides, as the older version did, caused gigantic streaks and texture artifacts.
save_png(ROOT/"textures/item/ice_side.png",[[EDGE_ICE]*32 for _ in range(32)])
save_png(ROOT/"textures/item/metal_side.png",[[EDGE_METAL]*32 for _ in range(32)])

# Subtle volume: thicker ice heads, slimmer dark handles.
# Real cube faces are generated only at exposed edges to prevent coplanar flicker.
HAND_DISPLAY={
    "firstperson_righthand":{"rotation":[0,-58,21],"translation":[0.0,1.0,0.15],"scale":[0.52,0.52,0.52]},
    "firstperson_lefthand":{"rotation":[0,58,-21],"translation":[0.0,1.0,0.15],"scale":[0.52,0.52,0.52]},
    "thirdperson_righthand":{"rotation":[0,-58,50],"translation":[0.0,2.5,0],"scale":[0.63,0.63,0.63]},
    "thirdperson_lefthand":{"rotation":[0,58,-50],"translation":[0.0,2.5,0],"scale":[0.63,0.63,0.63]},
    "fixed":{"rotation":[0,180,0],"scale":[0.7,0.7,0.7]},
    "ground":{"translation":[0,1.5,0],"scale":[0.55,0.55,0.55]},
}

def create_hand_model(name):
    pix=small_pixels[name]
    occupied=[[pix[y][x][3]>0 for x in range(16)] for y in range(16)]
    elements=[]
    for cy in range(16):
        for cx in range(16):
            if not occupied[cy][cx]:
                continue
            c=pix[cy][cx]
            ice=c[2] > c[0]+17 and c[1]>c[0]+7 and max(c[:3])>140
            thickness=2.5 if ice else 1.8
            z0=8-thickness/2
            z1=8+thickness/2
            # Model UV maps to a 16x16 UV grid regardless of 32px texture.
            uv=[cx,cy,cx+1,cy+1]
            faces={
                "north":{"texture":"#layer0","uv":uv},
                "south":{"texture":"#layer0","uv":uv}
            }
            material="#ice" if ice else "#metal"
            # Adjacent voxels share a boundary; do not draw their internal faces.
            if cx==0 or not occupied[cy][cx-1]:
                faces["west"]={"texture":material,"uv":[0,0,16,16]}
            if cx==15 or not occupied[cy][cx+1]:
                faces["east"]={"texture":material,"uv":[0,0,16,16]}
            if cy==0 or not occupied[cy-1][cx]:
                faces["up"]={"texture":material,"uv":[0,0,16,16]}
            if cy==15 or not occupied[cy+1][cx]:
                faces["down"]={"texture":material,"uv":[0,0,16,16]}
            elements.append({
                "from":[cx,15-cy,z0],
                "to":[cx+1,16-cy,z1],
                "faces":faces
            })
    assert 15<len(elements)<256,(name,len(elements))
    model={
        "ambientocclusion":False,
        "gui_light":"front",
        "textures":{
            "particle":"modcentral:item/"+name,
            "layer0":"modcentral:item/"+name,
            "ice":"modcentral:item/ice_side",
            "metal":"modcentral:item/metal_side"
        },
        "elements":elements,
        "display":HAND_DISPLAY
    }
    json_write(ROOT/("models/item/"+name+"_held.json"),model)
    # Only the flat sprite is used in the creative inventory and hotbar.
    json_write(ROOT/("models/item/"+name+".json"),{
        "parent":"minecraft:item/handheld",
        "textures":{"layer0":"modcentral:item/"+name}
    })
    json_write(ROOT/("items/"+name+".json"),{
        "model":{
            "type":"minecraft:select",
            "property":"minecraft:display_context",
            "cases":[{
                "when":["firstperson_righthand","firstperson_lefthand",
                        "thirdperson_righthand","thirdperson_lefthand"],
                "model":{"type":"minecraft:model","model":"modcentral:item/"+name+"_held"}
            }],
            "fallback":{"type":"minecraft:model","model":"modcentral:item/"+name}
        }
    })

for tool in TOOLS:
    create_hand_model(tool)

json_write(ROOT/"models/item/cristal_azul.json",{
    "parent":"minecraft:item/generated",
    "textures":{"layer0":"modcentral:item/cristal_azul"}
})
json_write(ROOT/"items/cristal_azul.json",{
    "model":{"type":"minecraft:model","model":"modcentral:item/cristal_azul"}
})
print("MODCENTRAL 1.4.0 OK: crisp 2D inventory + smaller nonflickering 3D hand models.")
