#!/usr/bin/env python3
# Cubeforge: Opção 5 - textura gelada azul/prata, 16x16 pixel art original
# Mantém os IDs existentes e acrescenta ferramentas sem depender de bibliotecas externas.
from pathlib import Path
import json, struct, zlib, random, math

base = Path("src/main/resources")
assets = base / "assets/modcentral"
data = base / "data"
rng = random.Random(2635)

def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

def save_png(path, pixels):
    height, width = len(pixels), len(pixels[0])
    assert width in (16,32) and height in (16,32)
    pixels_b = b"".join(b"\x00" + b"".join(bytes(p) for p in row) for row in pixels)
    def chunk(tag, payload):
        return struct.pack(">I",len(payload)) + tag + payload + struct.pack(">I", zlib.crc32(tag + payload) & 0xffffffff)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR",struct.pack(">IIBBBBB",width,height,8,6,0,0,0)) + chunk(b"IDAT",zlib.compress(pixels_b,9)) + chunk(b"IEND",b""))

T = (0,0,0,0)
O = (19,31,54,255)           # azul quase preto no contorno
D = (43,60,84,255)           # contorno secundário
H = (58,67,79,255)           # cabo de ferramentas
G = (101,113,131,255)       # prata
B = (54,112,184,255)        # azul médio
C = (96,171,235,255)        # azul gelo
I = (158,217,255,255)       # gelo luminoso
W = (232,251,255,255)       # branco cristalino
S = (191,202,211,255)       # aço prateado

def blank(): return [[T for _ in range(16)] for _ in range(16)]
def dot(p,x,y,c):
    if 0<=x<16 and 0<=y<16: p[y][x]=c
def block(p,x0,y0,x1,y1,color):
    for y in range(y0,y1+1):
        for x in range(x0,x1+1):
            dot(p,x,y,color)
def line(p,x0,y0,x1,y1,color,wide=1):
    steps=max(abs(x1-x0),abs(y1-y0))
    for z in range(steps+1):
        x=round(x0+(x1-x0)*z/max(1,steps))
        y=round(y0+(y1-y0)*z/max(1,steps))
        for dx in range(wide):
            dot(p,x+dx,y,color)

# Gem faceted like the chosen ice-blue preview.
gem=blank()
for y in range(1,15):
    for x in range(3,14):
        if y<5: left=8-(y+1); right=8+(y+1)
        elif y<=10: left=4; right=12
        else: left=4+(y-10); right=12-(y-10)
        if left<=x<=right:
            edge=(x==left or x==right or y==1 or y==14)
            color=O if edge else (B if x<7 else C if x>=9 else I)
            dot(gem,x,y,color)
for x,y in [(6,3),(7,3),(6,4),(7,4),(6,5),(7,5),(6,6),(6,7),(7,7),(8,3),(8,4),(9,5),(8,6),(8,7),(8,8),(8,9),(8,10),(8,11)]:
    dot(gem,x,y,W)
for x,y in [(10,7),(10,8),(11,9),(9,11),(8,12)]: dot(gem,x,y,I)
save_png(assets/"textures/item/cristal_azul.png",gem)

# Weapon drawn at authentic 16x16 Minecraft scale, with frosted blade, silver guard.
sword=blank()
line(sword,1,14,6,9,O,3)
line(sword,2,14,6,10,H,1)
line(sword,3,13,5,11,S)
dot(sword,1,15,O);dot(sword,2,15,I)
# Blade polygon along NE diagonal, with dark outline, blue facets and bright ice edge.
for n in range(8):
    x=7+n; y=9-n
    dot(sword,x-1,y+1,O)
    dot(sword,x,y+1,B)
    dot(sword,x,y,C)
    dot(sword,x+1,y,I)
    if n<6: dot(sword,x+1,y-1,W)
    dot(sword,x+2,y-1,O)
dot(sword,14,1,W); dot(sword,15,1,O)
# Crossguard crossing the blade.
for x,y in [(4,9),(5,10),(6,11),(7,12),(4,8),(8,12)]:
    dot(sword,x,y,O)
for x,y in [(4,9),(5,10),(6,11),(7,12)]:
    dot(sword,x,y,S)
