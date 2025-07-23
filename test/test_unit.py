from app import ItemList, Item, items_db, current_id
import pytest

@pytest.fixture(autouse=True)
def run_around_tests():
    # Código que se ejecuta antes de cada prueba
    global items_db, current_id
    items_db.clear()
    current_id = 1
    yield
    # Código que se ejecuta después de cada prueba
    items_db.clear()
    current_id = 1

def test_item_creation():
    """Prueba unitaria de la creación de un ítem."""
    item_list = ItemList()
    # Simulamos el contexto de la petición
    with pytest.raises(RuntimeError):  # request.json no estará disponible
        item_list.post()

    # Este tipo de prueba es más útil para lógica que no depende del request