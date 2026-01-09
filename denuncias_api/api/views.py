from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import RegistroSerializer, DenunciaInputSerializer, DenunciaSerializer
from .services import AIService
from .models import Denuncia


class RegistroView(generics.CreateAPIView):
    """
    Endpoint para registrar nuevos usuarios en el sistema.

    Crea un nuevo usuario y retorna tokens JWT para autenticación.
    """
    permission_classes = [AllowAny]
    serializer_class = RegistroSerializer

    @swagger_auto_schema(
        operation_summary="Registro de usuario",
        operation_description="""
        Crea un nuevo usuario en el sistema y retorna tokens de acceso JWT.
        
        **Campos requeridos:**
        - username: Nombre de usuario único
        - email: Correo electrónico
        - password: Contraseña (mínimo 8 caracteres)
        - password_confirm: Confirmación de contraseña (debe coincidir)
        - first_name: Nombre(s)
        - last_name: Apellido(s)
        """,
        responses={
            201: openapi.Response(
                description="Usuario creado exitosamente",
                examples={
                    "application/json": {
                        "user": {
                            "id": 1,
                            "username": "usuario123",
                            "email": "usuario@example.com",
                            "first_name": "Juan",
                            "last_name": "Pérez"
                        },
                        "tokens": {
                            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                            "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
                        },
                        "message": "Usuario registrado exitosamente"
                    }
                }
            ),
            400: "Datos inválidos - Las contraseñas no coinciden o faltan campos"
        },
        tags=['Autenticación']
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Usuario registrado exitosamente'
        }, status=status.HTTP_201_CREATED)


