import time,pickle,base64,sqlite3

MINUTO = 60
HORA = 60*MINUTO
DIA = 24*HORA

class TBanco:
    def __init__(self,db):
        self.__db=db
        db_accounts=sqlite3.connect(self.__db)
        db_accounts.execute(
        "CREATE TABLE IF NOT EXISTS Accounts(ID INTEGER NOT NULL,Account_data TEXT NOT NULL)")
        db_accounts.commit()
        db_accounts.close()

    #Funciones para el usuario, basicas

    def crearCuenta(self,ID):
        cuenta=TCuenta(ID,int(time.time()))
        cuenta._TCuenta__setActualizadora(Actualizadora(cuenta,self.__cuentas_db))
        for _ in range(20):
            cuenta.agregarMoneda(TMoneda(100,3*DIA))
        db_accounts=sqlite3.connect(self.__db)
        db_accounts.execute(
            "INSERT INTO 'Accounts' (ID,Account_data) VALUES ('%s','%s')" % (
                cuenta.getID(), base64.b64encode(pickle.dumps(cuenta)).decode() 
            )
        )
        db_accounts.commit()
        db_accounts.close()
        return cuenta.getID()

        def obtenerCuenta(self,ID,clave="_",admin=None):
            db_accounts=sqlite3.connect("./data/db/"+self.__cuentas_db+".db")
            cursor=db_accounts.execute("select Account_data from Accounts where ID='%s'" % ID)
            try:
                cuenta=next(cursor)
                cursor.close()
                cuenta=pickle.loads(base64.b64decode(cuenta[0].encode()))
                if cuenta.confirmarClave(clave):
                    db_accounts.close()
                    return cuenta
                elif admin and admin.permisos():
                    db_accounts.close()
                    return cuenta
                else:
                    db_accounts.close()
                    return False
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
    def __init__(self,valor,duracion):
        self.__id=makeID()
        self.__emision=int(time.time())
        self.__duracion=duracion
        self.__valor=valor
        if not((self.__valor in [1,10,100,1000,10000]) and (self.__duracion>=10*MINUTO)):
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
        self.__premio=True

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

        
        
#   TCambio, recibe una lista de monedas y segun modo y valor retorna otra lista de monedas
#monedas:   lista de monedas a cambiar
#modo:      div o mul, si por el valor que tienen las monedas se obtendran 
#           menos monedas con mas 'valor' respecto a evaluar o mas monedas con menos valor 
#evaluar:   exp o val, si las monedas que se quieren cambiar se tienen que evaluar por su expiracion o su valor
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


