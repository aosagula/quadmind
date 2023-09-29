from dotenv import dotenv_values

settings = dotenv_values(".env")

class Config:
    def __init__(self, email_host="", email_port="", email_user="", email_password="", mail_send_flag="",
                 db_host="", db_database="", db_port="",db_user="",db_password="", 
                 quadmind_url="", quadmind_api_key=""):
        
        self.email_host = email_host
        self.email_port = email_port
        self.email_user = email_user
        self.email_password = email_password
        self.mail_send_flag = mail_send_flag
        self.db_host= db_host
        self.db_port=db_port
        self.db_database = db_database
        self.db_user= db_user
        self.db_password = db_password
        self.quadmind_url = quadmind_url
        self.quadmind_api_key = quadmind_api_key
        
config = Config( settings['MAIL_SERVER'], 
                settings['MAIL_PORT'],
                settings['MAIL_USER'],
                settings['MAIL_PASSWORD'],
                settings['MAIL_SEND_FLAG'],
                settings['DB_HOST'],
                settings['DB_PORT'],
                settings['DB_DATABASE'],
                settings['DB_USER'],
                settings['DB_PASSWORD'],
                settings['QUADMIND_URL'],
                settings['QUADMIND_API_KEY'],
                
                )
                



