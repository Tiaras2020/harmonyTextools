import importlib.util, json, os, pathlib, socket, subprocess, tempfile, time
root = pathlib.Path(os.environ['DELIVERY_ROOT'])
out = root/'validation/project-cli-1.0.25'
spec = importlib.util.spec_from_file_location('client',root/'tools/texstudioctl.py')
client = importlib.util.module_from_spec(spec); spec.loader.exec_module(client)
with tempfile.TemporaryDirectory() as temp:
    descriptor = pathlib.Path(temp)/'session.json'
    p = subprocess.Popen([str(out/'test-automation'),str(descriptor)])
    try:
        for _ in range(100):
            if descriptor.exists() and descriptor.stat().st_size: break
            time.sleep(.05)
        session = json.loads(descriptor.read_text())
        assert client.request(session,'status')['state'] == 'idle'
        bad = dict(session,token='wrong')
        assert client.request(bad,'status')['error'] == 'unauthorized'
        assert client.request(session,'shell')['error'] == 'unsupported_command'
        with socket.create_connection(('127.0.0.1',session['port']),timeout=2) as s:
            s.sendall(b'invalid\n'); assert b'invalid_json' in s.recv(1024)
        with socket.create_connection(('127.0.0.1',session['port']),timeout=2) as s:
            s.sendall(b'x'*8193); assert s.recv(1024) == b''
        assert client.request(session,'status')['ok']
    finally:
        p.terminate(); p.wait(timeout=5)
(out/'protocol-tests.json').write_text(json.dumps({'passed':True,'checks':['real Qt TCP server and Python client',
    'token rejection','unsupported command','invalid JSON','oversized input','subsequent service availability'],
    'scope':'Host transport only; HarmonyOS cross-sandbox test separate.'},indent=2)+'\n')
print('PASS: actual Qt transport and client, six protocol checks')
