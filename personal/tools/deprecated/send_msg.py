#!/usr/bin/env python3  
#coding: utf-8  

import smtplib  
from smtplib import SMTP_SSL
from email.mime.multipart import MIMEMultipart  
from email.mime.text import MIMEText  
from email.mime.image import MIMEImage  
  
sender = '553386336@qq.com'  
receiver = 'zjyx147@qq.com'  
subject = 'python email test'  
smtpserver = 'smtp.qq.com'  
username = '553386336@qq.com'  
password = 'owysccfocjeabfgj'
  
# Create message container - the correct MIME type is multipart/alternative.  
msg = MIMEMultipart('alternative')  
msg['Subject'] = "Link"  
  
# Create the body of the message (a plain-text and an HTML version).  
text = "Hi!\nHow are you?\nHere is the link you wanted:\nhttp://www.python.org"  
html = """\ 
<html> 
  <head></head> 
    <body> 
        <p>Hi!<br> 
	       How are you?<br> 
	              Here is the <a href="http://www.python.org">link</a> you wanted. 
		          </p> 
			    </body> 
			    </html> 
			    """  
			      
# Record the MIME types of both parts - text/plain and text/html.  
part1 = MIMEText(text, 'plain')  
part2 = MIMEText(html, 'html')  
			      
# Attach parts into message container.  
# According to RFC 2046, the last part of a multipart message, in this case  
# the HTML message, is best and preferred.  
msg.attach(part1)  
msg.attach(part2)  
#构造附件  
att = MIMEText(open('check_ip138.py', 'rb').read(), 'base64', 'utf-8')  
att["Content-Type"] = 'application/octet-stream'  
att["Content-Disposition"] = 'attachment; filename="1.jpg"'  
msg.attach(att)  
	     
#smtp = smtplib.SMTP()  
smtp = SMTP_SSL(smtpserver)
smtp.set_debuglevel(1)
#smtp.connect('smtp.qq.com')  
smtp.ehlo(smtpserver)
smtp.login(username, password)  
smtp.sendmail(sender, receiver, msg.as_string())  
smtp.quit()  
