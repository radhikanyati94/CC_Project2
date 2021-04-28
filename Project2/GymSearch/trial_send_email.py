import smtplib

gmail_user = 'ssridh55@asu.edu'
gmail_password = 'SenderEmailPassword'

sent_from = gmail_user
to = ['RecipientEmailAddress@gmail.com']
subject = 'Test e-mail from Python'
body = 'Test e-mail body'

email_text = """\
From: %s
To: %s
Subject: %s

%s
""" % (sent_from, ", ".join(to), subject, body)

server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
server.ehlo()
server.login(gmail_user, gmail_password)
server.sendmail(sent_from, to, email_text)
server.close()
print('Email sent!')