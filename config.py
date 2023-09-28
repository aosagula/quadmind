class Config:
    def __init__(self, email_host="", email_port="", email_user="", email_password=""):
        
        self.email_host = email_host
        self.email_port = email_port
        self.email_user = email_user
        self.email_password = email_password
        
config = Config( "mail.itservices.vaclog.com", 465, 'votsinformes@itservices.vaclog.com','Votsinformes$123')



