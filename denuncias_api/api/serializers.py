from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Denuncia


class RegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password',
                  'password_confirm', 'first_name', 'last_name']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Las contraseñas no coinciden")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class DenunciaInputSerializer(serializers.Serializer):
    nombre_victima = serializers.CharField(max_length=255)
    clasificacion = serializers.ChoiceField(choices=Denuncia.TIPOS_INCIDENTE)


class DenunciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Denuncia
        fields = '__all__'
        read_only_fields = ['usuario', 'fecha_creacion']
