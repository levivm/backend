from rest_framework.authtoken.models import Token
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from authentication.serializers import AuthTokenSerializer
from users.views import get_user_profile_data


class LoginView(GenericAPIView):
    """
    Class to login users
    """
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})

        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        profile_data = get_user_profile_data(user=user)
        token = Token.objects.get(user=user)
        data = {'token': token.key, 'user': profile_data}

        return Response(data)
