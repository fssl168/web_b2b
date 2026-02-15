from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from myapp.auth.authentication import AdminTokenAuthtication


class VerifyTokenView(APIView):
    authentication_classes = [AdminTokenAuthtication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        # 如果能到达这里，说明token已经验证通过
        return Response({
            'success': True,
            'message': 'Token验证通过',
            'user': {
                'id': request.user.id,
                'username': request.user.username
            }
        })
