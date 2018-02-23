import time, pickle, base64, math
from pymongo import MongoClient

MINUTO = 60
HORA = 60*MINUTO
DIA = 24*HORA

def EncodeObject(obj):
    return base64.b64encode(pickle.dumps(obj)).decode()

def DecodeObject(data):
    return pickle.loads(base64.b64decode(data.encode()))

def makeID(db):
    cursor = db.contador.find({'ocupado':0})
    if not(cursor.count()):
        idlibre = db.contador.find().count()+1
        db.contador.insert({'_id':idlibre,'ocupado':1})
    else:
        idlibre = cursor.next()['_id']
        db.contador.update_one({'_id':idlibre},{'$set':{'ocupado':1}})
    cursor.close()
    return idlibre
        
def deleteID(ID,db):
    db.contador.update_one({'_id':ID},{'$set':{'ocupado':0}})

class TBanco:
    def __init__(self,db):
        self.__db = db

    #Funciones para el usuario, basicas

    def crearCuenta(self,ID):
        cuenta = TCuenta(ID)
        cuenta._TCuenta__setActualizadora(Actualizadora(cuenta,self.__db.name))
        for _ in range(5):
            cuenta.agregarMoneda(TMoneda(100,3*DIA,makeID(self.__db)))
        db_accounts = self.__db.accounts
        exists = db_accounts.find_one({'_id':cuenta.getID()},{'_id':True})
        if not(exists):
            db_accounts.insert_one({
                '_id':cuenta.getID(),
                'account':EncodeObject(cuenta),
                'data':[{'data':cuenta.__json__(),'time':int(time.time())}]
                }    
            )
        else:
            db_accounts.update_one({'_id':cuenta.getID()},{'$set':{
                'account':EncodeObject(cuenta),
                'data':[{'data':cuenta.__json__(),'time':int(time.time())}]
                }}
            )
        return cuenta

    def obtenerCuenta(self,ID):
        db_accounts = self.__db.accounts
        cuenta = db_accounts.find_one({'_id':ID},{'account':True})
        if cuenta:
            cuenta = cuenta.get('account',None)
            if cuenta:
                cuenta = DecodeObject(cuenta)
        return cuenta

    def obtenerData(self,ID):
        db_accounts = self.__db.accounts
        data = db_accounts.find_one({'_id':ID},{'data':True})
        if data:
            data = data.get('data',None)
        return data

    def obtenerCuentas(self,page=1,pagesize=20):
        db_accounts=self.__db.accounts
        cuentas = [DecodeObject(el['account']) 
            for el in db_accounts.find({},{'account':True},limit=pagesize,skip=pagesize*(page-1))]
        return cuentas

class Actualizadora:
    """docstring for Actualizadora"""
    def __init__(self,cuenta,db_name):
        self.__cuenta=cuenta
        self.__db=db_name

    def __call__(self,a_funcion):
        def actualizarCuenta():
            r=a_funcion()
            client = MongoClient()
            db_accounts=client.get_database(self.__db).accounts
            db_accounts.update_one(
                {'_id':self.__cuenta.getID()},
                {'$set':{'account':EncodeObject(self.__cuenta)}}
            ) 
            db_accounts.update_one(
                {'_id':self.__cuenta.getID()},
                {'$push':{'data':{'data':self.__cuenta.__json__(),'time':int(time.time())}}}
            )
            return [deleteID(m.getID(),self.__db) for m in r]
        return actualizarCuenta

class TMoneda:
    #valor puede ser 1 o 10 o 100 o 1000 o 10000
    def __init__(self,valor,duracion,ID):
        self.__id=ID
        self.__emision=int(time.time())
        self.__duracion=duracion
        self.__valor=valor
        if not(math.log10(self.__valor).is_integer() and self.__duracion>=MINUTO):
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
        self.__saldo_duracion=0
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
        elif que.lower()=="duracion":
            return self.__saldo_duracion
        else:
            return {
                "valor" : self.__saldo_valor,
                "monedas" : self.__saldo_monedas,
                "duracion" : self.__saldo_duracion
            }

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
            self.__saldo_duracion = sum([moneda.consultarExpiracion() for moneda in self.__saldo_monedas])
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
            self.__saldo_monedas.remove(moneda)
            #cuenta.actualizarSaldo()
        self.actualizarSaldo()

    def __json__(self):
        return {
            "ID":self.getID(),
            "saldo_valor":self.getSaldo("valor"),
            "saldo_duracion":self.getSaldo("duracion"),
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

def ExtraerMoneda(moneda,db,dur=10*MINUTO):
    try:
        original = TMoneda(moneda.consultarValor(),moneda.consultarExpiracion()-dur,moneda.getID())
        extra = TMoneda(moneda.consultarValor(),dur,makeID(db))
        return (True,original,extra)
    except:
        return (False,)

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