dot(sword,5,9,I);dot(sword,7,11,B);dot(sword,6,10,W)
save_png(assets/"textures/item/espada_cristal_azul.png",sword)

def handle(p):
    line(p,2,14,10,6,O,3)
    line(p,3,14,10,7,H)
    line(p,5,12,7,10,G)
    dot(p,2,15,D);dot(p,3,14,C);dot(p,4,13,S)
    dot(p,7,10,S);dot(p,9,8,I)

# Axe: broad silver/icy head, strong silhouette.
axe=blank()
handle(axe)
rows={2:(8,11),3:(6,13),4:(5,13),5:(5,14),6:(5,14),7:(6,13),8:(8,12)}
for y,(a,b) in rows.items():
    for x in range(a,b+1):
        edge=(x==a or x==b or y==2 or y==8)
        dot(axe,x,y,O if edge else (W if x<=7 else I if x<=10 else C))
for x,y in [(7,3),(8,4),(9,5),(8,6),(7,6),(10,3)]:dot(axe,x,y,W)
for x,y in [(12,4),(12,5),(11,7)]:dot(axe,x,y,B)
save_png(assets/"textures/item/machado_cristal_azul.png",axe)

# Pickaxe: curved frozen arc with double pointed working ends.
pick=blank()
handle(pick)
for x in range(3,15):
    y=4 if 5<=x<=12 else 5
    dot(pick,x,y-1,O)
    dot(pick,x,y,I if 6<=x<=12 else C)
    dot(pick,x,y+1,B)
for x,y in [(11,6),(12,7),(13,8),(13,9),(14,10),(3,6),(2,7)]:
    dot(pick,x,y,O)
for x,y in [(12,6),(12,8),(13,9),(4,5),(3,6)]:
    dot(pick,x,y,C)
for x in (6,7,8,9):dot(pick,x,4,W)
save_png(assets/"textures/item/picareta_cristal_azul.png",pick)

# Shovel: clear rounded tip and bright icy central bevel.
shovel=blank()
handle(shovel)
shovel_shape={2:(10,11),3:(9,12),4:(8,13),5:(8,13),6:(8,13),7:(9,12),8:(10,11)}
for y,(a,b) in shovel_shape.items():
    for x in range(a,b+1):
        dot(shovel,x,y,O if (x==a or x==b or y in (2,8)) else (W if x<=10 else I if x==11 else B))
for x,y in [(10,3),(10,4),(9,5),(10,6),(11,5)]:dot(shovel,x,y,W)
save_png(assets/"textures/item/pa_cristal_azul.png",shovel)

# Hoe: horizontal prong, unlike the shovel.
hoe=blank()
handle(hoe)
for x in range(6,14):
    for y in range(3,6):
        dot(hoe,x,y,O if y==3 or x==6 or x==13 else (W if y==4 and x<11 else C))
for x,y in [(12,6),(13,6),(13,7),(14,7),(14,8)]:
    dot(hoe,x,y,O)
for x,y in [(12,5),(12,6),(13,7)]:dot(hoe,x,y,I)
save_png(assets/"textures/item/enxada_cristal_azul.png",hoe)

