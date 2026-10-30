#!/usr/bin/env python3
"""Sprites referenciais Opção 5 + modelos volumétricos de itens para Minecraft Java 26.3."""
from pathlib import Path
import json, struct, zlib

ROOT = Path("src/main/resources/assets/modcentral")
ITEMS = {
    "espada_cristal_azul": """
0000000000000003
0000000000000039
0000000000000F9B
000000000000FAB9
00000000000FAB97
000000000FBB897F
00000000FAB89710
0003F0001A78AF00
000F9111B8891000
0000E17A7A810000
000019479F100000
0000179111000000
0000D31876100000
0033210117810000
0DB4100001710000
0D8F000000110000
""",
    "machado_cristal_azul": """
0000000000000000
00000000CEF00000
00000003BB710000
0000000AB9811000
000000FB88621000
0000001898911100
0000000179B97F10
00000001E29A8BF0
0000000C2178B810
0000001110F89F00
000002D3018AF000
00012C1000110000
0013C10000000000
0FB1100000000000
0AA1000000000000
0970000000000000
""",
    "picareta_cristal_azul": """
0000000000000000
0000004FFF100000
000044BA997F0100
0003BA8987B82100
0000FF33F79B9200
000000001177B100
000000001EC197F0
00000001CC114740
000000232100FA60
000000321000CB60
000001E100000B70
0000171000000A50
0001C33000000110
0D18210000000000
0B91100000000000
097F000000000000
""",
    "pa_cristal_azul": """
0000000000000000
0000000000004FF0
000000000004BBA3
00000000007BAA93
00000000FB98B792
00000000FBA7B792
0000000F888B98F0
000000001E498400
00000001C319F000
0000001E210F0000
0000013C10000000
0000132100000000
0001321000000000
00F8310000000000
0FB4100000000000
0F9F000000000000
""",
    "enxada_cristal_azul": """
0000000000000000
0000000004ED0000
00000003879BF031
00000000FFFA9FD1
000000000009B911
0000000000015987
00000000001D1B9A
0000000001911FB9
000000001C2100F1
0000000131100000
0000001AC1000000
000001A510000000
00000C2100000000
000CB10000000000
000FA10000000000
0001900000000000
""",
    "cristal_azul": """
0000000000000000
0000000004F00000
000000003AAF0000
000000049BB6F000
00000004BBA75300
0000004BBAA69100
0000049B9AA776F0
000D49B99BB7799F
000DFAB99AA77A7F
000DF86BABB7A671
00001877ABB8A681
00000F877BB86810
000000F87AA86F00
0000000F8AA6F000
00000000F99F0000
000000000F100000
"""
}
ORE = {
    "minerio_cristal_azul": """
4434A4B34CE89434
5434A4A34DFEA564
4444E4543DFEB564
4444C4544DDFD333
3433B4544DDED333
5DD4443348DFD333
5DD44433C34DEB44
47543333D33DEB44
44444A44D34DEB44
3443DC455655C4C5
4443EC45464AB4C5
433CFDB3354AB455
534CFDC33433CE44
533CFDC33433DE44
644DB5C46645CE55
644C444466554755
""",
    "minerio_cristal_profundo": """
12102B0003101000
10011B000FEA1321
100E02009FEB1321
012D1421DEEC9000
01392321DDFD9000
13201232CDFD9000
1D01000021CFC111
1D010000D1CFC111
00093000D1CFC001
011BC012339D9CA3
010DC012329C2CA2
10BFC901329C11A2
20CFDB000001F501
10CFDB000012F411
31CA3B121211E501
31B321123321D412
"""
}
PALETTE = {
    c: rgb + (255,) for c, rgb in zip("123456789ABCDEF", [
       (25,36,61), (45,55,78), (69,81,107), (54,92,146),
       (57,118,189), (74,148,218), (105,171,233), (137,196,238),
       (182,223,251), (219,245,254), (244,253,255),
       (96,109,129), (129,144,165), (169,188,208),
       (34,61,96)
    ])
}
ORE_PALETTE = {c: rgb + (255,) for c, rgb in zip("0123456789ABCDEF", [
    (36,42,54),(49,54,66),(60,66,79),(73,79,91),
    (89,95,106),(105,110,121),(119,124,134),(137,143,153),
    (152,160,171),(40,80,128),(60,110,165),(80,142,207),
    (107,179,236),(151,211,250),(210,241,255),(243,253,255)
])}
TRANSPARENT = (0,0,0,0)

