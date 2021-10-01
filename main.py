import requests
import sys
import os
import io

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")

import datetime
import logging
import json
import requests
from email.mime.text import MIMEText
from email.header import Header
import smtplib

logger = logging.getLogger()
log_str = io.StringIO()
fh = logging.StreamHandler(log_str)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
fh.setFormatter(formatter)
logger.addHandler(ch)
logger.addHandler(fh)


# Third-party SMTP service for sending alert emails. 第三方 SMTP 服务，用于发送告警邮件
mail_host = "smtp.qq.com"       # SMTP server, such as QQ mailbox, need to open SMTP service in the account. SMTP服务器,如QQ邮箱，需要在账户里开启SMTP服务
mail_user = "2590187490@qq.com"  # Username 用户名
mail_pass = "fprrvocwgjojebbc"  # Password, SMTP service password. 口令，SMTP服务密码
mail_port = 465  # SMTP service port. SMTP服务端口

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
        print("send email success")
        return True
    except smtplib.SMTPException as e:
        print(e)
        print("Error: send email fail")
        return False

def main_handler(event, context):
    resp = None
    url="https://oa.shsmu.edu.cn/WProtalInfo_WeChat/InformationReporting/InformationReporting"
    logger.info('Accessing：'+url)
    try:
        resp = requests.get(url, cookies={"cookie":"ASP.NET_SessionId=2pl5qktc4abmp0w4nmww3tsa"}, timeout=3)
        logger.info(resp)
    except(requests.exceptions.Timeout, requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout) as e:
        logger.warning("request exceptions:" + str(e))
    else:
        if resp.status_code >= 400:
            logger.warn("response status code fail:" + str(resp.status_code))
    temp = resp.text.rfind('<input name="__RequestVerificationToken" type="hidden" value="') + 62
    token = resp.text[temp:temp+108]
    logger.info("token acquired："+ token)
    data = {'__RequestVerificationToken' : token,
            'studentNo':'520712910019', 'studentName':'陳鎧之',
            'mobile':'null;userAgent:WeChat;os:null;Webkit:537.36',
            'Loction':'上海市黄浦区淮海中路街道合肥路365号上海交通大学医学院东区',
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
            'Remark':''}
    logger.info("forwarding data: https://oa.shsmu.edu.cn/WProtalInfo_WeChat/InformationReporting/InformationReporting")
    try :
        post = requests.post(url, data = data, timeout = 3)
        logger.info(post)
    except(requests.exceptions.Timeout, requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout) as e:
        logger.warn("request exceptions:" + str(e))
    else:
        if post.status_code >= 400:
            logger.warning("response status code fail:" + str(resp.status_code))
    logger.info("post completed：" + post.text)
    subject = "Please note: Today's health check"
    logger.info("done, sending message" + post.text + "to thomaschan32866@gmail.com")
    log_contents = log_str.getvalue()
    sendEmail(mail_user, "thomaschan32866@gmail.com", subject, log_contents.lower())
    log_str.close()
    return True
if __name__ == '__main__':
    main_handler("", "")
