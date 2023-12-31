import requests
import db
import smtp
import traceback
import config as setting
import datetime
from datetime import datetime, timedelta
import pytz
import util
import sys


import quadmind
    
def filterWaypoints(consolidated):
    filtered = []
    for order in consolidated:
        if "waypoints" in order:
            filtered.append(order['waypoints'])
            
    return filtered
def filterDeliveredOrders(waypoints):
    filtered = []
    for wp_group in waypoints:
        for wp in wp_group:
            if 'status' in wp:
                if "Entregado" in wp['status']['description']:
                    filtered.append(wp)
            else:
                print(wp)    
    return filtered
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
        orders = quadmind.getConsolidatedRoutes(from_date, to_date)
        #orders = getConsolidatedRoutes('2023-11-06', '2023-11-09')
        
        waypoints = filterWaypoints(orders)
        
        delivered_waypoints = filterDeliveredOrders(waypoints)
        cantidad_ordenes = 0
        cantidad_ordenes_salteadas = 0
        for dw in delivered_waypoints:
            status = dw['status']['description']
            status_date = util.convert_gmt_to_argentina(dw['status']['certifiedAt'])
            for do in dw['activities'][0]['orders']:
                order_id = do['_id']
                pedido = do['code'].split('|')[0]
                if 'photos' in do['orderStatus']:
                   
                    photo_url = do['orderStatus']['photos'][0]['fullUrl']
                    #status_date_arg = convertir_gmt_a_argentina(status_date)
                else:
                    photo_url = ''    
                    #
                    
                cantidad_ordenes += 1
                db.updateOrderStatus(order_id, status, status_date, pedido, photo_url)
        dt = datetime.now()
        print(f"fin proceso se procesaron {cantidad_ordenes} se saltearon {cantidad_ordenes_salteadas} {dt}")  
    except Exception as inst :
        error_description = traceback.format_exc()
        print(error_description)
        if setting.config.mail_send_flag == True:
            smtp.smtp.SendMail('tickets@itservices.vaclog.com','ERROR Procesando Quadminds', error_description,"" )

   
db = db.DB()
url_base = setting.config.quadmind_url
apiKey = setting.config.quadmind_api_key

main()