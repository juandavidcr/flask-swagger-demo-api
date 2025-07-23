from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields, Namespace

app = Flask(__name__)
api = Api(app, version='1.0', title='API de Ejemplo para agregar Items genéricos',
          description='Una API CRUD en Flask y Swagger')

# Namespace para organizar los endpoints
ns = api.namespace('items', description='Operaciones CRUD para items ingresados por esta API')

# Modelo para la documentación Swagger
item_model = api.model('Item', {
    'id': fields.Integer(readOnly=True, description='Identificador único'),
    'name': fields.String(required=True, description='Nombre del ítem'),
    'description': fields.String(description='Descripción del ítem')
})

# Base de datos en memoria (para ejemplo)
items_db = []
current_id = 1

@ns.route('/')
class ItemList(Resource):

    @ns.doc('list_items')
    @ns.marshal_list_with(item_model)
    def get(self):
        """Lista todos los ítems agregados previamente"""
        return items_db

    @ns.doc('create_item',
            responses={
                201: 'Ítem creado exitosamente',
                400: 'Datos inválidos',
                409: 'ID ya existe'
            },
            params={
                'force_auto_id': {
                    'description': 'Forzar ID autoincremental (ignora ID en payload)',
                    'in': 'query',
                    'type': 'boolean',
                    'default': False
                }
            })
    @ns.expect(item_model)
    @ns.marshal_with(item_model, code=201)
    def post(self):
        """
        Crea un nuevo ítem.
        
        Por defecto usa ID autoincremental, pero puedes especificar un ID manualmente.
        Si el ID ya existe, devuelve error 409.
        
        Ejemplo Body (ID manual):
        {
            "id": 123,
            "name": "Ejemplo",
            "description": "Descripción opcional"
        }
        
        Ejemplo Body (ID autoincremental):
        {
            "name": "Ejemplo",
            "description": "Descripción opcional"
        }
        """
        global current_id
        data = api.payload
        
        # Verificar si se fuerza ID autoincremental vía query param
        force_auto = request.args.get('force_auto_id', 'false').lower() == 'true'
        
        # Determinar el ID a usar
        if force_auto or 'id' not in data:
            item_id = current_id
            current_id += 1
        else:
            item_id = data['id']
            # Verificar si el ID ya existe
            if any(item['id'] == item_id for item in items_db):
                api.abort(409, f"El ID {item_id} ya existe")
        
        # Crear el ítem
        item = {
            'id': item_id,
            'name': data['name'],
            'description': data.get('description', "")
        }
        
        items_db.append(item)
        return item, 201

@ns.route('/<int:id>')
@ns.response(404, 'Ítem no encontrado')
@ns.param('id', 'Identificador del ítem')
class Item(Resource):
    @ns.doc('get_item')
    @ns.marshal_with(item_model)
    def get(self, id):
        """Obtiene un ítem específico por ID"""
        item = next((item for item in items_db if item['id'] == id), None)
        if not item:
            api.abort(404, f"Ítem con id {id} no encontrado")
        return item
    
    @ns.doc('update_item')
    @ns.expect(item_model)
    @ns.marshal_with(item_model)
    def put(self, id):
        """Actualiza un ítem dado un id"""
        data = request.json
        for item in items_db:
            if item['id'] == id:
                item['name'] = data['name']
                item['description'] = data.get('description', item['description'])
                return item
        api.abort(404, f"Ítem con id {id} no encontrado")

    @ns.doc('delete_item',
            responses={
                204: 'Ítem eliminado exitosamente',
                400: 'Confirmación requerida',
                404: 'Ítem no encontrado'
            },
            params={
                'confirm': {
                'description': 'Debe ser "true" para confirmar eliminación',
                'in': 'query',
                'type': 'boolean',
                'required': True,
                'example': True
                }
            })
    @ns.response(204, 'Ítem eliminado')
    def delete(self, id):
        """Elimina un ítem específico.
        Requiere confirmación explícita:
        - ?confirm=true
        Ejemplo:
        DELETE /Items/1?confirm=true
        """
        if request.args.get('confirm') != 'true':
            api.abort(400, "Debe confirmar la eliminación con ?confirm=true")
        global items_db
        for i, item in enumerate(items_db):
            if item['id'] == id:
                del items_db[i]
                return '', 204
        api.abort(404, f"Ítem con id {id} no encontrado")

if __name__ == '__main__':
    app.run(debug=True)