@swagger_auto_schema(
    method='post',
    operation_summary="Iniciar sesión",
    operation_description="""
    Autentica un usuario existente y retorna tokens JWT para acceder a endpoints protegidos.
    
    **Campos requeridos:**
    - username: Nombre de usuario
    - password: Contraseña
    """,
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['username', 'password'],
        properties={
            'username': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Nombre de usuario',
                example='usuario123'
            ),
            'password': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Contraseña',
                format='password',
                example='micontraseña123'
            ),
        }
    ),
    responses={
        200: openapi.Response(
            description="Login exitoso",
            examples={
                "application/json": {
                    "user": {
                        "id": 1,
                        "username": "usuario123",
                        "email": "usuario@example.com",
                        "first_name": "Juan",
                        "last_name": "Pérez"
                    },
                    "tokens": {
                        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
                    },
                    "message": "Login exitoso"
                }
            }
        ),
        400: "Credenciales faltantes",
        401: "Credenciales inválidas"
    },
    tags=['Autenticación']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Endpoint para login de usuarios"""
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({
            'error': 'Se requiere username y password'
        }, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)

    if user is None:
        return Response({
            'error': 'Credenciales inválidas'
        }, status=status.HTTP_401_UNAUTHORIZED)

    refresh = RefreshToken.for_user(user)

    return Response({
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        },
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        },
        'message': 'Login exitoso'
    }, status=status.HTTP_200_OK)

# ====== DENUNCIA CON IA ======


@swagger_auto_schema(
    method='post',
    operation_summary="Generar denuncia con IA",
    operation_description="""
    Genera una denuncia automática usando Inteligencia Artificial basada en el nombre del denunciado y la clasificación del incidente.
    
    **Requiere autenticación JWT** - Usa el botón "Authorize" arriba para agregar tu token.
    
    **Campos requeridos:**
    - nombre_victima: Nombre completo de la persona denunciada
    - clasificacion: Tipo de incidente (fraud, harassment, discrimination, corruption, safety, other)
    
    **Valores válidos para clasificacion:**
    - `fraud`: Fraude
    - `harassment`: Acoso
    - `discrimination`: Discriminación
    - `corruption`: Corrupción
    - `safety`: Seguridad
    - `other`: Otro
    """,
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['nombre_victima', 'clasificacion'],
        properties={
            'nombre_victima': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Nombre completo de la persona denunciada',
                example='Carlos López Martínez'
            ),
            'clasificacion': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Tipo de incidente',
                enum=['fraud', 'harassment', 'discrimination',
                      'corruption', 'safety', 'other'],
                example='fraud'
            ),
        }
    ),
    responses={
        201: openapi.Response(
            description="Denuncia generada exitosamente",
            examples={
                "application/json": {
                    "success": True,
                    "message": "Denuncia generada exitosamente",
                    "denuncia_id": 1,
                    "data": {
                        "anonymous": True,
                        "channel": "web",
                        "reporter": {
                            "relationship_to_company": "Empleado actual",
                            "country": "México"
                        },
                        "people": {
                            "offender": {
                                "name": "Carlos López Martínez",
                                "position": "Gerente de Ventas",
                                "department": "Ventas"
                            }
                        },
                        "incident": {
                            "description": "Descripción detallada del incidente...",
                            "approximate_date": "2026-01-01",
                            "is_ongoing": False
                        },
                        "location": {
                            "city": "Ciudad de México",
                            "work_related": True
                        },
                        "evidence": {
                            "has_evidence": False,
                            "description": ""
                        }
                    }
                }
            }
        ),
        400: "Datos inválidos - Verifica que los campos sean correctos",
        401: "No autenticado - Debes estar autenticado con un token JWT válido",
        500: "Error al generar denuncia con IA"
    },
    security=[{'Bearer': []}],
    tags=['Denuncias']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generar_denuncia_view(request):
    """
    Endpoint protegido que genera una denuncia usando IA

    Body:
    {
        "nombre_victima": "Carlos López",
        "clasificacion": "fraud"
    }
    """
    serializer = DenunciaInputSerializer(data=request.data)

    if not serializer.is_valid():
        return Response({
            'error': 'Datos inválidos',
            'detalles': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    nombre_victima = serializer.validated_data['nombre_victima']
    clasificacion = serializer.validated_data['clasificacion']

    try:
        # Generar denuncia con IA
        ai_service = AIService()
        denuncia_data = ai_service.generar_denuncia(
            nombre_victima, clasificacion)

        # Guardar en base de datos
        denuncia = Denuncia.objects.create(
            usuario=request.user,
            anonimo=denuncia_data.get('anonymous', True),
            canal=denuncia_data.get('channel', 'web'),
            relacion_empresa=denuncia_data.get(
                'reporter', {}).get('relationship_to_company', ''),
            pais=denuncia_data.get('reporter', {}).get('country', 'México'),
            nombre_denunciado=denuncia_data.get('people', {}).get(
                'offender', {}).get('name', nombre_victima),
            cargo=denuncia_data.get('people', {}).get(
                'offender', {}).get('position', ''),
            departamento=denuncia_data.get('people', {}).get(
                'offender', {}).get('department', ''),
            tipo_incidente=clasificacion,
            descripcion=denuncia_data.get(
                'incident', {}).get('description', ''),
            fecha_aproximada=denuncia_data.get(
                'incident', {}).get('approximate_date', ''),
            es_continuo=denuncia_data.get(
                'incident', {}).get('is_ongoing', False),
            ciudad=denuncia_data.get('location', {}).get('city', ''),
            relacionado_trabajo=denuncia_data.get(
                'location', {}).get('work_related', True),
            tiene_evidencia=denuncia_data.get(
                'evidence', {}).get('has_evidence', False),
            descripcion_evidencia=denuncia_data.get(
                'evidence', {}).get('description', ''),
            datos_json=denuncia_data
        )

        return Response({
            'success': True,
            'message': 'Denuncia generada exitosamente',
            'denuncia_id': denuncia.id,
            'data': denuncia_data
        }, status=status.HTTP_201_CREATED)

    except ValueError as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({
            'error': f'Error inesperado: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='get',
    operation_summary="Listar denuncias del usuario",
    operation_description="""
    Obtiene todas las denuncias creadas por el usuario autenticado.
    
    **Requiere autenticación JWT** - Usa el botón "Authorize" arriba para agregar tu token.
    
    Retorna un listado con todas las denuncias y el conteo total.
    """,
    responses={
        200: openapi.Response(
            description="Lista de denuncias obtenida exitosamente",
            examples={
                "application/json": {
                    "count": 2,
                    "denuncias": [
                        {
                            "id": 1,
                            "usuario": 1,
                            "fecha_creacion": "2026-01-09T10:00:00Z",
                            "anonimo": True,
                            "canal": "web",
                            "tipo_incidente": "fraud",
                            "descripcion": "Descripción del incidente generada por IA...",
                            "nombre_denunciado": "Carlos López Martínez",
                            "cargo": "Gerente de Ventas",
                            "departamento": "Ventas"
                        },
                        {
                            "id": 2,
                            "usuario": 1,
                            "fecha_creacion": "2026-01-08T15:30:00Z",
                            "anonimo": True,
                            "canal": "web",
                            "tipo_incidente": "harassment",
                            "descripcion": "Otra descripción...",
                            "nombre_denunciado": "María González",
                            "cargo": "Supervisor",
                            "departamento": "RRHH"
                        }
                    ]
                }
            }
        ),
        401: "No autenticado - Debes estar autenticado con un token JWT válido"
    },
    security=[{'Bearer': []}],
    tags=['Denuncias']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_denuncias_view(request):
    """Listar todas las denuncias del usuario autenticado"""
    denuncias = Denuncia.objects.filter(usuario=request.user)
    serializer = DenunciaSerializer(denuncias, many=True)
    return Response({
        'count': denuncias.count(),
        'denuncias': serializer.data
    }, status=status.HTTP_200_OK)
