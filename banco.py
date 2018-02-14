import time,pickle,base64,sqlite3,math

MINUTO = 60
HORA = 60*MINUTO
DIA = 24*HORA

def makeID(db):
    a=sqlite3.connect(db)
    a.execute("CREATE TABLE IF NOT EXISTS Cont(ID INTEGER PRIMARY KEY,Ocupado BOOL NOT NULL)")
    a.commit()
    cur=a.execute("SELECT ID FROM Cont WHERE Ocupado IS 0")
    try:
        d=next(cur)
        cur.close()
        idd=d[0]
        a.execute("UPDATE Cont SET Ocupado = 1 WHERE ID IS "+str(idd))
        a.commit()
    except StopIteration:
        cur=a.execute("SELECT MAX(ID) FROM Cont")
        b=list(cur)
        if b[0][0]:
            idd=b[0][0]+1
            a.execute("INSERT INTO Cont VALUES(%i,1)" % idd)
            a.commit()
        else:
            idd=1
            a.execute("INSERT INTO Cont VALUES(%i,1)" % idd)
            a.commit()
    a.close()
    return idd

def deleteID(ID,db):
    a=sqlite3.connect(db)
    a.execute("UPDATE Cont SET Ocupado = 0 WHERE ID IS "+str(ID))
    a.commit()
    a.close()

class TBanco:
    def __init__(self,db):
        self.__db=db
        self.__cuentas_db=db
        db_accounts=sqlite3.connect(self.__db)
        db_accounts.execute(
        "CREATE TABLE IF NOT EXISTS Accounts(ID INTEGER NOT NULL,Account_data TEXT NOT NULL)")
        db_accounts.commit()
        db_accounts.close()

    #Funciones para el usuario, basicas

    def crearCuenta(self,ID):
        cuenta=TCuenta(ID)
        cuenta._TCuenta__setActualizadora(Actualizadora(cuenta,self.__db))
        for _ in range(5):
            cuenta.agregarMoneda(TMoneda(100,3*DIA,makeID(self.__db)))
        db_accounts=sqlite3.connect(self.__db)
        db_accounts.execute(
            "INSERT INTO 'Accounts' (ID,Account_data) VALUES (%i,'%s')" % (
                cuenta.getID(), base64.b64encode(pickle.dumps(cuenta)).decode() 
            )
        )
        db_accounts.commit()
        db_accounts.close()
        return cuenta

    def obtenerCuenta(self,ID):
        db_accounts=sqlite3.connect(self.__cuentas_db)
        cursor=db_accounts.execute("select Account_data from Accounts where ID=%i" % ID)
        try:
            cuenta=next(cursor)
            cursor.close()
            cuenta=pickle.loads(base64.b64decode(cuenta[0].encode()))
            db_accounts.close()
            return cuenta
        except:
            cursor.close()
            db_accounts.close()
            return None
'''
    def obtenerCuentas(self,page=1,pagesize=20):
        if page<=0:
            return {"error":True,"error_message":"Pagina "+str(page)+" fuera de rango"}
        db_accounts=sqlite3.connect(self.__cuentas_db)
        cursor=db_accounts.execute("SELECT Account_data FROM Accounts")
        npages=(lambda a,b:int(a/b)+1 if a%b else int(a/b))(cursor.count(),pagesize)
        cursor=cursor.skip((page-1)*pagesize)
        if not(cursor.count()):
            conn.close()
            return {"error":True,"error_message":"Pagina "+str(page)+" fuera de rango"}
        cuentas=[DecodeObject(cuenta['account_data']).__json__() for cuenta in cursor.limit(pagesize)]
        last_page=False
        if len(cuentas)<pagesize or cursor.count()==pagesize:
            last_page=True
        conn.close()
        return {
            "error" : False,
            "cuentas" : cuentas,
            "page" : page,
            "last_page" : last_page,
            "npages" : npages
        }
'''
class Actualizadora:
    """docstring for Actualizadora"""
    def __init__(self,cuenta,db_name):
        self.__cuenta=cuenta
        self.__db_name=db_name

    def __call__(self,a_funcion):
        def actualizarCuenta():
            r=a_funcion()
            db_accounts=sqlite3.connect(self.__db_name)
            db_accounts.execute("UPDATE Accounts SET Account_data='%s' where ID='%s'" % (
                base64.b64encode(pickle.dumps(self.__cuenta)).decode(), self.__cuenta.getID())
                )
            db_accounts.commit()
            db_accounts.close()
            return [deleteID(m.getID(),self.__db_name) for m in r]
        return actualizarCuenta

class TMoneda:
    #valor puede ser 1 o 10 o 100 o 1000 o 10000
    def __init__(self,valor,duracion,ID):
        self.__id=ID
        self.__emision=int(time.time())
        self.__duracion=duracion
        self.__valor=valor
        if not(math.log10(self.__valor).is_integer() and (self.__duracion>=MINUTO)):
            raise Exception("Datos de la moneda invalidos")

    def consultarExpiracion(self):
        return self.__duracion-self.tiempoActiva()

    def tiempoActiva(self):
        return int(time.time())-self.__emision

    def consultarValor(self):
        return self.__valor

    def getID(self):
        return self.__id

    def __json__(self):
        return {
            "ID":self.getID(),
            "valor":self.consultarValor(),
            "expiracion":self.consultarExpiracion(),
            "tiempo_activa":self.tiempoActiva()
        }

