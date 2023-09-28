import pymssql
import traceback
class DB:
    def __init__(self):
        self.server = '192.168.0.201'
        self.db = 'VKM_Prod'
        self.user = 'vaclog'
        self.password  = 'hola$$123'
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
                       and (ententidc != '' or EntEntIdC is not null) \
                       and c.DunEtaVal1 != '' \
                       and ( Dir.LEnDir != '' or Dir.LEnDir != '#N/A') \
                       and ( EntNombre != '' OR EntNombre != '0')\
                       and SentNroDsp not IN ( SELECT qua.pedido FROM Remito_PROD.dbo.quadmind_orders qua)\
                       order by SentNroDsp"
        
        #print(sentence)
        with self.conn.cursor(as_dict=True) as cursor:
            cursor.execute(sentence)  
            row_data = cursor.fetchall()    
            return row_data  

    def insertInQuadmind( self, pedido ):
        sentence=f"INSERT INTO Remito_PROD.dbo.quadmind_orders ( [pedido], [fecha_proceso]) \
                   VALUES ( '{pedido}', GETDATE())"
       
        with self.conn.cursor(as_dict=True) as cursor:
            cursor.execute(sentence) 
            
        self.conn.commit()
        print(f"Pedido {pedido} INSERTADO en tabla Quadmind_orders")

            
        #print (sentence)
        