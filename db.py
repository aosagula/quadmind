﻿import pymssql
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
                       and LogEntId in ( 12716, 13781 )\
                       and f.entid not in ( '13092', '14275', '14473' , '14328' )\
                       and SentFecFin >= '2023-11-06' \
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

    def updateOrderStatus( self, order_id, status, status_datetime, pedido ):
        sentence=f"update Remito_PROD.dbo.quadmind_orders SET\
                    estado = '{status}', \
                    fecha_estado = '{status_datetime}'\
                    WHERE order_id = {order_id}\
                    and fecha_estado is null"
       
        with self.conn.cursor(as_dict=True) as cursor:
            cursor.execute(sentence) 
            
        self.conn.commit()
        print(f"Pedido {pedido} Armado {armado} Orden_id {order_id} ACTUALIZADO en tabla Quadmind_orders")

        #TODO AGREGAR ARMADO AL INSERT, Tambien Status, FEcha de Entrega
        
            
        #print (sentence)
        