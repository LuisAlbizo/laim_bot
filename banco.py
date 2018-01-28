import time,pickle,base64,sqlite3

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
        a.execute("UPDATE Cont SET Ocupado = 1 WHERE ID IS "+idd)
        a.commit()
    except StopIteration:
        cur=a.execute("SELECT MAX(ID) FROM Cont")
        b=list(cur)
        print(b)
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
            return r
        return actualizarCuenta

class TMoneda:
    #valor puede ser 1 o 10 o 100 o 1000 o 10000
    def __init__(self,valor,duracion,ID):
        self.__id=ID
        self.__emision=int(time.time())
        self.__duracion=duracion
        self.__valor=valor
        if not((self.__valor in [1,10,100,1000,10000]) and (self.__duracion>=MINUTO)):
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

    def getSaldo(self,que="_"):
        if que.lower()=="valor":
            return self.__saldo_valor
        elif que.lower()=="monedas":
            return self.__saldo_monedas
        else:
            return {"valor":self.__saldo_valor,"monedas":self.__saldo_monedas}

    def agregarMoneda(self,moneda):
        if moneda.consultarExpiracion()>0:
            self.__saldo_monedas.append(moneda)
            return True
        else:
            return False

    def actualizarSaldo(self):
        try:
            @self.__actualizadora
            def actualizar():
                self.__saldo_monedas = list(filter(lambda moneda:moneda.consultarExpiracion()>0,self.__saldo_monedas))
                self.__saldo_valor = sum([moneda.consultarValor() for moneda in self.__saldo_monedas])
        except:
            def actualizar():
                self.__saldo_monedas = list(filter(lambda moneda:moneda.consultarExpiracion()>0,self.__saldo_monedas))
                self.__saldo_valor = sum([moneda.consultarValor() for moneda in self.__saldo_monedas])
        actualizar()

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

def TCambio(monedas,modo,evaluar):
    new_monedas=monedas
    if modo=="div":
        if evaluar=="exp":
            pass
        elif evaluar=="val":
            pass
    elif modo=="mul":
        if evaluar=="exp":
            pass
        elif evaluar=="val":
            pass
    return new_monedas

def TCambioS(moneda,modo):
    m=moneda.__json__()
    idd=m['id']
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

def FusionMonedas(monedas,db):
    if len(monedas)==2:
        if monedas[0].consultarValor()!=monedas[1].consultarValor():
            return None
        return TMoneda(
            monedas[0].consultarValor(),
            monedas[0].consultarExpiracion()+monedas[1].consultarExpiracion(),
            makeID(db)
        )
    else:
        try:
            return TMoneda(
                monedas[0].consultarValor(),
                monedas[0].consultarExpiracion()+FusionarMonedas(monedas[1:],db).consultarExpiracion(),
                None
            )
        except:
            return None










