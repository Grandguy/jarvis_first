import asyncio
import aiosmtplib
from email.mime.text import MIMEText
from app.core.config import settings

async def test_smtp():
    print(f"Testing SMTP with {settings.SMTP_HOST}:{settings.SMTP_PORT}")
    print(f"User: {settings.SMTP_USER}")
    
    msg = MIMEText("Test connection")
    msg["Subject"] = "SMTP Test"
    msg["From"] = settings.SMTP_FROM
    msg["To"] = settings.SMTP_USER # Send to self
    
    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            use_tls=True if settings.SMTP_PORT == 465 else False,
            start_tls=True if settings.SMTP_PORT == 587 else False,
            timeout=10
        )
        print("SMTP Success!")
    except Exception as e:
        print(f"SMTP Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_smtp())
