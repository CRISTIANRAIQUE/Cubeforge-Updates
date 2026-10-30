#!/usr/bin/env python3
# ModCentral 1.5.0 - Redesenhar espadas e ferramentas sem cortes nos slots.
# Sprites 32x32, margem de 3px e modelos voxel 3D fiéis às silhuetas novas.
from pathlib import Path
import base64, zlib, json, struct
ROOT=Path("src/main/resources/assets/modcentral")
NAMES=["espada_cristal_azul","machado_cristal_azul","picareta_cristal_azul",
       "pa_cristal_azul","enxada_cristal_azul"]
DATA="c-rlkyHNu{42D-LdmlLkPyi`8AsGQ3Pz6H;v;jR3kupOCgfzem0WpEmzV3`q(t;ge4|k!zJ^A*mZ}mGK9iN_@o}XPmTwL8;-o4&Ff80O5JiV>nKUe0@E&vsR#tAwVV+gT>p@U&xap+(K@r`bc2d-g26tDqnAqEgJSnuWEoG|f)#0v&XcnK2r^aO@2Kp#?Z!o)z@TfxH9IRF_O+I3KHeRt-cTs^O~myuA6QCyH|j3~Ad5_L}G=*lH5Sm&T{#K3I=D#xT*m@X&+VZkx51qMz9ctz_1WXh)=E=$662hEbQf_b_oQML$JgUO;ySX>oV1ot{liW<#-s~r#C%GF2z&Fuf4A0FZfQG45^1Av*4DKa>h{dYL^XN1{+v|!^mrYkp6Zo)JQH_U7flqO9*v5ukj;n2k2xEl>)_6DP2k^^IPc>*hj?O44jw%Gd1e^7m)Zw<QD<)#`=F4=#@@8Z9i{r`o<J467)oB>3vWq^8jp5YSLGQhwC3TIH8@f?T7C2R{vf#(5^ZYkdGTLR#5=Ahsj!ev||gs7-Kg5~+&o6u$cgFgSa3m4=3H}m{I<N&aip!q+dnYtM30l~*>5Wk|D12y7K@6V~*)<$A^fEFOwrzh@puFvSy$Q_C7P7&Pe5q$Rl;QaprYZM;#"
raw=zlib.decompress(base64.b85decode(DATA))
nc=raw[0]
palette=[(*raw[1+3*i:4+3*i],255) for i in range(nc)]
bytes_idx=raw[1+3*nc:]
assert len(bytes_idx)==5*32*32, (nc,len(bytes_idx))
T=(0,0,0,0)

def put_json(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
def put_png(path,pixels):
    assert len(pixels)==len(pixels[0])==32
    scan=b"".join(b"\0"+b"".join(bytes(c) for c in row) for row in pixels)
    def ch(t,v):
        return struct.pack(">I",len(v))+t+v+struct.pack(">I",zlib.crc32(t+v)&0xffffffff)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(b"\x89PNG\r\n\x1a\n"+ch(b"IHDR",struct.pack(">IIBBBBB",32,32,8,6,0,0,0))+ch(b"IDAT",zlib.compress(scan,9))+ch(b"IEND",b""))

def side_textures():
    ice=[[(99,151,200,255) if (x+y)%7 else (171,224,251,255) for x in range(32)] for y in range(32)]
    metal=[[(42,57,79,255) if (x//4+y//4)%3 else (79,101,133,255) for x in range(32)] for y in range(32)]
    put_png(ROOT/"textures/item/ice_side.png",ice)
    put_png(ROOT/"textures/item/metal_side.png",metal)

DISPLAY={
    "firstperson_righthand":{"rotation":[0,-56,19],"translation":[0.05,1.15,0.1],"scale":[0.53,0.53,0.53]},
    "firstperson_lefthand":{"rotation":[0,56,-19],"translation":[0.05,1.15,0.1],"scale":[0.53,0.53,0.53]},
    "thirdperson_righthand":{"rotation":[0,-52,47],"translation":[0,2.3,0],"scale":[0.61,0.61,0.61]},
    "thirdperson_lefthand":{"rotation":[0,52,-47],"translation":[0,2.3,0],"scale":[0.61,0.61,0.61]},
}
side_textures()
for i,name in enumerate(NAMES):
    rawpix=bytes_idx[i*1024:(i+1)*1024]
    pixels=[[T if rawpix[y*32+x]==0 else palette[rawpix[y*32+x]-1]
              for x in range(32)] for y in range(32)]
    opaque=[(x,y) for y in range(32) for x in range(32) if pixels[y][x][3]>0]
    assert opaque and min(x for x,y in opaque)>=3 and min(y for x,y in opaque)>=3
    assert max(x for x,y in opaque)<=28 and max(y for x,y in opaque)<=28
    put_png(ROOT/("textures/item/"+name+".png"),pixels)

    # No hotbar e nas abas o arquivo é apenas uma textura pixel art 2D.
    put_json(ROOT/("models/item/"+name+".json"),{
       "parent":"minecraft:item/handheld",
       "textures":{"layer0":"modcentral:item/"+name}
    })
    small=[[next((pixels[2*y+dy][2*x+dx] for dy,dx in ((0,0),(0,1),(1,0),(1,1))
                  if pixels[2*y+dy][2*x+dx][3]>0),T)
            for x in range(16)] for y in range(16)]
    mask=[[small[y][x][3]>0 for x in range(16)] for y in range(16)]
    elements=[]
    for y in range(16):
        for x in range(16):
            if not mask[y][x]:continue
            c=small[y][x]
            ice=(c[2]>c[0]+18 and c[1]>c[0]+10 and c[2]>155)
            thick=2.4 if ice else 1.7
            z0,z1=8-thick/2,8+thick/2
            uv=[x,y,x+1,y+1]
            faces={
                "north":{"texture":"#layer0","uv":uv},
                "south":{"texture":"#layer0","uv":uv}
            }
            for side,dx,dy in [("west",-1,0),("east",1,0),
                               ("up",0,-1),("down",0,1)]:
                xx,yy=x+dx,y+dy
                if xx<0 or xx>=16 or yy<0 or yy>=16 or not mask[yy][xx]:
                    faces[side]={"texture":"#ice" if ice else "#metal","uv":[0,0,16,16]}
            elements.append({
                "from":[x,15-y,z0],"to":[x+1,16-y,z1],"faces":faces
            })
    assert 25<len(elements)<160,(name,len(elements))
    put_json(ROOT/("models/item/"+name+"_held.json"),{
        "ambientocclusion":False,
        "gui_light":"front",
        "textures":{"particle":"modcentral:item/"+name,"layer0":"modcentral:item/"+name,
                    "ice":"modcentral:item/ice_side","metal":"modcentral:item/metal_side"},
        "elements":elements,
        "display":DISPLAY
    })
    put_json(ROOT/("items/"+name+".json"),{
        "model":{"type":"minecraft:select",
                 "property":"minecraft:display_context",
                 "cases":[{"when":["firstperson_righthand","firstperson_lefthand",
                                   "thirdperson_righthand","thirdperson_lefthand"],
                           "model":{"type":"minecraft:model","model":"modcentral:item/"+name+"_held"}}],
                 "fallback":{"type":"minecraft:model","model":"modcentral:item/"+name}}
    })
    print("UPDATED",name,"pixel-art 32x32; voxel elements",len(elements))
