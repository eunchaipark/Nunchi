import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.config.settings import settings
from app.domains.notification.repository import NotificationRepository


class NotificationService:
    def __init__(self, repo: NotificationRepository):
        self.repo = repo

    async def check_and_notify(self, user_id: int, overall_risk: float) -> None:
        # 위험도 7.0 이상일 때만 알림
        if overall_risk < 7.0:
            return

        # 보호자 목록 조회
        guardians = await self.repo.get_guardians_by_elder(user_id)
        if not guardians:
            return

        # 보호자마다 알림 발송
        for guardian in guardians:
            if not guardian.email:
                continue

            # 이메일 발송
            success = self._send_email(
                to_email=guardian.email,
                user_id=user_id,
                trigger_score=overall_risk,
            )

            if success:
                await self.repo.save_notification(
                    user_id=user_id,
                    guardian_id=guardian.id,
                    trigger_score=overall_risk,
                    channel="email",
                )

    @staticmethod
    def _send_email(to_email: str, user_id: int, trigger_score: float) -> bool:
        try:
            msg = MIMEMultipart()
            msg["From"] = settings.GMAIL_USER
            msg["To"] = to_email
            msg["Subject"] = "[눈치] 담당 어르신 위험 알림"

            body = f"""
안녕하세요.

담당 어르신(ID: {user_id})의 오늘 감정 위험도가 {trigger_score}점으로 높게 측정되었습니다.

위험도 기준:
- 안정: 5.0 미만
- 주의: 5.0 ~ 7.0
- 위험: 7.0 이상

빠른 확인 부탁드립니다.

눈치 서비스
            """
            msg.attach(MIMEText(body, "plain"))

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(settings.GMAIL_USER, settings.GMAIL_APP_PASSWORD)
                server.sendmail(settings.GMAIL_USER, to_email, msg.as_string())

            return True
        except Exception as e:
            print(f"이메일 발송 실패: {e}")
            return False
