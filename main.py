import requests
import db
import smtp
import traceback


url_base = "https://saas.quadminds.com/api/v2/"
apiKey = "7d8d4723e289db708e2e3962630696166ed4a490"
db = db.DB()

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

def addOrder(payload):
    
    url = url_base + "orders"
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "x-saas-apikey":apiKey
    }

    response = requests.post(url, json=payload, headers=headers)


    db.insertInQuadmind(payload[0]['code'])
    #print(response.json())

def getAbrCode(cuenta):
    if(cuenta == '1032'):
        return 'BR'
    elif (cuenta == '13000'):
        return 'OT'
    elif ( cuenta == '13781'):
        return 'BP'
    elif (cuenta=='1034'):
        return 'PE'
        
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
       if (customer['address'] != f"{dir} - {loc} ({cp}) - {prov}"):
           customer = AddPois( abr, cuenta, cliente_codigo, cliente_nombre, 
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
        return response.json()['data'][0]
    else:
        return None
    print(response.text)

def main():
    
    print(f"Inicia Proceso")
    try:
        orders = db.getOrders()
        cliente_codigo_anterior = ''
        orden_anterior = ''
        cantidad_ordenes = 0
        add_order_flag = False
        order_items = []
        order_payload = []
        for idx, order in enumerate(orders):
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
            volumen_m3 = round(order['VolumenMts3'], 2)
            peso_kg = round(order['PesoKgr'], 2)   
            calle_numero = order['calle_numero'].strip()
            localidad_nombre = order['localidad_nombre'].strip()
            cod_postal = order['localidad_codigo_postal'].strip()
            provincia_nombre = order['provincia_nombre'].strip()         
            
            if ( orden_anterior != pedido ):
                print(f"Procesando Orden: {pedido}")
                if (add_order_flag):
                    order_payload[0]["orderItems"].extend(order_items)
                    addOrder(order_payload)
                    print(f"fin del proceso orden {orden_anterior}")
                    pass
                add_order_flag = True
                cantidad_ordenes = cantidad_ordenes + 1
                order_items = []
                order_payload = []
                if ( abr_cuenta + cliente_codigo != cliente_codigo_anterior):
                    pois = handlePois( abr_cuenta, cuenta, cliente_codigo, cliente_nombre, calle_numero, localidad_nombre, cod_postal, provincia_nombre)
                    
                    cliente_codigo_anterior = abr_cuenta + cliente_codigo
                order_payload = [{
                    "operation": "PEDIDO",
                    "poiId": pois['_id'],
                    "code": pedido,
                    "date": fechaFin,
                    "orderItems": []
                }]
                orden_anterior = pedido
            
            item = handleArticulo( abr_cuenta, cuenta, vkm_articulo, articulo_nombre)
            order_items.append ({
                "productId": item['_id'],
                "productCode" : vkm_articulo,
                "quantity": cantidad_preparada,
                "weight": peso_kg
            })    
    except Exception as inst :
        error_description = traceback.format_exc()
        print(error_description)
        smtp.smtp.SendMail('tickets@itservices.vaclog.com','ERROR Procesando Quadminds', error_description,"" )
    
    print(f"fin proceso se procesaron {cantidad_ordenes}")
    
    

main()

# TODO
# - Las abreviaturas deben estar en una tabla
# - Revisar casos donde la direccion es nula
# - 
