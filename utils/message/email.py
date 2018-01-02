import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

from .base import BaseMessage


class Email(BaseMessage):
    def __init__(self, email, user, pwd):
        self.email = email
        self.user = user
        self.pwd = pwd

    def send(self, subject, body, email, name):
        msg = MIMEText(body, 'plain', 'utf-8')  # 发送内容
        msg['from'] = formataddr([self.user, self.email])  # 发件人的姓名和邮箱
        msg['to'] = formataddr([name, email])  # 收件人姓名和邮箱
        msg['subject'] = subject  # 发送主题

        server = smtplib.SMTP("smtp.126.com", 25)  # SMTP服务
        server.login(self.email, self.pwd)  # 登录邮箱
        server.sendmail(self.email, [email, ], msg.as_string())  # 发送者和接收者以及msg
        server.quit()

