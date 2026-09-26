"""Exercise XeTeX's three ICU converters using ICU 73 and external HNP data."""
import ctypes
import json
import sys

icu = ctypes.CDLL('libicuuc.so.73')
open_converter = icu.ucnv_open_73
open_converter.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_int32)]
open_converter.restype = ctypes.c_void_p
close_converter = icu.ucnv_close_73
close_converter.argtypes = [ctypes.c_void_p]
error_name = icu.u_errorName_73
error_name.argtypes = [ctypes.c_int32]
error_name.restype = ctypes.c_char_p
results = []
for name in ('macintosh', 'UTF16BE', 'UTF8'):
    error = ctypes.c_int32(0)
    converter = open_converter(name.encode(), ctypes.byref(error))
    results.append(dict(converter=name, opened=bool(converter), error=error.value,
                        error_name=error_name(error.value).decode()))
    if converter:
        close_converter(converter)
print(json.dumps(results, indent=2))
if sys.argv[1] == 'success':
    assert all(r['opened'] and r['error'] == 0 for r in results)
else:
    assert not results[0]['opened'] and results[0]['error'] > 0
