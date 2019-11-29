import smtplib

class EmailManager:
    SMTP_SERVER_ADDRESS = "smtp.gmail.com"
    SMTP_SERVER_PORT = 465
    ORIGIN_EMAIL = "8yesayesa@gmail.com"
    ORIGIN_EMAIL_PASS = "fxeiwcxqryrjhocb"
    SUBJECT = "Welcome to Telkom CloudPBX"
    BODY = "Hello. Welcome to Telkom CloudPBX. Please use the service wisely."

    @staticmethod
    def send_email(destination_email):
        content = """\
From: {0}
To: {1}
Subject: {2}
{3}
""".format(EmailManager.ORIGIN_EMAIL, destination_email, EmailManager.SUBJECT, EmailManager.BODY)

        try:
            server = smtplib.SMTP_SSL(EmailManager.SMTP_SERVER_ADDRESS, EmailManager.SMTP_SERVER_PORT)
            server.ehlo()
            server.login(EmailManager.ORIGIN_EMAIL, EmailManager.ORIGIN_EMAIL_PASS)
            server.sendmail(EmailManager.ORIGIN_EMAIL, destination_email, content)
            server.close()
            print("Email sent.")
        except Exception as e:
            raise e

if __name__ == "__main__":
    EmailManager.send_email("ysyesayesa@gmail.com")
