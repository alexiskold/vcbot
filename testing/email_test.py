# from .. import cb_scraping

import smtplib
import datetime

from email.mime.text import MIMEText

def send_email( sender, addresses, content ):
    d = datetime.datetime.strftime( datetime.datetime.today(), "%m-%d-%Y" )

    msg = MIMEText( content, 'html' )
    msg['Subject'] = d + ': startups to review'
    msg['From'] = sender
    msg['To'] = ','.join(addresses)

    s = smtplib.SMTP('smtp.gmail.com', 465)
    s.ehlo()
    s.starttls()
    s.login('yoland68@gmail', '08CEO...cn!')
    s.sendmail( sender, addresses, msg.as_string() )
    s.quit()

def email_testing():
    send_email("yoland68@gmail.com", ["yoland.yan@techstars.com"], "<div>Hello</div>")

if __name__ == "__main__":
    email_testing()