# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['desktop_app.py'],
    pathex=['C:\\Users\\wille\\Downloads\\Fichaje\\backend'],
    binaries=[],
    datas=[('frontend/dist', 'frontend/dist')],
    hiddenimports=['uvicorn.logging', 'uvicorn.loops', 'uvicorn.loops.auto', 'uvicorn.protocols', 'uvicorn.protocols.http', 'uvicorn.protocols.http.auto', 'uvicorn.protocols.http.h11_impl', 'uvicorn.protocols.websockets', 'uvicorn.protocols.websockets.auto', 'uvicorn.lifespan', 'uvicorn.lifespan.on', 'uvicorn.lifespan.off', 'h11', 'email.mime.multipart', 'email.mime.text', 'email.mime.base', 'email.mime.image', 'email.mime.audio', 'email._header_value_parser', 'passlib.handlers.bcrypt', 'bcrypt', 'asyncio', 'asyncio.events', 'asyncio.base_events', 'multipart', 'multipart.multipart'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='FichajeZaragonjg',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:\\Users\\wille\\Downloads\\Fichaje\\assets\\fingerprint.ico'],
)
