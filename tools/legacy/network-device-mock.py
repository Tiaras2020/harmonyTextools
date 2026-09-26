"""Loopback-only synthetic HTTP/SSE fixture. Never stores headers or API keys."""
import json,ssl,time,threading
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
root=Path(__file__).resolve().parent
class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args): pass
    def do_GET(self):
        data=json.dumps({'data':[{'id':'network-fixture'}]}).encode()
        self.send_response(200); self.send_header('Content-Type','application/json'); self.end_headers(); self.wfile.write(data)
    def do_POST(self):
        raw=self.rfile.read(min(int(self.headers.get('Content-Length','0')),1000000))
        (root/'requests.log').open('a').write(json.dumps({'path':self.path,'bytes':len(raw),'time':time.time()})+'\n')
        if 'error' in self.path:
            self.send_response(401); self.send_header('Content-Type','application/json'); self.end_headers(); self.wfile.write(b'{"error":{"message":"Synthetic unauthorized test"}}'); return
        if 'slow' in self.path: time.sleep(8)
        text='中文流式测试成功；data: 是正文。'
        if 'json' in self.path:
            self.send_response(200); self.send_header('Content-Type','application/json'); self.end_headers()
            self.wfile.write(json.dumps({'choices':[{'message':{'role':'assistant','content':text},'finish_reason':'stop'}]},ensure_ascii=False).encode()); return
        self.send_response(200); self.send_header('Content-Type','text/event-stream'); self.end_headers()
        try:
            self.wfile.write(b': keepalive\n\n'); self.wfile.flush()
            for c in text:
                event=('data: '+json.dumps({'choices':[{'delta':{'content':c}}]},ensure_ascii=False)+'\r\n\r\n').encode()
                # Split in the middle of UTF-8 and JSON, at delays spanning the UI poll.
                for i in range(0,len(event),7):
                    self.wfile.write(event[i:i+7]); self.wfile.flush(); time.sleep(.012)
            self.wfile.write(b'data: [DONE]\n\n'); self.wfile.flush()
        except (BrokenPipeError,ConnectionResetError): pass
for port in (18831,18832):
    server=ThreadingHTTPServer(('127.0.0.1',port),Handler)
    if port==18832:
        ctx=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER); ctx.load_cert_chain(root/'localhost.pem',root/'localhost.key'); server.socket=ctx.wrap_socket(server.socket,server_side=True)
    threading.Thread(target=server.serve_forever,daemon=True).start()
print('Network31 loopback fixtures ready: 18831 HTTP, 18832 untrusted TLS',flush=True)
while True: time.sleep(60)
