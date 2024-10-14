import os
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

#Define the OAuth 2.0 scope (send only)
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


gmail_credentials = "my_email_auth_creds.json"       # Replace this, get from Google gmail api credentials


def authenticate_gmail():
    creds = None
    if os.path.exists('token.js'):
        creds = Credentials.from_authorized_user_file('token.js',SCOPES)
    if not creds or not creds.valid():                                                              #if token.js does not exist, generate one
        flow = InstalledAppFlow.from_client_secrets_file(gmail_credentials,SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json','w') as token:
            token.write(creds.to_json())
    return creds

def create_message(sender, recipient, subject, body, attachement_path):
    message = MIMEMultipart()
    message['to'] = recipient
    message['from'] = sender
    message['subject'] = subject
     # Add the CC field if there are any CC recipients
    # message['Cc'] = "example@gmail.com"                   #uncomment if there is a CC

    message.attach(MIMEText(body, 'html'))                                    # add the body text to email using html formatting to include links

    #open attached file as read binary mode  and attach it to the email
    with open(attachement_path,'rb') as attachement:        
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachement.read())

    encoders.encode_base64(part)                                
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {os.path.basename(attachement_path)}",
    )

    message.attach(part)
    return message


def send_email_via_oauth2_only(creds, sender_email, recipient_email, subject, body, attachement_path):
    access_token = creds.token
    message = create_message(sender_email, recipient_email , subject, body, attachement_path)
     # Encode the message
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
      # Create the service
    service = build('gmail', 'v1', credentials=creds)
     # Send the email using the Gmail API
    try:
        service.users().messages().send(userId="me", body={'raw': raw_message}).execute()
        print(f"Email sent to {recipient_email}")
    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    creds = authenticate_gmail()
    sender_email = "my_email@gmail.com"              
   
    recipient_emails = ["email1@gmail.com"]      # you can add multiple recipient emails to do a one to many email, e.g. ["email1@gmail.com","email2@gmail.com"]
    subject = ""        # add subject
    body = """
    <html>
    <body>
    <pre>
  
    ###Your message here!####
   
    
        
    </pre>
    </body>
    </html>
    """
    attachement_path = "resume.pdf"   # your attachement here

    for recipient_email in recipient_emails:
        send_email_via_oauth2_only(creds=creds,sender_email=sender_email, recipient_email=recipient_email,subject=subject,body=body,attachement_path=attachement_path)

if __name__ == '__main__':

    main()