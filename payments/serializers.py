from rest_framework import serializers

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    payment_type = serializers.SerializerMethodField()
    card_type = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = (
            'date',
            'payment_type',
            'card_type',
            'last_four_digits',
        )

    def get_payment_type(self,obj):
        return obj.get_payment_type_display()

    def get_card_type(self,obj):
        return obj.get_card_type_display()


class PaymentsPSEDataSerializer(serializers.Serializer):
    payerEmail = serializers.EmailField()
    name = serializers.CharField()
    contactPhone = serializers.CharField()
    bank = serializers.CharField()
    userType = serializers.CharField()
    idNumber = serializers.CharField()
