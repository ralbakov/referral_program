import smtplib
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import bcrypt
import jwt

from core.config import settings


def encode_jwt(
    payload: dict,
    private_key: str = settings.auth.private_key_path.read_text(),
    algorithm: str = settings.auth.algorithm,
    expire_minutes: float = settings.auth.access_token_expire_minutes,
    expire_timedelta: timedelta | None = None,
) -> str:
    to_encode = payload.copy()
    now = datetime.now(timezone.utc)
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_minutes)
    to_encode.update(
        exp=expire,
        iat=now,
    )
    encoded = jwt.encode(
        to_encode,
        private_key,
        algorithm=algorithm,
    )
    return encoded  # type: ignore


def decode_jwt(
    token: str | bytes,
    public_key: str = settings.auth.public_key_path.read_text(),
    algorithm: str = settings.auth.algorithm,
) -> dict:
    decoded = jwt.decode(
        token,
        public_key,
        algorithms=[algorithm],
    )
    return decoded


def hash_password(password: str) -> bytes:
    salt: bytes = bcrypt.gensalt()
    password_bytes: bytes = password.encode()
    return bcrypt.hashpw(password_bytes, salt)


def validate_password(password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(
        password=password.encode(),
        hashed_password=hashed_password,
    )


def send_key_for_reset_password(email: str, key: str) -> None:
    server = smtplib.SMTP(
        host=settings.emailserver.smtp_host,
        port=settings.emailserver.smtp_port
    )
    password_email = settings.emailserver.password
    msg = MIMEMultipart()
    msg['From'] = settings.emailserver.email
    msg['To'] = f'{email}'
    msg['Subject'] = 'Key for reset password'
    message = f'Your key for reset password: {key}'
    msg.attach(MIMEText(message, 'plain'))
    server.starttls()
    server.login(msg['From'], password_email)
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()
    return None
