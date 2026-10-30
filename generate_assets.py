#!/usr/bin/env python3
# Gera texturas originais em pixel art e arquivos de dados, sem dependências.
from pathlib import Path
import json, struct, zlib, random
rng=random.Random(263)
base=Path("src/main/resources")
assets=base/"assets/modcentral"
data=base/"data"
def write_json(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding="utf-8")
def save_png(path,pixels):
    h=len(pixels);w=len(pixels[0])
    raw=b"".join(b"\0"+b"".join(bytes(pixel) for pixel in row) for row in pixels)
    def chunk(tag,value):return struct.pack(">I",len(value))+tag+value+struct.pack(">I",zlib.crc32(tag+value)&0xffffffff)
    png=b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",struct.pack(">IIBBBBB",w,h,8,6,0,0,0))+chunk(b"IDAT",zlib.compress(raw,9))+chunk(b"IEND",b"")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(png)
T=(0,0,0,0)
outline=(18,19,36,255)
metal=(51,54,79,255)
purple=(96,56,160,255)
gold=(250,185,60,255)
blue=(26,117,227,255)
bright=(37,230,253,255)
white=(192,252,255,255)
crystal=[[T for x in range(16)] for y in range(16)]
def draw(p,x,y,c):
    if 0<=x<16 and 0<=y<16:p[y][x]=c
for y in range(2,14):
    for x in range(3,13):
        d=abs(x-8)*1.2+abs(y-7)*0.8
        if d<6.5:draw(crystal,x,y,outline if d>5.5 else (blue if x<=8 else bright))
for y in range(4,10):
    for x in range(7,9):draw(crystal,x,y,white)
save_png(assets/"textures/item/cristal_azul.png",crystal)
sword=[[T for x in range(16)] for y in range(16)]
for i in range(9):
    x,y=12-i,2+i
    draw(sword,x-1,y,outline)
    draw(sword,x,y,blue)
    draw(sword,x+1,y,bright)
    if i<6:draw(sword,x+2,y,white)
for x,y in [(4,10),(5,9),(5,11),(6,10),(3,11)]:draw(sword,x,y,gold)
for i in range(5):
    draw(sword,5-i,10+i,outline)
    draw(sword,6-i,10+i,purple)
draw(sword,1,15,gold)
save_png(assets/"textures/item/espada_cristal_azul.png",sword)
for name,deep in [("minerio_cristal_azul",False),("minerio_cristal_profundo",True)]:
    tex=[]
    for y in range(16):
        row=[]
        for x in range(16):
            z=rng.randrange(7)
            shade= (48+z*3,49+z*3,57+z*3,255) if deep else (103+z*5,105+z*5,110+z*5,255)
            row.append(shade)
        tex.append(row)
    veins=[(3,4),(4,4),(4,5),(3,6),(5,6),(11,2),(12,3),(11,4),(10,4),(9,9),(10,9),(10,10),(12,11),(3,12),(4,11),(5,12)]
    for x,y in veins:
        draw(tex,x,y,bright)
        if (x+y)%3==0:draw(tex,x+1,y,blue)
    for x,y in [(4,4),(11,3),(10,9),(4,12)]:draw(tex,x,y,white)
    save_png(assets/("textures/block/"+name+".png"),tex)
    write_json(assets/("blockstates/"+name+".json"),{"variants":{"":{"model":"modcentral:block/"+name}}})
    write_json(assets/("models/block/"+name+".json"),{"parent":"minecraft:block/cube_all","textures":{"all":"modcentral:block/"+name}})
    write_json(assets/("items/"+name+".json"),{"model":{"type":"minecraft:model","model":"modcentral:block/"+name}})
    write_json(data/("modcentral/loot_table/blocks/"+name+".json"),{"type":"minecraft:block","pools":[{"rolls":1,"entries":[{"type":"minecraft:item","name":"modcentral:cristal_azul"}]}]})
for name,parent in [("espada_cristal_azul","handheld"),("cristal_azul","generated")]:
    write_json(assets/("models/item/"+name+".json"),{"parent":"minecraft:item/"+parent,"textures":{"layer0":"modcentral:item/"+name}})
    write_json(assets/("items/"+name+".json"),{"model":{"type":"minecraft:model","model":"modcentral:item/"+name}})
write_json(assets/"lang/pt_br.json",{
 "creativeTab.modcentral.minerios_espadas":"Cubeforge: Minérios e Espadas",
 "item.modcentral.cristal_azul":"Cristal Azul",
 "item.modcentral.espada_cristal_azul":"Espada de Cristal Azul",
 "block.modcentral.minerio_cristal_azul":"Minério de Cristal Azul",
 "block.modcentral.minerio_cristal_profundo":"Minério de Cristal Profundo"
})
write_json(assets/"lang/en_us.json",{
 "creativeTab.modcentral.minerios_espadas":"Cubeforge: Ores and Swords",
 "item.modcentral.cristal_azul":"Blue Crystal",
 "item.modcentral.espada_cristal_azul":"Blue Crystal Sword",
 "block.modcentral.minerio_cristal_azul":"Blue Crystal Ore",
 "block.modcentral.minerio_cristal_profundo":"Deep Blue Crystal Ore"
})
write_json(data/"minecraft/tags/block/mineable/pickaxe.json",{"values":["modcentral:minerio_cristal_azul","modcentral:minerio_cristal_profundo"]})
write_json(data/"minecraft/tags/block/needs_iron_tool.json",{"values":["modcentral:minerio_cristal_azul","modcentral:minerio_cristal_profundo"]})
write_json(data/"minecraft/tags/item/swords.json",{"values":["modcentral:espada_cristal_azul"]})
write_json(data/"modcentral/recipe/espada_cristal_azul.json",{
 "type":"minecraft:crafting_shaped","category":"equipment",
 "pattern":["C","C","S"],"key":{"C":"modcentral:cristal_azul","S":"minecraft:stick"},
 "result":{"id":"modcentral:espada_cristal_azul","count":1}
})
write_json(base/"pack.mcmeta",{"pack":{"description":"ModCentral - Fabric 26.3","min_format":97,"max_format":121}})
