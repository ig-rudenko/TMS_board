import requests
from django.conf import settings


class TGNotify:
    _url = f"https://api.telegram.org/bot{settings.TG_TOKEN}"

    def send_message(self, message: str, to_user_tg_id: int) -> bool:
        json_data = {"chat_id": to_user_tg_id, "text": message}

        # https://api.telegram.org/bot{TG_TOKEN}/sendMessage
        resp = requests.post(f"{self._url}/sendMessage", json=json_data)

        return resp.status_code == 200


tg_notify = TGNotify()
