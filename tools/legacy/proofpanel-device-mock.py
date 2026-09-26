"""Loopback-only synthetic proofreader; logs character counts, never source text."""
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
import json
class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args): pass
    def do_POST(self):
        form=parse_qs(self.rfile.read(int(self.headers['Content-Length'])).decode())
        text=form.get('text',[''])[0]
        print(json.dumps({'characters':len(text),'language':form.get('language')}),flush=True)
        offset=text.find('before')
        matches=[] if offset<0 else [{'offset':offset,'length':6,'message':'Synthetic fixture suggestion','replacements':[{'value':'after'}]}]
        body=json.dumps({'matches':matches}).encode()
        self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(body)
HTTPServer(('127.0.0.1',18834),Handler).serve_forever()
