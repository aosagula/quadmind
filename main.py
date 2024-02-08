import requests
import db
import smtp
import traceback
import config as setting
import datetime

import quadmind


def getPOIS(code):
    url = url_base + "pois/search?limit=1&offset=0&code=" + code

    headers = {
        "accept": "application/json",
        "x-saas-apikey": apiKey
    }

    response = requests.get(url, headers=headers)
    records = response.json()['data']
    
    for r in records:
        print(r['_id'], r['code'], r['name'], r['address'])
        
def getPOISByCode(code):
    url = url_base + "pois/" + code

    headers = {
        "accept": "application/json",
        "x-saas-apikey": apiKey
    }

    response = requests.get(url, headers=headers)
   
    if (response.status_code == 200):
        return response.json()['data']
    else:
        return None
    
def getArticulo( code ):
    url = url_base + "products/search?limit=100&offset=0&code=" + code

    headers = {
        "accept": "application/json",
        "x-saas-apikey": apiKey
    }

    response = requests.get(url, headers=headers)
    records = response.json()['data']
    if ( len(records) > 0):
        return records[0]
    else:
        return None

def addOrder(payload, armado):
    
    url = url_base + "orders"
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "x-saas-apikey":apiKey
    }

    response = requests.post(url, json=payload, headers=headers)


    if response.status_code == 200:
        
            
        if len(response.json()['meta']['errors']) == 0:
           
            order_id = response.json()['data'][0]['_id']
            db.insertInQuadmind(payload[0]['code'], armado, order_id)
        elif response.json()['meta']['errors'][0]['error'] == 2020:   
            order_id = int(quadmind.getOrder(payload[0]['code']))
            db.insertInQuadmind(payload[0]['code'], armado, order_id)
        
        
    #print(response.json())

def getAbrCode(cuenta):
    for elemento in abreviaturas:
        if elemento['Entidad'] == int(cuenta):
            return elemento['Abreviatura']
    return None  # Devuelve None si no se encuentra la entidad
        
def addArticulo( code, cuenta, descripcion):
    url = url_base + "products"

    payload = [
        {
            "code": code,
            "group": cuenta,
            "description": descripcion
        }
    ]
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "x-saas-apikey": apiKey
    }

    response = requests.post(url, json=payload, headers=headers)
    if (response.status_code == 200):
        return response.json()['data'][0]
    else:
        return None
    print(response.text)
    
def handleArticulo( abr, cuenta, codigo, descripcion):
    item = getArticulo(codigo)
    if ( item == None ):
        item = addArticulo( codigo , cuenta, descripcion)
        print( f"agregando articulo {codigo} {descripcion}")
    return item

def handlePois( abr, cuenta, cliente_codigo, cliente_nombre, dir, loc, cp, prov):
   customer = getPOISByCode(abr + cliente_codigo) 
   if ( customer == None):
        customer = AddPois(abr, cuenta, cliente_codigo, cliente_nombre, dir,
                           loc, cp, prov)
        print (f"se agrega pois {cliente_codigo}-{cliente_nombre}")
   else:
       #"4 de Febrero 3640, San Andres, Provincia de Buenos Aires, Argentina",
       if (customer['originalAddress'] != f"{dir} - {loc} ({cp}) - {prov}" and dir != 'VACLOG' and dir != 'VAC LOG'):
           customer = updatePois( abr, cuenta, cliente_codigo, cliente_nombre, 
                               dir, loc, cp, prov)
           print (f"se cambio dirección {cliente_codigo}-{cliente_nombre}")
   return customer
        
def AddPois( abr, cuenta, cliente_codigo, cliente_nombre, dir, loc, cp, prov):
    url = url_base + "pois"

    payload = [
        {
            "address": {
                "street": dir,
                
                "locality": f"{loc} ({cp})",
                "state": prov,
                "country": "Argentina"
            },
            "code": abr + cliente_codigo,
            "name": cliente_nombre,
            "grouping": cuenta,
            "longAddress": f"{dir} - {loc} ({cp}) - {prov}"
        }
    ]
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "x-saas-apikey": apiKey
    }

    response = requests.post(url, json=payload, headers=headers)
    if (response.status_code == 200):
        # if ( response.json()['meta']['errors'][0]['error'] == 2020):
        #     return response.json()
        return response.json()['data'][0]
    else:
        return None
    print(response.text)
    
    
    



