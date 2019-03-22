#!/usr/bin/python
#coding: utf-8

# sent email via python

import os, sys
import smtplib
from smtplib import SMTP_SSL
from email.header import Header
from email.mime.text import MIMEText
 

#
def send_msg(mailInfo):

    smtp = SMTP_SSL(mailInfo["hostname"])
    smtp.set_debuglevel(1)
    smtp.ehlo(mailInfo["hostname"])
    smtp.login(mailInfo["username"],mailInfo["password"])
     

    if (not mailInfo.has_key('attachment')) or (mailInfo['attachment'] is None):
        msg = MIMEText(mailInfo["mailtext"],"html",mailInfo["mailencoding"])
    else:
        from email.mime.multipart import MIMEMultipart
        msg = MIMEMultipart('alternative')
        msg = attach_file(msg, mailInfo['attachment'])

    msg["Subject"] = Header(mailInfo["mailsubject"],mailInfo["mailencoding"])
    msg["from"] = mailInfo["from"]
    msg["to"] = mailInfo["to"]
    smtp.sendmail(mailInfo["from"], mailInfo["to"], msg.as_string())
     
    smtp.quit()

#
def attach_file(msg_main, msg_att):

    if not os.path.exists(msg_att):
        print ('%s not found in current folder, stop.\n'% msg_att)
        sys.exit(1)
    att = MIMEText(open('./%s'% msg_att, 'rb').read(), 'base64', 'utf-8')  
    att["Content-Type"] = 'application/octet-stream'  
    att["Content-Disposition"] = 'attachment; filename="%s"'% msg_att  
    msg_main.attach(att)  
    return msg_main
        
if __name__ == '__main__':

    info_qq = {
        # attachmeent, may be ignored
        "attachment": "send_email.py",

        "from": "553386336@qq.com",
        #"to": "adormer1@126.com",
        "to": "553386336@qq.com",
        "hostname": "smtp.qq.com",
        "username": "553386336@qq.com",
        "password": "owysccfocjeabfgj",
        "mailsubject": "test",
        "mailtext": "hello, this is send mail test.",
        "mailencoding": "utf-8"

    }

    send_msg(info_qq)
