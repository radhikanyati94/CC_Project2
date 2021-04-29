# import smtplib

# gmail_user = 'ssridh55@asu.edu'
# gmail_password = 'SenderEmailPassword'

# sent_from = gmail_user
# to = ['RecipientEmailAddress@gmail.com']
# subject = 'Test e-mail from Python'
# body = 'Test e-mail body'

# email_text = """\
# From: %s
# To: %s
# Subject: %s

# %s
# """ % (sent_from, ", ".join(to), subject, body)

# server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
# server.ehlo()
# server.login(gmail_user, gmail_password)
# server.sendmail(sent_from, to, email_text)
# server.close()
# print('Email sent!')


from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__)
mail= Mail(app)
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'noreply.gymsearch@gmail.com'
app.config['MAIL_PASSWORD'] = 'Test@12345'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

@app.route("/")
def index():
   msg = Message('Hello', sender = 'noreply.gymsearch@gmail.com', recipients = ['srihariravi7@gmail.com', 'ssridh55@asu.edu'])
   msg.body = "Hello User, Gym information is updated ! https://8080-cs-621499849372-default.cs-us-west1-olvl.cloudshell.dev/gyms/Spot%20Fitness%20and%20Spa"
   mail.send(msg)
   return "Sent"

if __name__ == '__main__':
   app.run(debug = True)