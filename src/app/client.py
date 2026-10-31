"""
Описание запроса создания горячего кофе
---------------------------------------
Метод и URL: POST https://api.sampleapis.com/coffee/hot

Заголовки: Content-Type: application/json

Поля тела:
- title — строка, обязательное
- description — строка, обязательное
- ingredients — список строк, обязательное
- image — строка (ссылка на картинку), обязательное
- id — не передаём, его ставит сервер

Успешный ответ: 201 Created, в теле созданный напиток вместе с id,
заголовок location: /coffee/hot/<id>

Ошибка: 400, если не хватает обязательного поля.
В ответе сервер пишет, какие поля ожидал (expected) и что получил (received).

Проверено запросами:
- POST с 4 полями -> 201 и id в ответе
- POST без image -> 400
- id передавать не нужно

"""

import requests
from app.exceptions import CoffeeApiError, CoffeeNotFoundError

JsonObject = dict[str, object]


class SampleApisCoffeeClient:
    def __init__(
        self,
        base_url: str = "https://api.sampleapis.com/coffee/hot",
        timeout: float = 10.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    def list_drinks(self) -> list[JsonObject]:
        response = self._request("GET")
        return response.json()
    
    def get_drink(self, drink_id: int) -> JsonObject:
        raise NotImplementedError

    def create_drink(self, payload: JsonObject) -> JsonObject:
        raise NotImplementedError

    def replace_drink(
        self,
        drink_id: int,
        payload: JsonObject,
    ) -> JsonObject:
        raise NotImplementedError

    def update_drink(
        self,
        drink_id: int,
        changes: JsonObject,
    ) -> JsonObject:
        raise NotImplementedError

    def delete_drink(self, drink_id: int) -> None:
        raise NotImplementedError

    def _request(
        self,
        method: str,
        path: str = "",
        payload: JsonObject | None = None,
    ) -> requests.Response:
        url = self._base_url + path
        try:
            response = requests.request(
                method, url, json=payload, timeout=self._timeout
            )
        except requests.RequestException as error:
            raise CoffeeApiError(f"{method} {url}: ошибка сети") from error
        return response