def rows_for(encoded):
    rows=[line.strip() for line in encoded.strip().splitlines() if line.strip()]
    if len(rows)!=16 or any(len(line)!=16 for line in rows):
        raise ValueError("Textura precisa ter exatamente 16x16")
    return rows

def save_rgba_png(path, pixels):
    h=len(pixels)
    w=len(pixels[0])
    raw=b"".join(b"\x00"+b"".join(bytes(p) for p in row) for row in pixels)
    def chunk(tag, payload):
        return struct.pack(">I",len(payload))+tag+payload+struct.pack(">I",zlib.crc32(tag+payload)&0xffffffff)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",struct.pack(">IIBBBBB",w,h,8,6,0,0,0))+chunk(b"IDAT",zlib.compress(raw,9))+chunk(b"IEND",b""))

def save_json(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,separators=(",",":")),encoding="utf-8")

def model3d(name, grid):
    # Minecraft resolve os elementos como cubóides reais no inventário, no chão
    # e nas mãos (primeira e terceira pessoa); textura da face reproduz o pixel art.
    elements=[]
    for y,row in enumerate(grid):
        for x,code in enumerate(row):
            if code=="0": continue
            # Espessura perceptível de 2,5 unidades na peça, 3 para cabo e guarda.
            # Mantém o desenho original 16x16 na face frontal e no inventário.
            thickness = 3.0 if code in "123CDEF" else 2.0
            lo = round(8-thickness/2,2)
            hi = round(8+thickness/2,2)
            uv=[x,y,x+1,y+1]
            faces={f:{"uv":uv,"texture":"#layer0"} for f in
                ("north","south","east","west","up","down")}
            elements.append({
              "from":[x,15-y,lo],
              "to":[x+1,16-y,hi],
              "faces":faces
            })
    # Handheld fornece as transformações corretas de mão no jogo Vanilla.
    model={
      "parent":"minecraft:item/handheld",
      "gui_light":"front",
      "textures":{"layer0":"modcentral:item/"+name},
      "elements":elements,
      "display":{
          "gui":{"rotation":[0,0,0],"translation":[0,0,0],"scale":[1,1,1]},
          "ground":{"rotation":[0,0,0],"translation":[0,2,0],"scale":[0.5,0.5,0.5]},
          "fixed":{"rotation":[0,0,0],"translation":[0,0,0],"scale":[0.9,0.9,0.9]},
          "thirdperson_righthand":{"rotation":[0,-90,55],"translation":[0,4,0.5],"scale":[0.85,0.85,0.85]},
          "thirdperson_lefthand":{"rotation":[0,90,-55],"translation":[0,4,0.5],"scale":[0.85,0.85,0.85]},
          "firstperson_righthand":{"rotation":[0,-90,25],"translation":[1.13,3.2,1.13],"scale":[0.82,0.82,0.82]},
          "firstperson_lefthand":{"rotation":[0,90,-25],"translation":[1.13,3.2,1.13],"scale":[0.82,0.82,0.82]}
      }
    }
    save_json(ROOT/("models/item/"+name+".json"),model)
    print("Modelo 3D:",name,"elementos:",len(elements))
    if not elements:raise ValueError("Modelo 3D vazio")

for name,encoded in ITEMS.items():
    rows=rows_for(encoded)
    pixel_grid=[[PALETTE.get(c,TRANSPARENT) for c in row] for row in rows]
    save_rgba_png(ROOT/("textures/item/"+name+".png"),pixel_grid)
    model3d(name,rows)

for name,encoded in ORE.items():
    rows=rows_for(encoded)
    pixel_grid=[[ORE_PALETTE[c] for c in row] for row in rows]
    save_rgba_png(ROOT/("textures/block/"+name+".png"),pixel_grid)

print("Opção 5: 8 texturas atualizadas; 6 modelos volumétricos 3D.")
