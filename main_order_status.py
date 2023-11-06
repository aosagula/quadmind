import requests
import db
import smtp
import traceback
import config as setting
import datetime
from datetime import datetime, timedelta


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
        
        for do in delivered_orders:
            status = do['orderStatus']['description']
            status_date = do['orderStatus']['photos'][0]['timestamp']
            order_id = do['_id']
            pedido = do['code']
            db.updateOrderStatus(order_id, status, status_date, pedido)
        
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

main()