"""Local TLS acceptance with explicit CA trust and negative certificate checks."""
import hashlib,http.server,json,os,pathlib,ssl,subprocess,threading
root=pathlib.Path(__file__).resolve().parents[1];repo=pathlib.Path(os.environ['BUILD_REPO']);out=root/'validation/biber/tls';out.mkdir(exist_ok=True)
work=repo/'build/biber-tls-test';work.mkdir(exist_ok=True);cert=work/'cert.pem';key=work/'key.pem'
with (out/'certificate-generation.log').open('w') as log:
    subprocess.run(['openssl','req','-x509','-newkey','rsa:2048','-nodes','-keyout',str(key),'-out',str(cert),'-days','2','-subj','/CN=localhost','-addext','subjectAltName=DNS:localhost'],stdout=log,stderr=subprocess.STDOUT,check=True)
class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        body=b'@article{ohos_tls_fixture,title={Verified local TLS}}\n';self.send_response(200);self.end_headers();self.wfile.write(body)
    def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler)
context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);context.load_cert_chain(cert,key);server.socket=context.wrap_socket(server.socket,server_side=True)
thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
runtime=repo/'build/biber-perl-5.40.3/stage/data/service/hnp/texlive.org/texlive_1.0.18'
env=os.environ.copy();env['LC_ALL']='en_US.UTF-8';env['PERL5LIB']=':'.join(map(str,[repo/'build/biber-runtime/lib',runtime/'lib/perl5/5.40.3',runtime/'lib/perl5/5.40.3/aarch64-linux']))
try:
    p=subprocess.run(['qemu-aarch64','-L',str(repo/'build/perl-ohos-5.40.3/qemu-root'),str(runtime/'bin/perl'),str(root/'validation/biber/tls-smoke.pl'),str(server.server_port),str(cert)],env=env,capture_output=True,timeout=120)
finally:server.shutdown();server.server_close();thread.join()
(out/'stdout.txt').write_bytes(p.stdout);(out/'stderr.txt').write_bytes(p.stderr)
assert p.returncode==0,p.stderr.decode(errors='replace')
report=json.loads(p.stdout);assert report['passed'];report['interpreterSha256']=hashlib.sha256((runtime/'bin/perl').read_bytes()).hexdigest();report['scope']='OHOS Perl under QEMU against local TLS fixture, not device HTTPS validation'
(out/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
