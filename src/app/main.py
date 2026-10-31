from uuid import uuid4

from app.client import SampleApisCoffeeClient
from app.exceptions import CoffeeApiError, CoffeeNotFoundError

def check_fields(expected: dict, actual: dict, stage: str) -> None:
    for field, value in expected.items():
        if actual.get(field) != value:
            raise ValueError(f"{stage}: поле {field}: ожидали {value}, получили {actual.get(field)}")
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
        replacement = {
            "title": f"Replaced coffee {marker}",
            "description": "Fully replaced",
            "ingredients": ["Espresso"],
            "image": "https://example.com/replaced.jpg",
        }
        client.replace_drink(created_id, replacement)
        check_fields(replacement, client.get_drink(created_id), "GET после PUT")
        print("4. PUT: все поля заменились")
        changes = {"description": "Patched only"}
        client.update_drink(created_id, changes)
        after_patch = client.get_drink(created_id)
        check_fields(changes, after_patch, "GET после PATCH")
        unchanged = {
            "title": replacement["title"],
            "ingredients": replacement["ingredients"],
            "image": replacement["image"],
        }
        check_fields(unchanged, after_patch, "остальные поля после PATCH")
        print("5. PATCH: description изменился, остальные поля на месте")
        client.delete_drink(created_id)
        try:
            client.get_drink(created_id)
        except CoffeeNotFoundError:
            print("6. DELETE: получили ожидаемый 404, напиток удалён")
            created_id = None
        else:
            raise ValueError("Напиток всё ещё доступен после DELETE")
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
