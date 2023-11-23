import requests
import db
import smtp
import traceback
import config as setting
import datetime
from datetime import datetime, timedelta
import pytz
import util
import quadmind


    
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
       
        # Calculate the date and time 7 days ago
        some_days_ago = current_datetime - timedelta(days=6)
        
        two_days_ago = current_datetime - timedelta(days=2)
        
        next_four_days = current_datetime + timedelta(days=4)
        
        from_date = two_days_ago.strftime('%Y-%m-%d')
        
        to_date = next_four_days.strftime('%Y-%m-%d')
        # orders = quadmind.getConsolidatedRoutes(from_date, to_date)
        # orders = quadmind.getConsolidatedRoutes(from_date, to_date)
        routes = quadmind.getRoutes(from_date, to_date)
        #routes = quadmind.getRoutes('2023-11-14', '2023-11-20')
        print(f"ruta_id;fecha_plan; waypoint;estado;fecha_estado;cliente;direccion;order;pedido;cuenta")
        
        cantidad_ordenes = 0
        for r in routes:
            consolidated_route = quadmind.getConsolidatedRoute( r['_id'])
            for w in consolidated_route[0]['waypoints']:
                poi = quadmind.getPoi(w['poiId'])
                
                   
                cliente  = poi['name']
                address = poi['address']
                valkimia_entity_struct = getValkimiaEntity(poi)
                if 'status' in w:
                    estado = w['status']['description']
                    fecha_estado = util.convert_gmt_to_argentina(w['status']['certifiedAt'])
                else:
                    estado = ''
                    fecha_estado = ''
                if 'activities' in w:
                    for act in w['activities']:
                        if 'delivery' in act['type']:
                            for o in act['orders']:
                                
                                print(f"{r['_id']};{r['startDate']};{w['_id']};{estado};{fecha_estado};{util.eliminate_lf_cr(cliente)};{util.eliminate_lf_cr(address)};{o['_id']};{o['code']};{valkimia_entity_struct['client_id']}")
                                
                                if fecha_estado != '':
                                    # if r['_id'] == 44415196:
                                    #     fecha_estado_fmt = util.convert_to_ba_datetime(fecha_estado)
                                    # else:
                                    fecha_estado_fmt = util.convert_to_ba_datetime(fecha_estado)
                                else:
                                    fecha_estado_fmt = ''
                                
                               
                                    
                                cuenta_id = valkimia_entity_struct['client_id']
                                client_id = valkimia_entity_struct['entidad_id']
                                
                                planned_order = {
                                                "order_id": o['_id'],
                                                "cuenta_id": cuenta_id,
                                                "client_id": client_id,
                                                "name": poi['name'],
                                                "pedido": o['code'],
                                                "fecha_plan": r['startDate'],
                                                "fecha_estado": fecha_estado_fmt,
                                                "estado": estado,
                                                "direccion": address
                                                }
                                if cuenta_id == None:
                                    print('SALTEADO NO RECONOCE CLIENTE')
                                else:
                                    db.insertPlannedOrder(planned_order)
                        
                        #print (f"Sin vehiculo: {op['code']} {op['date']} {op['poiId']} {pw['scheduledDate']} {poiData['name'] } {valkimia_entity_struct['client_id']}" )
                                cantidad_ordenes += 1
        
        
                        
        dt = datetime.now()
        print(f"fin proceso se procesaron {cantidad_ordenes}  {dt}")  
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