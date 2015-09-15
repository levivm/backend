from rest_framework import serializers
from .models import Payment



class PaymentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        exclude = (
            'transaction_id',
            'id'
            )




class PaymentsPSEDataSerializer(serializers.Serializer):

	payerEmail = serializers.EmailField()
	name  = serializers.CharField()
	contactPhone  = serializers.CharField()
	bank     = serializers.CharField()
	idType   = serializers.CharField()
	userType = serializers.CharField()
	idNumber = serializers.CharField()
