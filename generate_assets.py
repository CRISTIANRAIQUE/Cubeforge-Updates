#!/usr/bin/env python3
import json,struct,zlib,pathlib
root=pathlib.Path('src/main/resources/assets/modcentral')
items=['espada_aetheric','picareta_aetheric','machado_aetheric','pa_aetheric','cristal_aetheric','fragmento_aetheric','lingote_aetheric','nucleo_aetheric','pedra_aetheric','emblema_mods']
pt=['Espada Aetheric','Picareta Aetheric','Machado Aetheric','Pá Aetheric','Cristal Aetheric','Fragmento Aetheric','Lingote Aetheric','Núcleo Aetheric','Pedra Aetheric','Emblema dos Mods']
en=['Aetheric Sword','Aetheric Pickaxe','Aetheric Axe','Aetheric Shovel','Aetheric Crystal','Aetheric Shard','Aetheric Ingot','Aetheric Core','Aetheric Stone','Mods Emblem']
def png(path,pixels):
    w=len(pixels[0]); h=len(pixels)
    raw=b''.join(b'\x00'+b''.join(bytes(p) for p in row) for row in pixels)
    def chunk(tag,data):return struct.pack('>I',len(data))+tag+data+struct.pack('>I',zlib.crc32(tag+data)&0xffffffff)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b''))
clear=(0,0,0,0); edge=(20,19,35,255);cyan=(45,234,255,255);blue=(28,135,230,255);purple=(108,56,170,255);gold=(245,188,57,255);steel=(100,110,131,255)
for idx,name in enumerate(items):
    pixels=[[clear for _ in range(16)] for _ in range(16)]
    def p(x,y,c):
        if 0<=x<16 and 0<=y<16:pixels[y][x]=c
    if idx==0:
        for i in range(9):p(11-i,2+i,edge);p(12-i,2+i,blue);p(13-i,2+i,cyan)
        for x,y in [(3,10),(4,9),(5,8),(6,7),(7,6)]:p(x,y,cyan)
        for x,y in [(2,10),(3,9),(4,11),(5,10)]:p(x,y,gold)
        for x,y in [(1,14),(2,13),(3,12),(4,11)]:p(x,y,purple)
        p(1,15,gold)
    elif idx in (1,2,3):
        for i in range(9):p(3+i,13-i,edge);p(4+i,13-i,steel)
        if idx==1:
            for x in range(5,15):p(x,3,cyan);p(x,4,blue)
        elif idx==2:
            for x in range(7,13):p(x,4,cyan);p(x,5,blue)
        else:
            for x in range(10,14):
                for y in range(2,6):p(x,y,cyan)
    else:
        palette=[cyan,purple,gold,blue,steel,purple]
        c=palette[(idx-4)%len(palette)]
        for y in range(3,13):
            for x in range(3,13):
                if abs(x-8)+abs(y-8)<=6:p(x,y,edge if abs(x-8)+abs(y-8)>5 else c)
        for y in range(5,9):
            for x in range(6,9):p(x,y,(205,252,255,255))
    png(root/'textures/item'/f'{name}.png',pixels)
    model={'parent':'minecraft:item/handheld' if idx<4 else 'minecraft:item/generated','textures':{'layer0':'modcentral:item/'+name}}
    dest=root/'models/item'/f'{name}.json';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(model))
for locale,names in [('pt_br',pt),('en_us',en)]:
    dic={'itemGroup.modcentral.mods':'Aetheric Arms'}
    dic.update({'item.modcentral.'+name:label for name,label in zip(items,names)})
    path=root/'lang'/f'{locale}.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(dic,ensure_ascii=False,indent=2),encoding='utf8')
