import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import ApiConfig
from app.exceptions.exceptions import EmailException
from app.models.user import UserIn
from app.utils.auth_utils import AuthUtils
from app.utils.html import account_activation_html


class EmailService:
    def __init__(self, config: ApiConfig):
        self.config = config
        self.smtp_server = config.MAIL_SERVICE
        self.sender = config.MAIL_SERVICE_USER
        self.password = config.MAIL_SERVICE_PASSWORD
        self.message = None
        self.recipient = None

    def configure_mail(self, recipient, subject, body):
        message = MIMEMultipart()
        message["From"] = self.sender
        message["To"] = recipient
        message["Subject"] = subject
        message.attach(MIMEText(body, "html"))

        self.recipient = recipient
        self.message = message

    def send_mail(self):
        if not self.recipient or not self.message:
            raise EmailException("Email service is not configured")
        try:
            with smtplib.SMTP(self.smtp_server, 587) as server:
                server.set_debuglevel(1)
                server.starttls()
                server.login(self.sender, self.password)
                server.sendmail(self.sender, self.recipient, self.message.as_string())
        except Exception as e:
            raise EmailException(f"Error sending email: {str(e)}")


class AuthEmailService(EmailService):
    def __init__(self, config: ApiConfig, auth_utils: AuthUtils):
        self.auth_utils = auth_utils
        super().__init__(config)

    def configure_auth_mail(self, request: UserIn):
        subject = "Account activation"
        link = self.auth_utils.generate_verification_link(request)
        body = account_activation_html(request.email, link)
        super().configure_mail(request.email, subject, body)
