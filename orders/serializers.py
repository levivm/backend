from rest_framework import serializers
from orders.models import Order, Assistant


class AssistantSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Assistant
        fields = (
            'order',
            'first_name',
            'last_name',
            'email',
        )

class OrdersSerializer(serializers.ModelSerializer):
    assistants = AssistantSerializer(many=True)

    class Meta:
        model = Order
        fields = (
            'chronogram',
            'student',
            'amount',
            'quantity',
            'assistants',
            'enroll',
        )

    def create(self, validated_data):
        assistants_data = validated_data.pop('assistants')
        order = Order.objects.create(**validated_data)
        assistant_objects = [Assistant(order=order, **assistant) for assistant in assistants_data]
        Assistant.objects.bulk_create(assistant_objects)
        return order
