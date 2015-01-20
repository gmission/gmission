__author__ = 'chenzhao'

######################################
# DO NOT RENAME THIS FILE TO email.py
######################################


# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.mime.text import MIMEText


gmail_user, gmail_password = 'gmission.from.hkust@gmail.com','csp2014hkust'


def invalid_receiver(receiver):
    return 'test.com' in receiver or 'xxx.com' in receiver
    pass


def send(subject, body, receiver):
    if invalid_receiver(receiver):
        return False
    msg = MIMEText(body)

    msg['Subject'] = subject
    msg['From'] = gmail_user
    msg['To'] = receiver

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(gmail_user, gmail_password)

    server.sendmail(gmail_user, [receiver, ], msg.as_string())
    server.quit()
    return True


if __name__ == '__main__':
    send('test', 'body', 'zchenah@ust.hk')