from selenium import webdriver
import socket, threading, re, base64

request_p = re.compile(r'(?P<pet>[a-z]{1,6}) (?P<param>[a-zA-Z0-9+/]+={0,2}) (?P<dest>.*)')
webdriver = webdriver.PhantomJS()

def handle(conn):
    global request_p
    global webdriver
    recv = conn.recv(1024).decode()
    print(recv)
    request = request_p.fullmatch(recv)
    if not(request):
        conn.send('error:mal formato'.encode())
        return conn.close()
    else:
        request = request.groupdict()
    pet,param,dest = request['pet'],base64.b64decode(request['param'].encode()).decode(),request['dest']
    if pet == "mutt":
        webdriver.set_window_size(480,800)
        webdriver.get('http://127.0.0.1:8080/mutt?text=%s' % param)
        webdriver.save_screenshot(dest)
        conn.send(('succes:'+dest).encode())
    elif pet == "ss":
        webdriver.set_window_size(1280,720)
        webdriver.get(param)
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
        print("Ocurrio un error")
        exit(0)
    print('Conexion encontrada: %s:%i' % addr)
    threading.Thread(target=handle,args=(conn,)).start()

#Luis Albizo 17/02/2018
