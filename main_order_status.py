import requests
import db
import smtp
import traceback
import config as setting
import datetime
from datetime import datetime, timedelta
import pytz

def convertir_gmt_a_argentina(gmt):
      # Crear un objeto datetime a partir de la cadena, asumiendo que está en la zona horaria UTC
  dt_utc = datetime.fromisoformat(gmt).replace(tzinfo=pytz.utc)
  # Crear un objeto datetime con la zona horaria de Argentina (GMT-3)
  dt_arg = dt_utc.astimezone(pytz.timezone("America/Argentina/Buenos_Aires"))
  # Devolver el objeto datetime con la zona horaria de Argentina
  return dt_arg

def getOrders(from_date, to_date):
    url = f"{url_base}orders/search?limit=100&offset=0&from={from_date}&to={to_date}"
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
    
def filterDelivered(orders):
    filtered = []
    for order in orders:
        if "orderStatus" in order:
            filtered.append(order)
            
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
        orders = getOrders(from_date, to_date)
        
        delivered_orders = filterDelivered(orders)
        cantidad_ordenes = 0
        cantidad_ordenes_salteadas = 0
        for do in delivered_orders:
            status = do['orderStatus']['description']
            if 'photos' in do['orderStatus']:
                status_date = do['orderStatus']['photos'][0]['timestamp']
                photo_url = do['orderStatus']['photos'][0]['fullUrl']
                #status_date_arg = convertir_gmt_a_argentina(status_date)
                order_id = do['_id']
                pedido = do['code']
                db.updateOrderStatus(order_id, status, status_date, pedido, photo_url)
                cantidad_ordenes += 1
            else:
                cantidad_ordenes_salteadas += 1 
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