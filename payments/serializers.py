from rest_framework import serializers
from .models import Payment
from django.core.exceptions import ObjectDoesNotExist



class PaymentsSerializer(serializers.ModelSerializer):
    
    # activity  = serializers.serializers.SerializerMethodField()

    class Meta:
        model = Payment
        exclude = (
            'transaction_id',
            'id'
            )
      #   fields = (
            # 'date',
            # 'payment_type',
            # 'card_type',
            # 'last_four_digits'
            # 'activity'
      #   )


  #   def get_activity(self,obj):
        # try:
     #      return obj.order.chronogram.activity.id
        # except ObjectDoesNotExist:
        #       return None






class PaymentsPSEDataSerializer(serializers.Serializer):

    payerEmail = serializers.EmailField()
    name  = serializers.CharField()
    contactPhone  = serializers.CharField()
    bank     = serializers.CharField()
    idType   = serializers.CharField()
    userType = serializers.CharField()
    idNumber = serializers.CharField()
