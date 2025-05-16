import smtplib
import os
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText

import pandas as pd

FROM = "iagoerrerareserva@gmail.com"
TO = "iagoerrerareserva@gmail.com"
PASS = "psmzhmcjpychfmhj"

def send_email(_from, to, _pass, subject, body, filename):
    msg = MIMEMultipart()
    msg['To'] = Header(to)
    msg['From'] = Header(_from)
    msg['Subject'] = Header(subject)
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    attachment_name = os.path.basename(filename) 
    with open(filename, 'rb') as f:
        attachment = MIMEApplication(f.read(), _subtype='csv')
    attachment.add_header('Content-Disposition', 'attachemnt', filename=attachment_name)
    msg.attach(attachment)

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(_from, _pass)
    server.sendmail(_from, to, msg.as_string())

def fix_data(filename_data, filename_fixed):
    data = pd.read_csv(filename_data)
    data.drop_duplicates(subset=['headline', 'link'])
    data = data[~((data['headline'] == 'headline') & (data['link'] == 'link'))]

    data.to_csv(filename_fixed, index=False)

if __name__ == '__main__':
    body = """Here is the news from yesterday"""
    filename_data = "data.csv"
    filename_fixed = "news.csv"
    
    fix_data(filename_data, filename_fixed)
    send_email(FROM, TO, PASS, body, filename_fixed)