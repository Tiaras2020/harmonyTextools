"""Test a unique generated font through the production importer and Fontconfig."""
import hashlib, json, os, pathlib, subprocess, tempfile, zipfile
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

root = pathlib.Path(os.environ['DELIVERY_ROOT'])
repo = pathlib.Path(os.environ['BUILD_REPO'])
out = root/'validation/resources'
cli = out/'resource-cli'
with tempfile.TemporaryDirectory(prefix='resource-font-') as temp:
    temp = pathlib.Path(temp)
    font = temp/'HarmonyResourceTest.ttf'
    fb = FontBuilder(1000, isTTF=True)
    fb.setupGlyphOrder(['.notdef', 'space', 'A'])
    fb.setupCharacterMap({32:'space', 65:'A'})
    glyphs = {}
    for name in ['.notdef','space','A']:
        pen = TTGlyphPen(None)
        if name == 'A':
            pen.moveTo((50,0)); pen.lineTo((300,700)); pen.lineTo((550,0)); pen.closePath()
        glyphs[name] = pen.glyph()
    fb.setupGlyf(glyphs)
    fb.setupHorizontalMetrics({name:(600,0) for name in glyphs})
    fb.setupHorizontalHeader(ascent=800, descent=-200)
    fb.setupNameTable({'familyName':'Harmony Resource Test','styleName':'Regular',
                      'uniqueFontIdentifier':'HarmonyResourceTest-1', 'fullName':'Harmony Resource Test',
                      'psName':'HarmonyResourceTest-Regular'})
    fb.setupOS2(sTypoAscender=800,sTypoDescender=-200,usWinAscent=800,usWinDescent=200)
    fb.setupPost(); fb.save(font)
    data = font.read_bytes(); name = 'texmf/fonts/truetype/harmony-test/HarmonyResourceTest.ttf'
    manifest = {'schema':1,'profile':'additive-v1','id':'font-test','version':'1',
                'compatibilityId':json.loads((root/'texstudio-harmony/release.json').read_text())['compatibilityId'],
                'files':{name:{'size':len(data),'sha256':hashlib.sha256(data).hexdigest()}}}
    archive = temp/'font.zip'
    with zipfile.ZipFile(archive,'w') as z:
        z.writestr('manifest.json',json.dumps(manifest)); z.writestr(name,data)
    def run(*args): return subprocess.check_output([str(cli),*map(str,args)],text=True).strip()
    store = temp/'中文 fonts'
    ident = run('import',store,archive)
    run('activate',store,ident)
    dist = repo/'build/build-texlive-ohos-dist'
    env = dict(os.environ, **json.loads(run('environment',store,dist,ident)))
    found = subprocess.check_output(['fc-match','-f','%{file}', 'Harmony Resource Test'],env=env,text=True)
    assert str(store/'resources'/ident) in found, found
    env_builtin = dict(os.environ, **json.loads(run('environment',store,dist,'builtin')))
    fallback = subprocess.check_output(['fc-match','-f','%{file}', 'Harmony Resource Test'],env=env_builtin,text=True)
    assert str(store/'resources'/ident) not in fallback
    assert env['TEXMFVAR'] != env_builtin['TEXMFVAR']
    report = {'passed':True,'uniqueImportedFontFound':True,'rollbackExcludesFont':True,'isolatedCache':True}
    (out/'font-tests.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report)
