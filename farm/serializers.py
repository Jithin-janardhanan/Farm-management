# from rest_framework import serializers
# from accounts.serializers import UserSerializer
# from .models import Farm, Motor, Valve
# from accounts.models import User
#
#
# class ValveSerializer(serializers.ModelSerializer):
#     is_active = serializers.IntegerField(default=0)  # Removed source='is_active'
#
#     class Meta:
#         model = Valve
#         fields = ['id', 'name', 'is_active']
#
#     def to_representation(self, instance):
#         ret = super().to_representation(instance)
#         ret['is_active'] = 1 if instance.is_active else 0
#         return ret
#
#     def to_internal_value(self, data):
#         data = super().to_internal_value(data)
#         if 'is_active' in data:
#             data['is_active'] = bool(data['is_active'])
#         return data
#
#
# class MotorSerializer(serializers.ModelSerializer):
#     valves = ValveSerializer(many=True, read_only=True)
#
#     class Meta:
#         model = Motor
#         fields = ['id', 'motor_type', 'valve_count', 'valves']
#
#     def validate(self, data):
#         motor_type = data.get('motor_type')
#         valve_count = data.get('valve_count')
#
#         max_valves = {
#             'single_phase': 4,
#             'double_phase': 6,
#             'triple_phase': 10
#         }
#
#         if valve_count > max_valves[motor_type]:
#             raise serializers.ValidationError(
#                 f"{motor_type} cannot have more than {max_valves[motor_type]} valves"
#             )
#         return data
#
#
# class FarmSerializer(serializers.ModelSerializer):
#     motors = MotorSerializer(many=True)
#     owner = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
#
#     class Meta:
#         model = Farm
#         fields = ['id', 'name', 'location', 'owner', 'motors']
#
#     def create(self, validated_data):
#         motors_data = validated_data.pop('motors', [])
#         farm = Farm.objects.create(**validated_data)
#
#         for motor_data in motors_data:
#             Motor.objects.create(farm=farm, **motor_data)
#             # Valves are created automatically via Motor.save()
#
#         farm.refresh_from_db()
#         return farm

from rest_framework import serializers
from .models import Farm, Motor, Valve
from accounts.models import User

class ValveSerializer(serializers.ModelSerializer):
    is_active = serializers.IntegerField(default=0)

    class Meta:
        model = Valve
        fields = ['id', 'name', 'is_active']
        extra_kwargs = {'name': {'required': False}}

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['is_active'] = 1 if instance.is_active else 0
        return ret

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        if 'is_active' in data:
            data['is_active'] = bool(data['is_active'])
        return data

class MotorSerializer(serializers.ModelSerializer):
    valves = ValveSerializer(many=True, read_only=True)  # Ensure read_only to prevent incorrect writes

    class Meta:
        model = Motor
        fields = ['id', 'motor_type', 'valve_count', 'valves', 'farm']

    def validate(self, data):
        motor_type = data.get('motor_type')
        valve_count = data.get('valve_count')
        
        max_valves = {
            'single_phase': 4,
            'double_phase': 6,
            'triple_phase': 10
        }

        if motor_type and valve_count and valve_count > max_valves.get(motor_type, 0):
            raise serializers.ValidationError(
                f"{motor_type} cannot have more than {max_valves[motor_type]} valves"
            )
        return data

class FarmSerializer(serializers.ModelSerializer):
    motors = MotorSerializer(many=True, read_only=True)
    owner = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Farm
        fields = ['id', 'name', 'location', 'owner', 'motors']