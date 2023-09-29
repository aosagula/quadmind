import smtplib, ssl
import config

from email.mime.text import MIMEText
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase

class Smtp:

    def __init__ (self, host, port, user, password):
        
        self.host = host
        self.port = port
        self.user = user
        self.password = password
                     
            
    def SendMail(self, to, subject, plain_message="", html_message="<html></html>", imagename=""):
        context = ssl.create_default_context()
        
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self.user
        message["To"] = to
        text= plain_message
        html = html_message
        
        part1=MIMEText(text, 'plain')
             
        message.attach(part1)
        if (len(imagename)> 0):
            filename=imagename
            
            with open(filename, 'rb') as attachment:
                part2 = MIMEBase("application", "octet-stram")
                part2.set_payload(attachment.read())
            
            encoders.encode_base64(part2)
            part2.add_header(
                "Content-Disposition",
                f"attachment; filename= {filename}",
            )
            
            
            message.attach(part2)
        with smtplib.SMTP_SSL(self.host, self.port, context=context) as self.server:
            self.server.login(self.user, self.password)
            self.server.sendmail(self.user, to, message.as_string())
            
smtp = Smtp( config.config.email_host, config.config.email_port,
            config.config.email_user, config.config.email_password)
