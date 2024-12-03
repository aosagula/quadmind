import pymssql
import traceback
import config as setting
class DB:
    def __init__(self):
        self.server = setting.config.db_host
        self.db = setting.config.db_database
        self.user = setting.config.db_user
        self.password  = setting.config.db_password
        try:
            self.conn = pymssql.connect(self.server, 
                                   self.user, 
                                   self.password, 
                                   self.db)		
            print ('CONECTADO')
            self.cursor = self.conn.cursor(as_dict=True)
        
        except Exception as e:
            print(traceback.format_exc())
            print(e)
            
            
    def getOrders(self):
        
        sentence=f"SELECT SentNroDsp 'Pedido', \
                          SentDocNro 'Armado', \
                          LogEntId 'Cuenta',\
                          ententidc 'Cliente', \
                          EntNombre 'Nombre', \
                          SentFecFin 'FinDeArmado', \
                          e.ARTID as 'vkm_articulo', \
                          DunEtaVal1 'Articulo', \
                          ArtNom 'Descripcion', \
                          ArmIteCntC 'CantidadPreparada', \
                          (DUNVol * ArmIteCntC)/100 'VolumenMts3', \
                          DunPeso * ArmIteCntC 'PesoKgr',\
                          Dir.LEnDir as calle_numero, \
                          Loc.LclNom as localidad_nombre, \
                          Loc.LclCP as localidad_codigo_postal, \
                          Prov.PncNom as provincia_nombre \
                     FROM SENT a \
                     inner join SARM d  on a.SEntDocNro = d.ArmId \
                     inner join SARM1 b on SEntDocNro = b.ArmId \
                     inner join DUN c   on c.ARTID = b.ArmArtId \
                                              and b.ArmDUNFPId = c.dunfpid \
                     inner join art e  on e.ARTID = b.ArmArtId \
                     inner join ENT f  on f.EntID = a.SEntEntId \
                     inner join ENT21 Dir on Dir.EntID = F.EntID \
                     inner join LCL Loc on Loc.LclID = Dir.LEnLclID \
                     inner join PNC Prov on Prov.PncID = Loc.PncID \
                     where SEntEstEnt in ('PRE') \
                       and ArmIteCntC <> 0 \
                       and LogEntId not in (1032) \
                       and LogEntId in ( 12716, 18200, 18697, 13781, 19322)\
                       and f.entid not in ( '13092', '14275', '14473' , '14328')\
                       and SentFecFin >= '2023-01-31' \
                       and (ententidc != '' or EntEntIdC is not null) \
                       and c.DunEtaVal1 != '' \
                       and ( Dir.LEnDir != '' or Dir.LEnDir != '#N/A') \
                       and ( EntNombre != '' OR EntNombre != '0')\
                       and SentDocNro not IN ( SELECT qua.armado \
                                                 FROM Remito_PROD.dbo.quadmind_orders qua)\
                       order by SentDocNro"
        
        #print(sentence)
        with self.conn.cursor(as_dict=True) as cursor:
            cursor.execute(sentence)  
            row_data = cursor.fetchall()    
            return row_data  

    def getParamsClient(self):
        sentence=f"SELECT LogEntId as Entidad, Abreviatura\
                     FROM Remito_PROD.dbo.parametros_clientes"
        
        #print(sentence)
        with self.conn.cursor(as_dict=True) as cursor:
            cursor.execute(sentence)  
            row_data = cursor.fetchall()    
            return row_data  
        
        
    def insertInQuadmind( self, pedido, armado, order_id ):
        sentence=f"INSERT INTO Remito_PROD.dbo.quadmind_orders ( [pedido], [fecha_proceso], [armado], [order_id]) \
                   VALUES ( '{pedido}', GETDATE(), {armado}, {order_id})"
       
        with self.conn.cursor(as_dict=True) as cursor:
            cursor.execute(sentence) 
            
        self.conn.commit()
        print(f"Pedido {pedido} Orden_id {order_id} INSERTADO en tabla Quadmind_orders")

    def insertPlannedOrder( self, op):
        fecha_estado = op['fecha_estado']
        
        if fecha_estado != '':
            sentence=f"INSERT INTO Remito_PROD.dbo.quadmind_planned_orders ( \
                            [fecha_proceso], [cuenta_id], [client_id],\
                            [name] , [fecha_plan], [updated_at], \
                            [pedido], [order_id], \
                            [fecha_estado], \
                            [estado],\
                            [direccion],\
                            [photo_url]) \
                    VALUES ( GETDATE(), \
                            {op['cuenta_id']},\
                            '{op['client_id']}', \
                            '{op['name']}',\
                            '{op['fecha_plan']}',\
                            GETDATE(), \
                            '{op['pedido']}',\
                            {op['order_id']},\
                            '{fecha_estado}',\
                            '{op['estado']}',\
                            '{op['direccion']}',\
                            '{op['photo_url']}')"
        else:
            sentence=f"INSERT INTO Remito_PROD.dbo.quadmind_planned_orders ( \
                            [fecha_proceso], [cuenta_id], [client_id],\
                            [name] , [fecha_plan], [updated_at], \
                            [pedido], [order_id], \
                            [fecha_estado], \
                            [estado],\
                            [direccion]) \
                    VALUES ( GETDATE(), \
                            {op['cuenta_id']},\
                            '{op['client_id']}', \
                            '{op['name']}',\
                            '{op['fecha_plan']}',\
                            GETDATE(), \
                            '{op['pedido']}',\
                            {op['order_id']},\
                            NULL,\
                            '{op['estado']}',\
                            '{op['direccion']}')"
            
        #print (sentence)
        with self.conn.cursor(as_dict=True) as cursor:
            cursor.execute(sentence) 
            
        self.conn.commit()
        
        
    def updateOrderStatus( self, order_id, status, status_datetime, pedido, photo_url ):
        date_fmt= status_datetime.strftime('%Y-%m-%d %H:%M:%S')
        sentence=f"update Remito_PROD.dbo.quadmind_orders SET\
                        estado = '{status}', \
                        fecha_estado = '{date_fmt}',\
                        photo_url = '{photo_url}',\
                        order_id = {order_id},\
                        updated_at = GETDATE()\
                    WHERE pedido = '{pedido}'\
                    and fecha_estado is null"
       
        with self.conn.cursor(as_dict=True) as cursor:
            result = cursor.execute(sentence) 
            
        self.conn.commit()
        print(f"Pedido {pedido} Orden_id {order_id} ACTUALIZADO en tabla Quadmind_orders")

        #TODO AGREGAR ARMADO AL INSERT, Tambien Status, FEcha de Entrega
        
            
        #print (sentence)
        