import requests
import sys
import os
import io

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")

import logging
from html.parser import HTMLParser
from email.mime.text import MIMEText
from email.header import Header
import smtplib

logger = logging.getLogger()
log_str = io.StringIO()
fh = logging.StreamHandler(log_str)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)

# Third-party SMTP service for sending alert emails. 第三方 SMTP 服务，用于发送告警邮件
mail_host = ""       # SMTP server, such as QQ mailbox, need to open SMTP service in the account. SMTP服务器,如QQ邮箱，需要在账户里开启SMTP服务
mail_user = ""  # Username 用户名
mail_pass = ""  # Password, SMTP service password. 口令，SMTP服务密码
mail_port = 465  # SMTP service port. SMTP服务端口

class token_extract(HTMLParser):
    data = None
    #继承HTMLParser类
    def __init__(self):
        #用父类的__init__
        HTMLParser.__init__(self)
    def handle_starttag(self, tag, attrs):
        # 重写handle_starttag方法
        if tag=="input":
           for key,values in attrs:
               if (key=="value" and len(values)==108):
                   self.data = values
    def get_token(self):
        return self.data

def sendEmail(fromAddr, toAddr, subject, content):
    sender = fromAddr
    receivers = toAddr
    message = MIMEText(content, 'plain', 'utf-8')
    message['From'] = Header(fromAddr, 'utf-8')
    message['To'] = Header(toAddr, 'utf-8')
    message['Subject'] = Header(subject, 'utf-8')
    try:
        smtpObj = smtplib.SMTP_SSL(mail_host, mail_port)
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        print("Execution completed")
        return True
    except smtplib.SMTPException as e:
        print(e)
        print("Error: send email fail")
        return False

def main_handler(event, context):
    resp = None
    url="https://oa.shsmu.edu.cn/WProtalInfo_WeChat/InformationReporting/InformationReporting"
    logger.info('Accessing: '+url)
    try:
        resp = requests.get(url, timeout=3)
        logger.info(resp)
    except(requests.exceptions.Timeout, requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout) as e:
        logger.warning("Request exceptions:" + str(e))
    else:
        if resp.status_code >= 400:
            logger.warn("Response status code fail:" + str(resp.status_code))
    token_extract_obj = token_extract()
    token_extract_obj.feed(resp.text)
    token = token_extract_obj.get_token()
    logger.info("token extracted: "+ token)
    data = {'__RequestVerificationToken' : token,
            'studentNo':'', 'studentName':'',
            'mobile':'null;userAgent:WeChat;os:null;Webkit:537.36',
            'Loction':'',
            'LoctionSatus':'true',
            'Country':'中国',
            'Province':'上海市',
            'City':'上海市',
            'AtSchool':'true',
            'rSchool':'true',
            'Accommodation':'1',
            'Fever':'false',
            'rfever':'false',
            'Temperature':'℃',
            'Quarantine':'false',
            'rQuarantine':'false',
            'QAdress':'',
            'SuspectedOrConfirmed':'0',
            'rsoc':'0',
            'hesuanState':'02',
            'hesuan':'02',
            'checkHSReason':'',
            'HSReasonDesc':'',
            'Remark':'',
            'X-Requested-With':'XMLHttpRequest'
            }
    logger.info("forwarding data: https://oa.shsmu.edu.cn/WProtalInfo_WeChat/InformationReporting/InformationReporting")
    try :
        post = requests.post(url, data = data, timeout = 3)
        logger.info(post)
    except(requests.exceptions.Timeout, requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout) as e:
        logger.warn("Request exceptions:" + str(e))
    else:
        if post.status_code >= 400:
            logger.warning("Response status code fail:" + str(resp.status_code))
    logger.info("Post completed: " + post.text)
    subject = "Please note: Today's health check"
    logger.info("Done, sending message: " + post.text + "to ")
    log_contents = log_str.getvalue()
    sendEmail(mail_user, "", subject, log_contents.lower())
    log_str.close()
    return True

if __name__ == "__main__":
    main_handler(None,None)
