from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated

from . import models
from . import serializers
from neomodel import db


from collections import Counter
import pandas as pd
import json



class Symptom(generics.ListCreateAPIView):
    queryset = models.Symptom.nodes.all()
    serializer_class = serializers.Symptom
    
    
    
class getsyms(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get(self, request, format=None):
        
        return HttpResponse(models.Symptom.nodes.all())
    
    
class userview(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        content = {
            'user': str(request.user),  # `django.contrib.auth.User` instance.
            'auth': str(request.auth),  # None
        }
        return Response(content)
    
    
class qa(APIView):
    
#     authentication_classes = (SessionAuthentication, BasicAuthentication)
#     permission_classes = (IsAuthenticated,)


    def makequery(self,sl):
        q = '''MATCH (u:User {group: $age, gender: $gen, pregnancy: $preg}) WITH u'''
        for i in range(len(sl)):
            q = q + ''' MATCH (:Symptom {name: "'''+ sl[i] +'''"})<-[:has]-(d:Disease) WITH d'''
        q = q + ''' Match (d:Disease)-[:has]->(ps:Symptom) return d.name , ps.name,ps.description'''
        return q

    def getprobs(self,li):
        _ = pd.DataFrame(li,columns=['Disease','Symptom','Deacription'])
        r = _.groupby('Disease').size().div(len(_)).sort_values(ascending=False)
        disprob = {}
        for i in range(len(list(r.index))):
            disprob[r.index[i]] = r[i]
        return Counter(_['Symptom']).most_common(10),disprob

    def post(self, request, format=None):
        data = request.data
        
        if list(data.keys())!=['age','gender','pregnancy','symtomps']:
            return HttpResponse('required parameters are not provided')
        
        
        params = {'age':data['age'],'gen':data['gender'],'preg':data['pregnancy']}
        results, meta = db.cypher_query(self.makequery(data['symtomps']),params)
#         people = [Person.inflate(row[0]) for row in results]
        nextsyms,disprobs = self.getprobs(results)
        res = {'Disease_probabilities':disprobs,'Next_questions':nextsyms}
        print(res)
        return HttpResponse(json.dumps(res))
#         return HttpResponse(list(data.keys()))
        

        
#         return HttpResponse(models.Symptom.nodes.all())
#         age = request.POST.get('age')
#         gen = request.POST.get('gender')
#         preg = request.POST.get('pregnancy')
#         syms = request.POST.getlist('symtomps[]')



class symsearch(APIView):
    
    def post(self, request, format=None):
        data = request.data
        
        if list(data.keys())!=['symptom']:
            return HttpResponse('required parameters are not provided')
        
        
        params = {'sym':data['symptom']}
        results, meta = db.cypher_query("match (s:Symptom) where s.name contains $sym return s.name,s.description",params)
#         nextsyms,disprobs = self.getprobs(results)
        res = {'symptoms':results}
        print(res)
        return HttpResponse(json.dumps(res))
