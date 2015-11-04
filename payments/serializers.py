from rest_framework import serializers

from .models import Payment


class PaymentsSerializer(serializers.ModelSerializer):
    # activity  = serializers.serializers.SerializerMethodField()
    payment_type = serializers.SerializerMethodField()
    card_type = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        # exclude = (
        #     'transaction_id',
        #     'id'
        # )
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



        #   def get_activity(self,obj):
        # try:
        #      return obj.order.calendar.activity.id
        # except ObjectDoesNotExist:
        #       return None


class PaymentsPSEDataSerializer(serializers.Serializer):
    payerEmail = serializers.EmailField()
    name = serializers.CharField()
    contactPhone = serializers.CharField()
    bank = serializers.CharField()
    idType = serializers.CharField()
    userType = serializers.CharField()
    idNumber = serializers.CharField()