# Gray stone and deepslate with large icy-white crystal clusters, low-noise background.
for name,deep in (("minerio_cristal_azul",False),("minerio_cristal_profundo",True)):
    tex=[]
    for y in range(16):
        row=[]
        for x in range(16):
            z=rng.randrange(-14,15)
            if deep:
                v=49 + z + (9 if ((x+y)//4)%3==0 else 0)
                color=(v-5,v-2,v+10,255)
            else:
                v=113 + z + (8 if (x//4+y//4)%2==0 else 0)
                color=(v,v+3,v+10,255)
            row.append(color)
        tex.append(row)
    # crystalline ore inclusions, custom pattern for independent identity.
    clusters=[
       [(2,2),(3,2),(2,3),(3,3),(4,3),(3,4),(4,4)],
       [(10,1),(11,1),(10,2),(11,2),(12,2),(11,3)],
       [(8,6),(9,6),(8,7),(9,7),(10,7),(9,8)],
       [(1,10),(2,10),(2,11),(3,11),(2,12)],
       [(11,11),(12,11),(11,12),(12,12),(13,12),(12,13)],
       [(6,13),(7,13),(6,14),(7,14)]
    ]
    for idx,cluster in enumerate(clusters):
        for j,(x,y) in enumerate(cluster):
            c=(D if j==0 else B if j%4==0 else C if j%3 else I)
            dot(tex,x,y,c)
        hx,hy=cluster[min(2,len(cluster)-1)]
        dot(tex,hx,hy,W)
        if idx%2==0: dot(tex,hx+1,hy,I)
    # stone surface fissures, avoiding ore highlights
    for x,y in [(0,5),(1,5),(5,0),(6,0),(7,10),(8,10),(15,7),(14,7),(4,15)]:
        dot(tex,x,y, (32,43,58,255) if deep else (82,97,114,255))
    save_png(assets/("textures/block/"+name+".png"),tex)
    write_json(assets/("blockstates/"+name+".json"),{"variants":{"":{"model":"modcentral:block/"+name}}})
    write_json(assets/("models/block/"+name+".json"),{"parent":"minecraft:block/cube_all","textures":{"all":"modcentral:block/"+name}})
    write_json(assets/("items/"+name+".json"),{"model":{"type":"minecraft:model","model":"modcentral:block/"+name}})
    write_json(data/("modcentral/loot_table/blocks/"+name+".json"),{
       "type":"minecraft:block","pools":[{"rolls":1,"entries":[{"type":"minecraft:item","name":"modcentral:cristal_azul"}]}]})

tools=["espada_cristal_azul","machado_cristal_azul","picareta_cristal_azul","pa_cristal_azul","enxada_cristal_azul"]
for name in tools+["cristal_azul"]:
    parent="handheld" if name in tools else "generated"
    write_json(assets/("models/item/"+name+".json"),
      {"parent":"minecraft:item/"+parent,"textures":{"layer0":"modcentral:item/"+name}})
    write_json(assets/("items/"+name+".json"),
      {"model":{"type":"minecraft:model","model":"modcentral:item/"+name}})

for language,names in [
    ("pt_br",["Cristal de Gelo Azul","Espada de Cristal de Gelo","Machado de Cristal de Gelo",
              "Picareta de Cristal de Gelo","Pá de Cristal de Gelo","Enxada de Cristal de Gelo",
              "Minério de Cristal de Gelo","Minério Profundo de Cristal de Gelo","Cubeforge: Minérios e Espadas"]),
    ("en_us",["Blue Ice Crystal","Ice Crystal Sword","Ice Crystal Axe",
              "Ice Crystal Pickaxe","Ice Crystal Shovel","Ice Crystal Hoe",
              "Ice Crystal Ore","Deepslate Ice Crystal Ore","Cubeforge: Ores and Swords"])
]:
    dictionary={
       "item.modcentral.cristal_azul":names[0],
       "item.modcentral.espada_cristal_azul":names[1],
       "item.modcentral.machado_cristal_azul":names[2],
       "item.modcentral.picareta_cristal_azul":names[3],
       "item.modcentral.pa_cristal_azul":names[4],
       "item.modcentral.enxada_cristal_azul":names[5],
       "block.modcentral.minerio_cristal_azul":names[6],
       "block.modcentral.minerio_cristal_profundo":names[7],
       "creativeTab.modcentral.minerios_espadas":names[8],
    }
    write_json(assets/("lang/"+language+".json"),dictionary)

# Block tags preserve harvest behaviour from prior version
write_json(data/"minecraft/tags/block/mineable/pickaxe.json",
 {"values":["modcentral:minerio_cristal_azul","modcentral:minerio_cristal_profundo"]})
write_json(data/"minecraft/tags/block/needs_iron_tool.json",
 {"values":["modcentral:minerio_cristal_azul","modcentral:minerio_cristal_profundo"]})
for folder,values in [
    ("swords",["espada_cristal_azul"]),
    ("axes",["machado_cristal_azul"]),
    ("pickaxes",["picareta_cristal_azul"]),
    ("shovels",["pa_cristal_azul"]),
    ("hoes",["enxada_cristal_azul"])
]:
    write_json(data/("minecraft/tags/item/"+folder+".json"),
       {"values":["modcentral:"+name for name in values]})

# Vanilla crafting recipes: 2/3 blue crystals plus sticks.
recipes={
  "espada_cristal_azul":[" C "," C "," S "],
  "machado_cristal_azul":["CC ","CS "," S "],
  "picareta_cristal_azul":["CCC"," S "," S "],
  "pa_cristal_azul":[" C "," S "," S "],
  "enxada_cristal_azul":["CC "," S "," S "]
}
for name, pattern in recipes.items():
    write_json(data/("modcentral/recipe/"+name+".json"),{
       "type":"minecraft:crafting_shaped","category":"equipment","pattern":pattern,
       "key":{"C":"modcentral:cristal_azul","S":"minecraft:stick"},
       "result":{"id":"modcentral:"+name,"count":1}
    })
write_json(base/"pack.mcmeta",{"pack":{"description":"Cubeforge - Opção 5 Gelo Azul (Fabric 26.3)","min_format":97,"max_format":121}})


# =====================================================================
# Cubeforge v1.2.0: Opção 5 refinada + modelos voxel 3D para mão/solo
# =====================================================================
def ice_refine(old, salt):
    """Textura em 32x32 para imagem mais fiel ao cristal de gelo da opção 5.
    Conservar o contorno original e criar sombreamento intra-pixel."""
    r=random.Random(26350+salt)
    shades={
       O:[O,(24,37,62,255)], D:[D,(53,72,99,255)],
       H:[H,(68,78,93,255)],G:[G,S],
       B:[B,(67,125,190,255)],C:[C,(122,185,232,255)],
       I:[I,(174,230,255,255)],W:[W,(247,254,255,255)],
       S:[S,(216,225,234,255)]
    }
    out=[[T for x in range(32)] for y in range(32)]
    for y in range(16):
        for x in range(16):
            c=old[y][x]
            if c==T: continue
            px=x*2;py=y*2
            for dy in range(2):
                for dx in range(2):
                    v=c
                    if c in shades and dx==0 and dy==0 and ((x+y+salt)%3==0):
                        v=shades[c][-1]
                    elif c in shades and dx==1 and dy==1 and c in (W,I,C):
                        v=shades[c][0]
                    out[py+dy][px+dx]=v
    return out

# A arma e as ferramentas mantêm silhuetas reconhecíveis mesmo no hotbar.
sprites={
    "espada_cristal_azul":sword,
    "machado_cristal_azul":axe,
    "picareta_cristal_azul":pick,
    "pa_cristal_azul":shovel,
    "enxada_cristal_azul":hoe,
    "cristal_azul":gem
}
for index,(name,pixels) in enumerate(sprites.items()):
    pix32=ice_refine(pixels,index)
    # Iluminação fria central, em contraste com o cabo de grafite.
    if name=="espada_cristal_azul":
        for x,y in [(25,6),(23,8),(21,10),(19,12),(17,14)]:
            if 0<=y<32 and pix32[y][x]!=T: pix32[y][x]=(247,254,255,255)
    save_png(assets/("textures/item/"+name+".png"),pix32)

# Minérios 32x32: grafite/matriz de pedra com inclusões azul-gelo,
# flocos brancos facetados, bem mais próximo da referência escolhida.
stone_sets={
  False:[(99,106,117,255),(118,123,131,255),(135,140,147,255),
         (110,119,131,255),(83,94,109,255),(149,151,158,255)],
  True:[(34,42,59,255),(48,55,70,255),(59,66,83,255),
        (41,49,65,255),(65,72,86,255),(29,37,51,255)]
}
ore_clusters=[(5,5,3),(19,4,3),(11,12,4),(26,12,3),(4,24,4),
              (17,24,4),(27,27,2),(26,3,2),(11,30,2)]
for name, deep in [("minerio_cristal_azul",False),("minerio_cristal_profundo",True)]:
    random_stone=random.Random(141 if not deep else 918)
    palette=stone_sets[deep]
    ore=[[None for _ in range(32)] for _ in range(32)]
    for yy in range(32):
        for xx in range(32):
            # pedra com microplacas e fraturas, sem ruído de cores excessivo.
            gx=xx//3;gy=yy//3
            region=(gx*13+gy*7+(gx*gy)//3)%len(palette)
            if random_stone.randrange(9)==0:region=(region+1)%len(palette)
            ore[yy][xx]=palette[region]
    for ci,(ox,oy,r) in enumerate(ore_clusters):
        for yy in range(max(0,oy-r),min(32,oy+r+1)):
            for xx in range(max(0,ox-r),min(32,ox+r+1)):
                delta=abs(xx-ox)*1.1+abs(yy-oy)*0.9
                if delta > r+0.4: continue
                if delta > r-0.2:
                    color=(34,75,126,255) if deep else (66,118,166,255)
                elif xx<ox:
                    color=(98,169,227,255)
                elif yy>oy and (xx+yy)%3==0:
                    color=(192,234,255,255)
                else:
                    color=(145,208,255,255)
                ore[yy][xx]=color
        for xx,yy in [(ox,oy),(ox-1,oy),(ox,oy-1)]:
            if 0<=xx<32 and 0<=yy<32:ore[yy][xx]=W
        if ci%2==0:
            for xx,yy in [(ox+1,oy+2),(ox+2,oy+1)]:
                if 0<=xx<32 and 0<=yy<32:ore[yy][xx]=I
    save_png(assets/("textures/block/"+name+".png"),ore)

# Modelos verdadeiramente tridimensionais:
# Cada pixel opaco se torna um pequeno prisma com faces laterais
# visíveis e textura no topo, base e nos lados. Isto difere do
# modelo "handheld" simples, que no jogo é uma lâmina visual plana.
#
# As coordenadas da geometria ficam em 0..16, com espessura 2 a 4
# unidades conforme peça. Um artesanato voxel sem arquivos externos.
hand_display={
    "thirdperson_righthand":{"rotation":[0,-90,55],"translation":[0,4,0],"scale":[0.82,0.82,0.82]},
    "thirdperson_lefthand":{"rotation":[0,90,-55],"translation":[0,4,0],"scale":[0.82,0.82,0.82]},
    "firstperson_righthand":{"rotation":[0,-90,25],"translation":[1.1,3.2,1.1],"scale":[0.72,0.72,0.72]},
    "firstperson_lefthand":{"rotation":[0,90,-25],"translation":[1.1,3.2,1.1],"scale":[0.72,0.72,0.72]},
    "gui":{"rotation":[30,225,0],"translation":[0,0,0],"scale":[0.92,0.92,0.92]},
    "ground":{"translation":[0,2,0],"scale":[0.5,0.5,0.5]},
    "fixed":{"rotation":[0,180,0],"scale":[0.75,0.75,0.75]}
}
def voxel_model(name,pixels):
    elements=[]
    for yy in range(16):
        for xx in range(16):
            if pixels[yy][xx]==T: continue
            color=pixels[yy][xx]
            # cabo mais arredondado; cristal/metal mais espesso.
            is_handle=color in (H,D,G,S)
            z0,z1=(6.5,9.5) if is_handle else (7.0,9.0)
            if name=="cristal_azul": z0,z1=6.5,9.5
            uv=[xx,yy,xx+1,yy+1]
            face={"texture":"#layer0","uv":uv}
            elements.append({
                "from":[xx,15-yy,z0],
                "to":[xx+1,16-yy,z1],
                "faces":{side:face.copy() for side in
                         ("north","south","east","west","up","down")}
            })
    assert 0<len(elements)<256,(name,len(elements))
    model={
       "ambientocclusion":False,
       "gui_light":"side",
       "textures":{"particle":"modcentral:item/"+name,
                   "layer0":"modcentral:item/"+name},
       "elements":elements,
       "display":hand_display
    }
    write_json(assets/("models/item/"+name+".json"),model)
    # Mesmo identificador de item, novo modelo renderizado em todos os contextos.
    write_json(assets/("items/"+name+".json"),{
       "model":{"type":"minecraft:model","model":"modcentral:item/"+name}
    })
for name,pixels in sprites.items():
    voxel_model(name,pixels)
