from uuid import uuid4

from app.client import SampleApisCoffeeClient
from app.exceptions import CoffeeApiError, CoffeeNotFoundError

def check_fields(expected: dict, actual: dict, stage: str) -> None:
    for field, value in expected.items():
        if actual[field] != value:
            raise ValueError(f"{stage}: поле {field}: ожидали {value}, получили {actual[field]}")
def main() -> int:
    client = SampleApisCoffeeClient()
    marker = uuid4().hex[:8]
    created_id = None
    try:
        # GET коллекции.
        # POST: исследуйте поля, добавьте marker в название.
        # Сразу сохраните id из ответа в created_id.
        # GET: сравните сохранённые поля с отправленными.
        # PUT и повторный GET: проверьте все заменённые поля.
        # PATCH и повторный GET: проверьте изменённое поле
        # и убедитесь, что остальные поля сохранились.
        # DELETE и GET: убедитесь, что вернулся ожидаемый 404.
        # После подтверждения удаления: created_id = None.
        drinks = client.list_drinks()
        print(f"1. GET: в коллекции {len(drinks)} напитков")

        new_drink = {
            "title": f"Group coffee {marker}",
            "description": "Hot drink",
            "ingredients": ["Water", "Coffee"],
            "image": "https://example.com/coffee.jpg",
        }
        created = client.create_drink(new_drink)
        created_id = created["id"]
        print(f"2. POST: создан напиток id={created_id}")
        fetched = client.get_drink(created_id)
        check_fields(new_drink, fetched, "3. GET")
        print("3. GET: все поля совпали с отправленными")
    except (CoffeeApiError, ValueError) as error:
        print(f"Ошибка: {error}. Метка группы: {marker}")
        return 1
    finally:
        if created_id is not None:
            try:
                client.delete_drink(created_id)
            except CoffeeNotFoundError:
                pass
            except CoffeeApiError as error:
                print(f"Не удалось удалить id={created_id}: {error}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
