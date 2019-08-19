from rest_framework import serializers
from . import models

class userdataser(serializers.ModelSerializer):
    class Meta:
        model = models.user_data
        fields = ('account_type', 'name','age','email','gender','pregnancy','report_count')



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CustomUser
        fields = ('email', 'username', )
