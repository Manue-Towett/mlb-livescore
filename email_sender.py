import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailSender:
    """Sends an email notification when the scraper is done collecting data
    
       Args:
          - settings: settings retrieved from the json file
    """
    def __init__(self, settings:dict) -> None:
        self.sender_address = settings["sending email"]
        self.sender_pass = settings["app password"]
        self.receiver_address = settings["receiving email"]
    
    def __extract_message(self, message_data:dict[str, dict[str, dict]]) -> str:
        """Extracts the message to be send from a dictionary
        
           Arg:
             - message_data: a dictionary containing items to be included in the message
        """
        message_email = ""

        for tikr, value in message_data.items():
            message_email = message_email + tikr + "\n"

            for message_dict in value.values():
                for key, val in message_dict.items(): 
                    message_email = message_email + key + str(val) + "\n"
            
        mail_content = 'Hello, Below is the Tikr summary information regarding '\
                      f'the latest run: \n{message_email}'
        
        return mail_content
    
    def send_email(self, message_data:dict[str, dict[str, dict]]) -> None:
        """Sends an email with logs showing the number of csv rows extracted for each tikr
        
           Arg:
             - message_data: a dictionary containing items to be included in the message
        """
        print("Sending email...")

        mail_content = self.__extract_message(message_data)

        mail_content = "This is just a test"

        message = MIMEMultipart()
        message['From'] = self.sender_address
        message['To'] = self.receiver_address
        message['Subject'] = f'Test email'
        message.attach(MIMEText(mail_content, 'plain'))

        session = smtplib.SMTP('webhost.dynadot.com', 587)
        session.starttls() 
        session.login(self.sender_address, self.sender_pass)

        text = message.as_string()

        session.sendmail(self.sender_address, self.receiver_address, text)
        session.quit()

        print("Email sent!")

sender = EmailSender({"sending email": "support@atswins.ai",
                      "app password": "18238675",
                      "receiving email": "etowett6@gmail.com"})
sender.send_email({})