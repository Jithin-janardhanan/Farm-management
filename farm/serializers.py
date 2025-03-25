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
from accounts.serializers import UserSerializer
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
    valves = ValveSerializer(many=True, read_only=True)

    class Meta:
        model = Motor
        fields = ['id', 'motor_type', 'valve_count', 'valves']

    def validate(self, data):
        motor_type = data.get('motor_type')
        valve_count = data.get('valve_count')

        max_valves = {
            'single_phase': 4,
            'double_phase': 6,
            'triple_phase': 10
        }

        if valve_count > max_valves[motor_type]:
            raise serializers.ValidationError(
                f"{motor_type} cannot have more than {max_valves[motor_type]} valves"
            )
        return data

class FarmSerializer(serializers.ModelSerializer):
    motors = MotorSerializer(many=True)
    owner = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Farm
        fields = ['id', 'name', 'location', 'owner', 'motors']

    def create(self, validated_data):
        motors_data = validated_data.pop('motors', [])
        farm = Farm.objects.create(**validated_data)

        for motor_data in motors_data:
            Motor.objects.create(farm=farm, **motor_data)
            # Valves are created automatically via Motor.save()

        farm.refresh_from_db()
        return farm

    def update(self, instance, validated_data):
        # Update farm fields
        instance.name = validated_data.get('name', instance.name)
        instance.location = validated_data.get('location', instance.location)
        instance.owner = validated_data.get('owner', instance.owner)
        instance.save()

        # Handle motors
        motors_data = validated_data.get('motors', [])
        existing_motors = {motor.id: motor for motor in instance.motors.all()}

        # Update or create motors
        for motor_data in motors_data:
            motor_id = motor_data.get('id')
            if motor_id and motor_id in existing_motors:
                # Update existing motor
                motor = existing_motors[motor_id]
                motor.motor_type = motor_data.get('motor_type', motor.motor_type)
                motor.valve_count = motor_data.get('valve_count', motor.valve_count)
                motor.save()
                del existing_motors[motor_id]
            else:
                # Create new motor
                Motor.objects.create(farm=instance, **motor_data)

        # Delete motors not included in the update
        for motor in existing_motors.values():
            motor.delete()

        instance.refresh_from_db()
        return instance