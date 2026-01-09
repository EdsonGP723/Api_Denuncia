from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import RegistroSerializer, DenunciaInputSerializer, DenunciaSerializer
from .services import AIService
from .models import Denuncia
# Create your views here.


class RegistroView(generics.CreateAPIView):
    """Endpoint para registrar nuevos usuarios"""
    permission_classes = [AllowAny]
    serializer_class = RegistroSerializer

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