class TCuenta:
    def __init__(self,ID):
        self.__saldo_valor=0
        self.__id=ID
        self.__saldo_monedas=[]
        self.__creacion=int(time.time())

    def __setActualizadora(self,actualizadora):
        self.__actualizadora=actualizadora

    def getID(self):
        return self.__id

    #Funciones de consulta de saldo y modificacion de saldo

    def getCreacion(self):
        return self.__creacion

    def getSaldo(self,que="_"):
        if que.lower()=="valor":
            return self.__saldo_valor
        elif que.lower()=="monedas":
            return self.__saldo_monedas
        else:
            return {"valor":self.__saldo_valor,"monedas":self.__saldo_monedas}

    def agregarMoneda(self,moneda):
        self.__saldo_monedas.append(moneda)
    
    def eliminarMoneda(self,idmoneda):
        for m in self.__saldo_monedas:
            if m.getID()==idmoneda:
                self.__saldo_monedas.remove(m)
                return True

    def obtenerMoneda(self,idmoneda):
        for m in self.__saldo_monedas:
            if m.getID()==idmoneda:
                return m

    def actualizarSaldo(self):
        @self.__actualizadora
        def actualizar():
            d=filter(lambda moneda:moneda.consultarExpiracion()<0,self.__saldo_monedas)
            self.__saldo_monedas = list(filter(lambda moneda:moneda.consultarExpiracion()>0,self.__saldo_monedas))
            self.__saldo_valor = sum([moneda.consultarValor() for moneda in self.__saldo_monedas])
            return d
        return actualizar()

    #--rango = tupla (int limite_inferior,int limite_superior) - (si el limite_inferior es mayor que el limite_superior entonces
    #se retornaran todas las monedas que no esten dentro del rango (limite_superior,limite_inferior))
    #--tipo_filtro = string 'exp' (por expiracion), 'val' (por valor)
    def obtenerMonedasEnRango(self,rango,tipo_filtro):
        if tipo_filtro=="exp":
            return set(filter(lambda moneda:moneda.consultarExpiracion()>=rango[0],self.__saldo_monedas)).intersection(
                    set(filter(lambda moneda:moneda.consultarExpiracion()<=rango[1],self.__saldo_monedas)))
        elif tipo_filtro=="val":
            return set(filter(lambda moneda:moneda.consultarValor()>=rango[0],self.__saldo_monedas)).intersection(
                    set(filter(lambda moneda:moneda.consultarValor()<=rango[1],self.__saldo_monedas)))

    def seleccionarMonedasPorID(self,ids):
        return list(filter(lambda moneda:moneda.getID() in ids,self.__saldo_monedas))

    #Funcion de transferencia

    def transferirMonedas(self,monedas,cuenta):
        for moneda in monedas:
            cuenta.agregarMoneda(moneda)
            self.__saldo_monedas.remove(monedas)
            #cuenta.actualizarSaldo()
        self.actualizarSaldo()

    def __json__(self):
        return {
            "ID":self.getID(),
            "saldo_valor":self.getSaldo("valor"),
            "saldo_monedas":[moneda.__json__() for moneda in self.getSaldo("monedas")]
        }

def TCambio(moneda,modo):
    m=moneda.__json__()
    idd=m['ID']
    if modo=="t":
        if m["valor"]>=10:
            return (True,TMoneda(m["valor"]/10,m["expiracion"]*2,idd))
        else:
            return (False,"Valor menor que 10")
    elif modo=="v":
        if m["expiracion"]>=MINUTO*2:
            return (True,TMoneda(m["valor"]*10,int(m["expiracion"]/2),idd))
        else:
            return (False,"Tiempo insuficiente para dividir")
    else:
        return (False,"Opcion invalida")

def FusionarMonedas(monedas,ID):
    if len(monedas)==2:
        if monedas[0].consultarValor()!=monedas[1].consultarValor():
            return None
        return TMoneda(
            monedas[0].consultarValor(),
            monedas[0].consultarExpiracion()+monedas[1].consultarExpiracion(),
            ID
        )
    else:
        try:
            return TMoneda(
                monedas[0].consultarValor(),
                monedas[0].consultarExpiracion()+FusionarMonedas(monedas[1:],ID).consultarExpiracion(),
                ID
            )
        except:
           return None

def DividirMoneda(moneda,db,d=2):
    ex=moneda.consultarExpiracion()
    divs=[]
    if ex>MINUTO*d:
        deleteID(moneda.getID(),db)
        for el in range(d):
            divs.append(banco.TMoneda(moneda.consultarValor(),int(ex/d),makeID(db)))
    return divs

def ClonarMoneda(moneda):
    return TMoneda(moneda.consultarValor(),moneda.consultarExpiracion(),-1)

def paginarMonedas(cuenta,page,pagesize=20):
	if page<=0:
		return {"error":True,"error_message":"Pagina "+str(page)+" fuera de rango"}
	elif (page-1)*pagesize>len(cuenta.getSaldo('monedas')):
		return {"error":True,"error_message":"Pagina "+str(page)+" fuera de rango"}
	else:
		if (page)*pagesize>=len(cuenta.getSaldo('monedas')):
			return {
				"error":False,
				"last_page":True,
				"monedas":cuenta.getSaldo("monedas")[((page-1)*20):]
			}
		else:
			return {
				"error":False,
				"last_page":False,
				"monedas":cuenta.getSaldo("monedas")[((page-1)*20):((page)*20)]
			}



