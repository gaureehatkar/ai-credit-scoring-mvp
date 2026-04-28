import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings


class EmailService:
    def __init__(self):
        self.smtp_host = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = settings.GMAIL_ADDRESS
        self.sender_password = settings.GMAIL_APP_PASSWORD

    def _send(self, msg):
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.sendmail(self.sender_email, msg["To"], msg.as_string())

    def send_status_notification(self, to_email: str, full_name: str, application_id: int, new_status: str, reason: str = None):
        """Send email when admin approves or rejects an application"""
        status_display = new_status.replace("_", " ").upper()
        color = "#4CAF50" if new_status == "approved" else "#f44336" if new_status == "rejected" else "#FF9800"
        emoji = "✅" if new_status == "approved" else "❌" if new_status == "rejected" else "🔍"

        reason_html = f"<p><strong>Reason/Notes:</strong> {reason}</p>" if reason else ""

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"{emoji} Loan Application #{application_id} — {status_display}"
        msg["From"] = self.sender_email
        msg["To"] = to_email

        html = f"""
        <html><body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto">
        <div style="background:#1a1a2e;padding:24px;border-radius:8px">
          <h2 style="color:white;margin:0">AI Credit Scoring Platform</h2>
        </div>
        <div style="padding:24px;border:1px solid #eee;border-radius:0 0 8px 8px">
          <p>Dear <strong>{full_name}</strong>,</p>
          <p>Your loan application <strong>#{application_id}</strong> has been reviewed.</p>
          <div style="background:{color}15;border-left:4px solid {color};padding:16px;margin:16px 0;border-radius:4px">
            <h3 style="color:{color};margin:0">Status: {status_display}</h3>
          </div>
          {reason_html}
          <p>Log in to your dashboard to view full details.</p>
          <p style="color:#666;font-size:12px;margin-top:32px">AI Credit Scoring Platform — Vishwakarma Institute of Technology</p>
        </div>
        </body></html>
        """
        msg.attach(MIMEText(html, "html"))
        self._send(msg)

    def send_verification_email(self, to_email: str, full_name: str, token: str):
        """Send email verification link"""
        verify_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"

        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Verify your email - AI Credit Scoring"
        msg["From"] = self.sender_email
        msg["To"] = to_email

        html = f"""
        <html><body>
        <h2>Welcome, {full_name}!</h2>
        <p>Please verify your email address to activate your account.</p>
        <a href="{verify_url}" style="
            background:#3498db;color:white;padding:12px 24px;
            text-decoration:none;border-radius:4px;display:inline-block;margin:16px 0
        ">Verify Email</a>
        <p>Or copy this link: <a href="{verify_url}">{verify_url}</a></p>
        <p>This link expires in 24 hours.</p>
        </body></html>
        """

        msg.attach(MIMEText(html, "html"))
        self._send(msg)
