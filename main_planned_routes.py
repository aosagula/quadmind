import requests
import db
import smtp
import traceback
import config as setting
import datetime
from datetime import datetime, timedelta
import pytz
import util


def getConsolidatedRoutes(from_date, to_date):
    url = f"{url_base}consolidated-routes/search?limit=100&offset=0&from={from_date}&to={to_date}"
    #url = "https://saas.quadminds.com/api/v2/orders/search?limit=100&offset=0&from=2023-09-18&to=2023-09-19"
    headers = {
        "accept": "application/json",
        "x-saas-apikey": apiKey
    }

    response = requests.get(url, headers=headers)
   
    if (response.status_code == 200):
        return response.json()['data']
    else:
        return None
    
def filterWaypoints(consolidated):
    filtered = []
    for order in consolidated:
        if "waypoints" in order:
            filtered.append(order['waypoints'])
            
    return filtered
def filterPlannedOrders(waypoints):
    filtered = []
    for wp_group in waypoints:
        for wp in wp_group:
            if 'status' not in wp:
               
                    filtered.append(wp)
            else:
                 if "Entregado" not in wp['status']['description']:
                        pass # Los no entregados print(wp)
                    
    return filtered

def getPoi( poiId):
    url = f"{url_base}pois?limit=100&offset=0&_id={poiId}"
    headers = {
        "accept": "application/json",
        "x-saas-apikey": apiKey
    }

    response = requests.get(url, headers=headers)
   
    if (response.status_code == 200):
        return response.json()['data'][0]
    else:
        return None
def getClientByAbbr( abreviatura ):
    for ab in abreviaturas:
        if ab['Abreviatura'] == abreviatura:
            return ab['Entidad']
def getEntityId( poiData, abreviatura):
    code = poiData['code']
    entidad_id = code.split(abreviatura)[1]
    return entidad_id
def getValkimiaEntity( poiData):
    
    return { "client_id": getClientByAbbr( poiData['code'][:3]), 
             "entidad_id": getEntityId(poiData, poiData['code'][:3]) }
def main():
    dt = datetime.now()
    print(f"Inicia Proceso {dt}")
    try:
        # Get the current date and time
        current_datetime = datetime.now()
        to_date = current_datetime.strftime('%Y-%m-%d')
        # Calculate the date and time 7 days ago
        some_days_ago = current_datetime - timedelta(days=6)
        
        from_date = some_days_ago.strftime('%Y-%m-%d')
        orders = getConsolidatedRoutes(from_date, to_date)
        
        waypoints = filterWaypoints(orders)
        
        planned_waipoints = filterPlannedOrders(waypoints)
        cantidad_ordenes = 0
        cantidad_ordenes_salteadas = 0
        for pw in planned_waipoints:
            for activity in pw['activities']:
                if activity['type'] == 'delivery':
                    for op in pw['activities'][0]['orders']:
                        
                        poiData = getPoi(op['poiId'])
                        valkimia_entity_struct = getValkimiaEntity(poiData)
                        
                        planned_order = {
                            "order_id": op['_id'],
                            "cuenta_id": valkimia_entity_struct['client_id'],
                            "client_id": valkimia_entity_struct['entidad_id'],
                            "name": poiData['name'],
                            "pedido": op['code'],
                            "fecha_plan": pw['scheduledDate']
                            }
                        db.insertPlannedOrder(planned_order)
                        
                        print (f"Sin vehiculo: {op['code']} {op['date']} {op['poiId']} {pw['scheduledDate']} {poiData['name'] } {valkimia_entity_struct['client_id']}" )
                        cantidad_ordenes += 1
                        
        dt = datetime.now()
        print(f"fin proceso se procesaron {cantidad_ordenes} se saltearon {cantidad_ordenes_salteadas} {dt}")  
    except Exception as inst :
        error_description = traceback.format_exc()
        print(error_description)
        if setting.config.mail_send_flag == True:
            smtp.smtp.SendMail('tickets@itservices.vaclog.com','ERROR Procesando Quadminds', error_description,"" )

   
db = db.DB()
abreviaturas = db.getParamsClient()

url_base = setting.config.quadmind_url
apiKey = setting.config.quadmind_api_key

main()