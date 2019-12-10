import smtplib
from model.email import Email
from secret import Secret

class EmailManager:
    @staticmethod
    def send_email(email):
        print(email.destination)
        print(email.subject)
        print(email.body)
        content = """\
From: {0}
To: {1}
Subject: {2}
{3}
""".format(Secret.ORIGIN_EMAIL, email.destination, email.subject, email.body)

        try:
            server = smtplib.SMTP_SSL(Secret.SMTP_SERVER_ADDRESS, Secret.SMTP_SERVER_PORT)
            server.ehlo()
            server.login(Secret.ORIGIN_EMAIL, Secret.ORIGIN_EMAIL_PASS)
            server.sendmail(Secret.ORIGIN_EMAIL, email.destination, content)
            server.close()
            print("Email sent.")
        except Exception as e:
            raise e

if __name__ == "__main__":
    an_email = Email(subject="Welcome to CloudPBX",
                     body="Please use the service wisely.",
                     destination="ysyesayesa@gmail.com")
    EmailManager.send_email(an_email)
