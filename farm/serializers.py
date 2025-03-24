# # serializers.py
# from rest_framework import serializers
# from rest_framework.serializers import ModelSerializer
#
# from accounts.models import User
# from motors.models import Motor
# from .models import Farm
#
#
# class FarmSerializer(serializers.ModelSerializer):
#     owner_email = serializers.EmailField(write_only=True, required=False)
#     owner_details = serializers.SerializerMethodField()
#
#     motors = serializers.PrimaryKeyRelatedField(
#         queryset=Motor.objects.all(),
#         required=False,
#     )
#     motors_details =ModelSerializer(source='motors',many=True,read_only=True)
#
#     class Meta:
#         model = Farm
#         fields = ['id', 'name', 'location', 'size', 'description', 'created_at', 'updated_at',
#                   'owner', 'owner_email', 'owner_details']
#         read_only_fields = ['owner', 'owner_details']
#
#     def get_owner_details(self, obj):
#         return {
#             'id': obj.owner.id,
#             'email': obj.owner.email,
#             'username': obj.owner.username,
#             'role': obj.owner.role
#         }
#
#     def create(self, validated_data):
#         request = self.context.get('request')
#         user = request.user
#
#         # Handle owner_email if provided by admin/manager
#         if 'owner_email' in validated_data and user.role in ['admin', 'manager']:
#             owner_email = validated_data.pop('owner_email')
#             try:
#                 owner = User.objects.get(email=owner_email)
#                 validated_data['owner'] = owner
#             except User.DoesNotExist:
#                 raise serializers.ValidationError({'owner_email': 'User with this email does not exist'})
#         else:
#             validated_data['owner'] = user
#
#         return super().create(validated_data)
#
#         if motors:
#             farm.motors.set(motors)

# serializers.py
# serializers.py
from rest_framework import serializers
from accounts.models import User
from .models import Farm
from motors.models import Motor
from motors.serializers import MotorSerializer

class FarmSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(write_only=True, required=False)
    owner_details = serializers.SerializerMethodField()

    motors = serializers.PrimaryKeyRelatedField(
        queryset=Motor.objects.all(),
        many=True,
        required=False
    )

    motors_details = MotorSerializer(source='motors', many=True, read_only=True)

    class Meta:
        model = Farm
        fields = ['id', 'name', 'location', 'size', 'description', 'created_at', 'updated_at',
                  'owner', 'owner_email', 'owner_details', 'motors', 'motors_details']
        read_only_fields = ['owner', 'owner_details', 'motors_details']

    def get_owner_details(self, obj):
        return {
            'id': obj.owner.id,
            'email': obj.owner.email,
            'username': obj.owner.username,
            'role': obj.owner.role
        }

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user

        motors = validated_data.pop('motors', [])
        owner_email = validated_data.pop('owner_email', None)

        if owner_email and user.role in ['admin', 'manager']:
            try:
                owner = User.objects.get(email=owner_email)
                validated_data['owner'] = owner
            except User.DoesNotExist:
                raise serializers.ValidationError({'owner_email': 'User with this email does not exist'})
        else:
            validated_data['owner'] = user

        farm = Farm.objects.create(**validated_data)
        if motors:
            farm.motors.set(motors)
        return farm

    def update(self, instance, validated_data):
        motors = validated_data.pop('motors', None)
        instance = super().update(instance, validated_data)
        if motors is not None:
            instance.motors.set(motors)
        return instance