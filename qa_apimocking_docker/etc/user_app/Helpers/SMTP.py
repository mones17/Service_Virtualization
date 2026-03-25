from genericpath import isfile
import smtplib  
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart 
from email.mime.image import MIMEImage
import base64

message_html = """  
<html>
<head>
  <style>
    * {
      margin: 0;
      padding: 0;
    }
    body {
      font-family: Arial, sans-serif;
      background-color: #f6f6f6;
    }
    .container {
      max-width: 800px;
      margin: 0 auto;
      background-color: #ffffff;
      border-radius: 10px;
      overflow: hidden;
    }
 
    .header {
      background-color: #f6f6f6;
      padding: 20px;
      display: flex;
      justify-content: center;
      border-radius: 10px 10px 0 0;
    }
 
    .mail-body {
      padding: 20px;
    }
 
    h1 {
      color: #6f42c1;
    }
 
    p {
      color: #333333;
    }
 
    .btn {
      display: inline-block;
      padding: 10px 20px;
      background-color: #6f42c1;
      color: #ffffff;
      text-decoration: none;
      border-radius: 5px;
      margin-top: 12px;
      margin-bottom: 16px;
    }
     
    .image {
      display: block;
      margin: 0 auto;
      margin-bottom: 24px;
      width: 280px;
      height: auto;
    }
   
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Welcome to Solera service virtualizer!</h1>
    </div>
    <div class="mail-body">
      <img class ="image" src="data:image/png;base64,[Logo_Base_64]" alt="SSV Logo" height="150" width="500">
      <p style="margin-bottom: 12px;">Welcome to SSV (Virtualization Web Platform), We are thrilled to have you as part of our community!</p>
      <p>To get started, click the button below to create your login credentials so you can enjoy all the benefits that SSV has to offer:</p>
      <a href="[Insert link here]" class="btn">Get Started</a>
      <p>Remember, we are here to assist you every step of the way. If you have any questions or need assistance, feel free to reach out to our support team via <a href="mailto:claudio.mones@solera.com">claudio.mones@solera.com</a> or <a href="mailto:luis.banderas@solera.com">luis.banderas@solera.com</a> or by using the live chat option on our platform.</p>
      <p style="margin-top: 12px;">Welcome again, and have a fantastic SSV experience!</p>
      <p style="margin-top: 14px;">Best regards,</p>
      <p>QA Team & SSV Team</p>
 
    </div>
  </div>
</body>
</html>
"""
  
def SendEmail(email_to, link):
    # Setups the SMTP server details
    server_smtp = 'mrelay.audatex.com'
    port_smtp = 25

    # Convert the PNG image to base 64
    image_path = '/home/python/app/Resources/SSVLogo.png'
    with open(image_path, 'rb') as image_file:  
        image_data = image_file.read()  
        image_base64 = base64.b64encode(image_data).decode('utf-8')

    # Create the object MIMEText with the email details
    mensaje = message_html.replace("[Insert link here]", link).replace("[Logo_Base_64]", image_base64)
    email = MIMEMultipart()
    email.attach(MIMEText(mensaje, 'html'))
    email['Subject'] = 'SSV Credentials'
    email['From'] = 'qa.admin@solera.com'
    email['To'] = email_to
  
    # Start a connection to the SMTP server and send the email
    with smtplib.SMTP(server_smtp, port_smtp) as smtp_server:
        smtp_server.starttls()
        smtp_server.send_message(email)