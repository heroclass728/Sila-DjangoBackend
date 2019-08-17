from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from users.models import CustomUser as User

class GetUserDetails(APIView):
    """
    View to list all users in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    authentication_classes = [authentication.TokenAuthentication]
#    permission_classes = [permissions.IsAdminUser]

    def get(self, request, format=None):
        """
        Return a list of all users.
        """
#        usernames = [user.username for user in User.objects.all()]
        user = request.user
        return Response({ 'username': user.username,'email': user.email })
