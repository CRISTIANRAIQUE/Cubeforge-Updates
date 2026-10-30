#!/usr/bin/env python3
"""ModCentral 1.6.0: incorpora oito texturas autorais na pasta textura do mod.
Executar depois de generate_assets.py, apply_option5.py e fix_tool_sprites.py.
Usa apenas a biblioteca padrão do Python, para rodar no GitHub Actions.
"""
from pathlib import Path
import base64
import json
import struct
import zlib

ROOT=Path('src/main/resources/assets/modcentral')
TEXTURES=ROOT/'textures/textura'
NAMES=['cristal_azul','espada_cristal_azul','machado_cristal_azul',
       'picareta_cristal_azul','pa_cristal_azul','enxada_cristal_azul',
       'minerio_cristal_azul','minerio_cristal_profundo']
TOOLS=NAMES[1:6]
raw=zlib.decompress(base64.b85decode(Path('modcentral_texture_payload.txt').read_text().strip()))
assert raw[0]==len(NAMES)
position=1

def write_json(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')

def save_png(path,pixels):
    assert len(pixels)==32 and all(len(row)==32 for row in pixels)
    image_rows=b''.join(b'\0'+b''.join(bytes(c) for c in row) for row in pixels)
    def chunk(tag,data):
        return (struct.pack('>I',len(data))+tag+data+
                struct.pack('>I',zlib.crc32(tag+data)&0xffffffff))
    data=(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',32,32,8,6,0,0,0))+
          chunk(b'IDAT',zlib.compress(image_rows,9))+chunk(b'IEND',b''))
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(data)

pixel_images={}
for name in NAMES:
    color_count=raw[position]
    position+=1
    palette=[tuple(raw[position+3*j:position+3*j+3]) for j in range(color_count)]
    position+=color_count*3
    indexes=raw[position:position+1024]
    position+=1024
    alpha=raw[position:position+1024]
    position+=1024
    assert len(indexes)==len(alpha)==1024
    pixels=[]
    for y in range(32):
        line=[]
        for x in range(32):
            k=y*32+x
            line.append((*palette[indexes[k]],255) if alpha[k] else (0,0,0,0))
        pixels.append(line)
    pixel_images[name]=pixels
    save_png(TEXTURES/(name+'.png'),pixels)
assert position==len(raw),(position,len(raw))

# A pasta exata 'textura' é usada pelos modelos do Minecraft, não só armazenada.
for name in NAMES[:6]:
    path=ROOT/'models/item'/(name+'.json')
    model=json.loads(path.read_text(encoding='utf-8'))
    model.setdefault('textures',{})['layer0']='modcentral:textura/'+name
    write_json(path,model)

for name in NAMES[6:]:
    path=ROOT/'models/block'/(name+'.json')
    model=json.loads(path.read_text(encoding='utf-8'))
    model.setdefault('textures',{})['all']='modcentral:textura/'+name
    write_json(path,model)

DISPLAY={
    'firstperson_righthand':{'rotation':[0,-52,19],'translation':[0.05,1.15,0.1],'scale':[0.5,0.5,0.5]},
    'firstperson_lefthand':{'rotation':[0,52,-19],'translation':[0.05,1.15,0.1],'scale':[0.5,0.5,0.5]},
    'thirdperson_righthand':{'rotation':[0,-52,47],'translation':[0,2.3,0],'scale':[0.61,0.61,0.61]},
    'thirdperson_lefthand':{'rotation':[0,52,-47],'translation':[0,2.3,0],'scale':[0.61,0.61,0.61]},
}
for name in TOOLS:
    picture=pixel_images[name]
    # Redesenhar o volume 3D conforme a silhueta NOVA, não a antiga.
    sample=[[picture[2*y+1][2*x+1] for x in range(16)] for y in range(16)]
    opaque=[[sample[y][x][3]>0 for x in range(16)] for y in range(16)]
    elements=[]
    for y in range(16):
        x=0
        while x<16:
            if not opaque[y][x]:
                x+=1
                continue
            color=sample[y][x]
            ice=color[2]>color[0]+18 and color[1]>color[0]+8 and color[2]>150
            first=x
            x+=1
            while x<16 and opaque[y][x]:
                other=sample[y][x]
                same=(other[2]>other[0]+18 and other[1]>other[0]+8 and other[2]>150)==ice
                if not same:break
                x+=1
            depth=2.0 if ice else 1.5
            side='#ice' if ice else '#metal'
            faces={'north':{'texture':'#layer0','uv':[first,y,x,y+1]},
                   'south':{'texture':'#layer0','uv':[first,y,x,y+1]},
                   'west':{'texture':side,'uv':[0,0,16,16]},
                   'east':{'texture':side,'uv':[0,0,16,16]},
                   'up':{'texture':side,'uv':[0,0,16,16]},
                   'down':{'texture':side,'uv':[0,0,16,16]}}
            elements.append({'from':[first,15-y,8-depth/2],
                             'to':[x,16-y,8+depth/2],
                             'faces':faces})
    assert 10<len(elements)<160,(name,len(elements))
    write_json(ROOT/'models/item'/(name+'_held.json'),{
        'ambientocclusion':False,'gui_light':'front',
        'textures':{'particle':'modcentral:textura/'+name,
                    'layer0':'modcentral:textura/'+name,
                    'ice':'modcentral:item/ice_side','metal':'modcentral:item/metal_side'},
        'elements':elements,'display':DISPLAY})
    # Mantém 2D no inventário e hotbar; 3D na mão.
    definition=json.loads((ROOT/'items'/(name+'.json')).read_text(encoding='utf-8'))
    assert definition['model']['type']=='minecraft:select'
    write_json(ROOT/'items'/(name+'.json'),definition)
    print(name,'elementos 3D',len(elements))

print('ModCentral 1.6.0: 8 PNGs 32x32 carregados de assets/modcentral/textures/textura/')
