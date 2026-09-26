"""Reviewed 1.0.19 runtime configuration transformations (baseline stays frozen)."""
def texmf_config(text):
    old='TEXFONTMAPS = .;$TEXMFDIST/fonts/map/{pdftex,dvips,glyphlist}/{updmap,}//'
    assert text.count(old)==1
    text=text.replace(old,old.replace('pdftex,dvips,glyphlist','pdftex,dvips,dvipdfmx,glyphlist'))
    old='% dvipdfmx\nCMAPFONTS = .;$TEXMFDIST/fonts/cmap//'
    assert text.count(old)==1
    return text.replace(old,'% dvipdfmx\nDVIPDFMXINPUTS = .;$TEXMFDIST/dvipdfmx//\nXDVIPDFMXINPUTS = .;$TEXMFDIST/dvipdfmx//\nCMAPFONTS = .;$TEXMFDIST/fonts/cmap//')

def driver_config(text):
    assert text.count('f kanjix.map')==1
    return text.replace('f kanjix.map','% HarmonyOS: kanjix.map is not shipped; no default Japanese system-font map.\n% f kanjix.map')
