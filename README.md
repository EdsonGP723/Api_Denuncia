# Api_Denuncia

# ============================================

# INSTRUCCIONES DE INSTALACIÓN Y USO

# ============================================

## 1. INSTALACIÓN:

### Crear entorno virtual

python -m venv venv

**Linux/Mac** source venv/bin/activate

**Windows** venv\Scripts\activate

**Recomendación Personal** Usar Pipenv para crear entorno virtual

pipenv install django

### Instalar dependencias

pip install -r requirements.txt

## 2. CONFIGURACIÓN:

### Crear archivo .env con:

SECRET_KEY=tu-secret-key-muy-segura

DEBUG=True

GROQ_API_KEY=tu-api-key-de-groq-aqui

## 3. MIGRACIONES:

python manage.py makemigrations

python manage.py migrate

**Opcional** python manage.py createsuperuser

## 4. EJECUTAR:

python manage.py runserver

## 5. ENDPOINTS DISPONIBLES:

A) REGISTRO:

POST http://localhost:8000/api/auth/registro/

Body: {

"username": "usuario1",

"email": "usuario1@example.com",

"password": "password123",

"password_confirm": "password123",

"first_name": "Juan",

"last_name": "Pérez"

}

B) LOGIN:

POST http://localhost:8000/api/auth/login/

Body: {

"username": "usuario1",

"password": "password123"

}

C) GENERAR DENUNCIA (REQUIERE TOKEN):

POST http://localhost:8000/api/denuncias/generar/

Headers: {

"Authorization": "Bearer <access_token>"

}

Body: {

"nombre_victima": "Carlos López",

"clasificacion": "fraud"

}

D) LISTAR DENUNCIAS (REQUIERE TOKEN):

GET http://localhost:8000/api/denuncias/

Headers: {

"Authorization": "Bearer <access_token>"

}

## 6. CLASIFICACIONES DISPONIBLES:

- fraud: Fraude
- harassment: Acoso
- discrimination: Discriminación
- corruption: Corrupción
- safety: Seguridad
- other: Otro

## 7. EJEMPLO DE RESPUESTA:

{

"success": true,

"message": "Denuncia generada exitosamente",

"denuncia_id": 1,

"data": {

"date": "2026-01-08 15:30:00",

"anonymous": true,

"channel": "web",

"reporter": {

"relationship_to_company": "employee",

"country": "México"

},

"people": {

"offender": {

"name": "Carlos López",

"position": "Gerente",

"department": "Compras"

}

},

"incident": {

"type": "fraud",

"description": "...",

"approximate_date": "2025-12",

"is_ongoing": true

},

"location": {

"city": "Ciudad de México",

"work_related": true

},

"evidence": {

"has_evidence": true,

"description": "..."

}

}

}

## Documentación API

Una vez instalado y configurado, puede acceder a la siguiente dirección

http://localhost:8000/docs/

o

http://localhost:8000/redoc/

Para una mejor documentación de la API hecha con Swagger
