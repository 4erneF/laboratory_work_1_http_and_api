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

Проверяется только в клиенте:
- статус ответа проверяется до разбора тела (404 -> CoffeeNotFoundError)
- перед .json() проверяется Content-Type: application/json
- id для PUT/PATCH/DELETE берётся только из ответа POST
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
        return self._json(response)
    
    def get_drink(self, drink_id: int) -> JsonObject:
        response = self._request("GET", f"/{drink_id}")
        return self._json_object(response)
    def create_drink(self, payload: JsonObject) -> JsonObject:
        response = self._request("POST", payload=payload)
        created = self._json(response)
        if not isinstance(created, dict):
            raise CoffeeApiError("Ответ POST не объект")
        drink_id = created.get("id")
        if isinstance(drink_id, bool) or not isinstance(drink_id, int):
            raise CoffeeApiError(f"В ответе POST id не целое число: {drink_id!r}")
        return created
    
    def replace_drink(
        self,
        drink_id: int,
        payload: JsonObject,
    ) -> JsonObject:
        response = self._request("PUT", f"/{drink_id}", payload)
        return self._json_object(response)

    def update_drink(
        self,
        drink_id: int,
        changes: JsonObject,
    ) -> JsonObject:
        response = self._request("PATCH", f"/{drink_id}", changes)
        return self._json_object(response)

    def delete_drink(self, drink_id: int) -> None:
        self._request("DELETE", f"/{drink_id}")

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
        except requests.Timeout as error:
            raise CoffeeApiError(
                f"{method} {url}: нет ответа за {self._timeout} с, результат неизвестен"
            ) from error
        except requests.RequestException as error:
            raise CoffeeApiError(f"{method} {url}: ошибка сети") from error
        if response.status_code == 404:
            raise CoffeeNotFoundError(f"{method} {url}: не найдено (404)")
        if not 200 <= response.status_code < 300:
            raise CoffeeApiError(f"{method} {url}: HTTP {response.status_code}")
        return response

    def _json(self, response: requests.Response) -> object:
        content_type = response.headers.get("Content-Type", "")
        if "application/json" not in content_type:
            raise CoffeeApiError(f"Ожидали JSON, пришло: {content_type}")
        try:
            return response.json()
        except ValueError as error:
            raise CoffeeApiError("Сервер прислал битый JSON") from error

    def _json_object(self, response: requests.Response) -> JsonObject:
        data = self._json(response)
        if not isinstance(data, dict):
            raise CoffeeApiError("Ожидали JSON-объект напитка")
        return data