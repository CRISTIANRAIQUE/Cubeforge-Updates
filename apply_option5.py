#!/usr/bin/env python3
# Refina as texturas usando os sprites da Opção 5 e seleciona 2D no GUI / 3D só empunhado.
from pathlib import Path
import base64
import json
import struct
import zlib
from option5_sprites import DATA, NAMES

ROOT = Path("src/main/resources/assets/modcentral")
RAW = zlib.decompress(base64.b85decode(DATA))
ncolors = RAW[0]
assert ncolors == 64, ncolors
palette = [tuple(RAW[1+3*k:1+3*k+3]) for k in range(ncolors)]
start = 1 + 3*ncolors
allindices = RAW[start:]
assert len(allindices) == 8*32*32, len(allindices)
TRANSPARENT = (0,0,0,0)

def png(path, pixels):
    height = len(pixels)
    width = len(pixels[0])
    assert width == height == 32
    scanlines = b"".join(b"\0"+b"".join(bytes(c) for c in row) for row in pixels)
    def chunk(tag, content):
        return struct.pack(">I",len(content))+tag+content+struct.pack(">I",zlib.crc32(tag+content)&0xffffffff)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",struct.pack(">IIBBBBB",width,height,8,6,0,0,0))+chunk(b"IDAT",zlib.compress(scanlines,9))+chunk(b"IEND",b""))

def json_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding="utf-8")

texture_pixels={}
for i,name in enumerate(NAMES):
    indexes=allindices[i*1024:(i+1)*1024]
    image=[[TRANSPARENT if indexes[y*32+x]==0 else (*palette[indexes[y*32+x]-1],255)
            for x in range(32)] for y in range(32)]
    texture_pixels[name]=image
    location = "block" if name.startswith("minerio_") else "item"
    png(ROOT/("textures/"+location+"/"+name+".png"),image)

TOOLS=["espada_cristal_azul","machado_cristal_azul","picareta_cristal_azul","pa_cristal_azul","enxada_cristal_azul"]
HAND_TRANSFORMS={
    "firstperson_righthand":{"rotation":[0,-55,26],"translation":[1.1,2.9,0.1],"scale":[0.8,0.8,0.8]},
    "firstperson_lefthand":{"rotation":[0,55,-26],"translation":[1.1,2.9,0.1],"scale":[0.8,0.8,0.8]},
    "thirdperson_righthand":{"rotation":[0,-52,48],"translation":[0,3.4,0],"scale":[0.79,0.79,0.79]},
    "thirdperson_lefthand":{"rotation":[0,52,-48],"translation":[0,3.4,0],"scale":[0.79,0.79,0.79]},
    "gui":{"rotation":[0,0,0],"scale":[1,1,1]}
}
def create_hand_model(name):
    picture=texture_pixels[name]
    # Cada bloco da malha corresponde a 2x2 pixels da textura, mantendo escala Minecraft.
    elements=[]
    for cy in range(16):
        for cx in range(16):
            colors=[]
            for dy in range(2):
                for dx in range(2):
                    rgba=picture[cy*2+dy][cx*2+dx]
                    if rgba[3]>0:
                        colors.append(rgba)
            if not colors:continue
            # Arestas azul gelo destacadas; cabo preto/prata com volume menor.
            r=sum(v[0] for v in colors)/len(colors)
            g=sum(v[1] for v in colors)/len(colors)
            b=sum(v[2] for v in colors)/len(colors)
            icy = b>r+24 and (g>r+10)
            depth = 4.4 if icy else 2.7
            z0=8-depth/2
            z1=8+depth/2
            # No eixo XY é uma célula de 1x1, no Z é um prisma real.
            uv=[cx,cy,cx+1,cy+1]
            faces={
                side:{"texture":"#layer0","uv":uv}
                for side in ("north","south","east","west","up","down")
            }
            elements.append({
                "from":[cx,15-cy,z0],
                "to":[cx+1,16-cy,z1],
                "faces":faces
            })
    assert 20<len(elements)<256, (name,len(elements))
    model={
      "ambientocclusion":True,
      "gui_light":"side",
      "textures":{"particle":"modcentral:item/"+name,"layer0":"modcentral:item/"+name},
      "elements":elements,
      "display":HAND_TRANSFORMS
    }
    json_write(ROOT/("models/item/"+name+"_held.json"),model)
    json_write(ROOT/("models/item/"+name+".json"),{
        "parent":"minecraft:item/handheld",
        "textures":{"layer0":"modcentral:item/"+name}
    })
    # A definição de item seleciona conforme o contexto:
    # GUI/hotbar/aba/solo = flat 2D; mão direita/esquerda em primeira ou terceira pessoa = voxel 3D.
    json_write(ROOT/("items/"+name+".json"),{
      "model":{
        "type":"minecraft:select",
        "property":"minecraft:display_context",
        "cases":[{
          "when":["firstperson_righthand","firstperson_lefthand","thirdperson_righthand","thirdperson_lefthand"],
          "model":{"type":"minecraft:model","model":"modcentral:item/"+name+"_held"}
        }],
        "fallback":{"type":"minecraft:model","model":"modcentral:item/"+name}
      }
    })

for tool in TOOLS:create_hand_model(tool)

# Cristal fica como ícone 2D, mesmo quando é segurado; os blocos já têm cubos nativos.
name="cristal_azul"
json_write(ROOT/("models/item/"+name+".json"),{
    "parent":"minecraft:item/generated",
    "textures":{"layer0":"modcentral:item/"+name}
})
json_write(ROOT/("items/"+name+".json"),{
    "model":{"type":"minecraft:model","model":"modcentral:item/"+name}
})
print("OPÇÃO 5: 8 sprites 32x32, 5 ícones 2D e 5 modelos voxel 3D apenas na mão.")
