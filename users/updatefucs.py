from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from users.models import CustomUser as User
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from . import models
from django.http import JsonResponse
class GetUserDetails(APIView):
    """
    View to list all users in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    authentication_classes = [authentication.TokenAuthentication]
#    permission_classes = [permissions.IsAdminUser]
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
#        usernames = [user.username for user in User.objects.all()]
        user = request.user
        ac = models.account_data.objects.get(user=user)
        no_profile = models.user_data.objects.filter(account_id=user).count()
        p_profile = models.user_data.objects.filter(account_id=user,account_type=0).count()
        end_date = None
        reports_allowed = None
        profiles_allowed = None
        pprofile = False
        if p_profile:
            pprofile=True
        if ac.date_check:
            end_date = ac.enddate
        if ac.report_check:
            reports_allowed = ac.reports_allowed
        if ac.subuser_check:
            profiles_allowed = ac.subusers_allowed
        return JsonResponse({ 'username': user.username,'email': user.email ,'account_id':user.id,'subscription_end_date':end_date,'reports_allowed':reports_allowed,'reports_count':ac.report_count,'profiles_allowed':profiles_allowed,'profiles_count':no_profile,'primary_profile':pprofile})
