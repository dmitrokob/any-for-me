from plyer import notification
from models.deadline import Deadline
import config


class NotificationManager:
    def __init__(self):
        self.last_notification_time = {}

    def send_urgent_notification(self, deadline: Deadline):
        """Отправляет уведомление для срочного дедлайна"""
        try:
            days_remaining = (deadline.deadline - deadline.created).days

            notification.notify(
                title="⚠️ СРОЧНЫЙ ДЕДЛАЙН!",
                message=(
                    f"'{deadline.name}'\n"
                    f"Осталось {days_remaining} дн.\n"
                    f"Нужно {deadline.days_needed} дн. на выполнение!"
                ),
                timeout=config.NOTIFICATION_TIMEOUT,
                toast=True
            )
            print(f"Уведомление отправлено для: {deadline.name}")
        except Exception as e:
            print(f"Ошибка отправки уведомления: {e}")

    def should_send_notification(self, deadline_name: str, current_time) -> bool:
        """Проверяет, можно ли отправлять уведомление (не чаще чем раз в час)"""
        last_notified = self.last_notification_time.get(deadline_name)

        if last_notified is None:
            return True

        time_since_last = (current_time - last_notified).total_seconds()
        return time_since_last >= config.NOTIFICATION_COOLDOWN

    def update_notification_time(self, deadline_name: str, current_time):
        """Обновляет время последнего уведомления"""
        self.last_notification_time[deadline_name] = current_time