import smtplib, os
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

EMAIL_USER = os.environ['EMAIL_USER']
EMAIL_PASS = os.environ['EMAIL_PASS']
EMAIL_TO = os.environ.get('EMAIL_TO', EMAIL_USER)

# Construct filename based on today's UTC date
date_str = datetime.utcnow().strftime("%Y-%m-%d")
file_path = f"option_chain_{date_str}.json"

# Create the email
msg = MIMEMultipart()
msg['From'] = EMAIL_USER
msg['To'] = EMAIL_TO
msg['Subject'] = f"NSE Option Chain Data - {date_str}"

# Attach file
try:
    with open(file_path, 'rb') as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename="{file_path}"')
    msg.attach(part)
except FileNotFoundError:
    print(f"❌ File not found: {file_path}")
    exit(1)

# Send email via Gmail SMTP
try:
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, EMAIL_TO, msg.as_string())
    print("✅ Email sent successfully")
except Exception as e:
    print(f"❌ Email sending failed: {e}")