def updatePois(abr, cuenta, cliente_codigo, cliente_nombre, dir, loc, cp, prov):
    url = url_base + "pois/" + abr + cliente_codigo

    payload = [
        {
            "address": {
                "street": dir,
                
                "locality": f"{loc} ({cp})",
                "state": prov,
                "country": "Argentina"
            },
           
            "name": cliente_nombre,
            "grouping": cuenta,
            "longAddress": f"{dir} - {loc} ({cp}) - {prov}"
        }
    ]
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "x-saas-apikey": apiKey
    }

    response = requests.put(url, json=payload, headers=headers)
    if (response.status_code == 200):
        # if ( response.json()['meta']['errors'][0]['error'] == 2020):
        #     return response.json()
        return response.json()['data']
    else:
        return None
    print(response.text)
def main():
    dt = datetime.datetime.now()
    print(f"Inicia Proceso {dt}")
    try:
        
        
        orders = db.getOrders()
        cliente_codigo_anterior = ''
        orden_anterior = ''
        armado_anterior= ''
        cantidad_ordenes = 0
        add_order_flag = False
        order_items = []
        order_payload = []
        for idx, order in enumerate(orders):
            armado = int(order['Armado'])
            pedido = order['Pedido'].strip()
            cuenta = str(order['Cuenta'])
            abr_cuenta = getAbrCode(cuenta)
            cliente_codigo = order['Cliente'].strip()
            cliente_nombre = order['Nombre'].strip()
            fechaFin = order['FinDeArmado'].strftime('%Y-%m-%d')
            vkm_articulo = str(order['vkm_articulo'])
            articulo_codigo = order['Articulo'].strip()
            articulo_nombre = order['Descripcion'].strip()
            cantidad_preparada = round(order['CantidadPreparada'])
            volumen_m3 = int(round(order['VolumenMts3'], 0))
            peso_kg = int(round(order['PesoKgr'], 0))   
            calle_numero = order['calle_numero'].strip()
            localidad_nombre = order['localidad_nombre'].strip()
            cod_postal = order['localidad_codigo_postal'].strip()
            provincia_nombre = order['provincia_nombre'].strip()         
            
            if ( orden_anterior != pedido ):
                print(f"Procesando Orden: {pedido}")
                if (add_order_flag):
                    order_payload[0]["orderItems"].extend(order_items)
                    addOrder(order_payload, armado_anterior)
                    print(f"fin del proceso orden {orden_anterior}")
                    pass
                add_order_flag = True
                cantidad_ordenes = cantidad_ordenes + 1
                order_items = []
                order_payload = []
                if ( abr_cuenta + cliente_codigo != cliente_codigo_anterior):
                    pois = handlePois( abr_cuenta, cuenta, cliente_codigo, cliente_nombre, calle_numero, localidad_nombre, cod_postal, provincia_nombre)
                    
                    cliente_codigo_anterior = abr_cuenta + cliente_codigo
                    
                # DMD Merchants ID 18444 debe estar en un array por empresa
                if int(cuenta) == 12716: # DMD
                    merchants_id = 18444
                elif int(cuenta) == 18200: # DUGTRIO
                    merchants_id = 18514
                elif int(cuenta) == 18697: # AMANDE
                    merchants_id = 18516
                else:
                    pass
                order_payload = [{
                    "operation": "PEDIDO",
                    "poiId": pois['_id'],
                    "code": pedido,
                    "date": fechaFin,
                    "merchants": [
                    {
                        "_id": merchants_id
                    }
                    ],
                    "orderItems": []
                }]
                orden_anterior = pedido
                armado_anterior = armado
            
            item = handleArticulo( abr_cuenta, cuenta, vkm_articulo, articulo_nombre)
            order_items.append ({
                "productId": item['_id'],
                "productCode" : vkm_articulo,
                "quantity": cantidad_preparada,
                "weight": peso_kg
            })
        
        if len(orders) > 0:
            order_payload[0]["orderItems"].extend(order_items)
            addOrder(order_payload, armado_anterior)
            print(f"fin del proceso orden {orden_anterior}")
        dt = datetime.datetime.now()
        print(f"fin proceso se procesaron {cantidad_ordenes} {dt}")    
    except Exception as inst :
        error_description = traceback.format_exc()
        print(error_description)
        if setting.config.mail_send_flag == True:
            smtp.smtp.SendMail('tickets@itservices.vaclog.com','ERROR Procesando Quadminds', error_description,"" )
    
    
    
    
db = db.DB()
url_base = setting.config.quadmind_url
apiKey = setting.config.quadmind_api_key
abreviaturas = db.getParamsClient()
main()

# TODO
# - Las abreviaturas deben estar en una tabla
# - Revisar casos donde la direccion es nula
# - 
