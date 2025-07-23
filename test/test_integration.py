import json

def test_get_items(client):
    """Prueba para obtener todos los ítems."""
    response = client.get('/items/')
    assert response.status_code == 200
    assert response.json == []

def test_create_item(client):
    """Prueba para crear un ítem."""
    response = client.post('/items/', json={'name': 'Nuevo Ítem', 'description': 'Descripción'})
    assert response.status_code == 201
    data = response.json
    assert data['name'] == 'Nuevo Ítem'
    assert 'id' in data

def test_get_item(client):
    """Prueba para obtener un ítem específico."""
    # Primero crea un ítem para obtener
    post_response = client.post('/items/', json={'name': 'Ítem de prueba'})
    item_id = post_response.json['id']

    response = client.get(f'/items/{item_id}')
    assert response.status_code == 200
    assert response.json['name'] == 'Ítem de prueba'

def test_update_item(client):
    """Prueba para actualizar un ítem."""
    post_response = client.post('/items/', json={'name': 'Ítem Original'})
    item_id = post_response.json['id']

    response = client.put(f'/items/{item_id}', json={'name': 'Ítem Actualizado', 'description': 'Nueva Descripción'})
    assert response.status_code == 200
    assert response.json['name'] == 'Ítem Actualizado'

def test_delete_item_with_confirmation(client):
    """
    Prueba la eliminación de un ítem, cubriendo los casos de confirmación.
    """
    # --- 1. Arrange: Crear un ítem para tener algo que eliminar ---
    post_response = client.post('/items/', json={'name': 'Ítem para eliminar', 'description': 'Prueba de borrado'})
    assert post_response.status_code == 201
    item_id = post_response.json['id']

    # --- 2. Act & Assert: Intentar eliminar SIN confirmación ---
    # Se espera un error 400 Bad Request
    response_no_confirm = client.delete(f'/items/{item_id}')
    assert response_no_confirm.status_code == 400
    assert 'Debe confirmar la eliminación' in response_no_confirm.json['message']

    # --- 3. Act & Assert: Intentar eliminar un ítem que NO EXISTE ---
    # Se espera un error 404 Not Found
    response_not_found = client.delete('/items/999?confirm=true')
    assert response_not_found.status_code == 404

    # --- 4. Act & Assert: Eliminar el ítem CON confirmación (caso de éxito) ---
    # Se espera un código 204 No Content, que indica éxito sin devolver cuerpo
    response_confirm = client.delete(f'/items/{item_id}?confirm=true')
    assert response_confirm.status_code == 204
    assert response_confirm.data == b'' # El cuerpo de la respuesta está vacío

    # --- 5. Verify: Comprobar que el ítem ya no se puede obtener ---
    # Se espera un error 404 Not Found porque el ítem fue eliminado
    get_response_after_delete = client.get(f'/items/{item_id}')
    assert get_response_after_delete.status_code == 404