from selenium import webdriver
import socket, threading, re, base64, pickle

request_p = re.compile(r'(?P<pet>[a-z]{1,8}) (?P<param>[a-zA-Z0-9+/]+={0,2}) (?P<dest>.*)')
webdriver = webdriver.PhantomJS()

def handle(conn):
    global request_p
    global webdriver
    recv = conn.recv(2048).decode()
    request = request_p.fullmatch(recv)
    if not(request):
        conn.send('error:mal formato'.encode())
        return conn.close()
    else:
        request = request.groupdict()
    pet,param,dest = request['pet'],base64.b64decode(request['param'].encode()),request['dest']
    if pet == 'mutt':
        param = param.decode()
        webdriver.set_window_size(480,800)
        req = 'http://127.0.0.1:8080/mutt?text=%s' % param
        print('Requesting: '+req)
        webdriver.get(req)
        webdriver.save_screenshot(dest)
        conn.send(('succes:'+dest).encode())
    elif pet == 'ss':
        param = param.decode()
        webdriver.set_window_size(1280,720)
        webdriver.get(param)
        print('Requesting: '+param)
        webdriver.save_screenshot(dest)
        conn.send(('succes:'+dest).encode())
    elif pet == 'meme':
        param = pickle.loads(param)
        query = '&'.join([key+'='+param[key] for key in param])
        req = 'http://127.0.0.1:8080/meme?%s' % query
        print('Requesting: '+req)
        webdriver.get(req)
        webdriver.save_screenshot(dest)
        conn.send(('succes:'+dest).encode())
    elif pet == 'profile':
        param = base64.b16encode(param).decode()
        webdriver.set_window_size(1000,1000)
        req = 'http://127.0.0.1:8080/profile?pkfile=%s' % param
        print('Requesting: '+req)
        webdriver.get(req)
        webdriver.save_screenshot(dest)
        conn.send(('succes:'+dest).encode())
    else:
        conn.send('error:peticion no encontrada'.encode())
    conn.close()

socket = socket.socket()
socket.bind(('127.0.0.1',4300))
socket.listen(16)
print('Servicio listo')
while True:
    handle = handle
    try:
        conn, addr = socket.accept()
    except:
        socket.close()
        print('Termino el programa')
        exit(0)
    print('Conexion encontrada: %s:%i' % addr)
    threading.Thread(target=handle,args=(conn,)).start()

#Luis Albizo 17/02/2018
