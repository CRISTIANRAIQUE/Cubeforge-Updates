#!/usr/bin/env python3
"""Restore the five exact final 32x32 user sprites during the clean Gradle build."""
from pathlib import Path
import base64, hashlib, io, zipfile, zlib
root=Path('src/main/resources/assets/modcentral/textures/textura')
expected={
 'espada_cristal_azul.png':'5d94bc761a4a',
 'machado_cristal_azul.png':'f2e79d1aa4d3',
 'picareta_cristal_azul.png':'d4059167326f',
 'pa_cristal_azul.png':'e5500d746f50',
 'enxada_cristal_azul.png':'d3862e5a74ca',
}
raw=zlib.decompress(base64.b85decode(Path('latest_tool_textures.b85').read_text(encoding='ascii').strip()))
with zipfile.ZipFile(io.BytesIO(raw)) as z:
    assert set(z.namelist())==set(expected)
    for filename,sha in expected.items():
        data=z.read(filename)
        assert data[:8]==b'\x89PNG\r\n\x1a\n', filename
        assert int.from_bytes(data[16:20],'big')==32 and int.from_bytes(data[20:24],'big')==32
        assert hashlib.sha256(data).hexdigest().startswith(sha),(filename,'hash altered')
        target=root/filename
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(data)
        print('Restaurada textura',filename,len(data))
