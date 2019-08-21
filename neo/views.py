from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import authentication, permissions
from django.http import JsonResponse
import pickle



from . import models
from . import serializers
from neomodel import db
from api.models import settings as apisettings

from collections import Counter
import pandas as pd
import json



class Symptom(generics.ListCreateAPIView):
    queryset = models.Symptom.nodes.all()
    serializer_class = serializers.Symptom
 
class getsyms(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated)
    def get(self, request, format=None):
        return HttpResponse(models.Symptom.nodes.all())



class userview(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated)

    def get(self, request, format=None):
        content = {
            'user': str(request.user),  # `django.contrib.auth.User` instance.
            'auth': str(request.auth),  # None
        }
        return Response(content)



class qa(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def makequery_ar(self,sl):
        q = '''MATCH (u:User {group: $age, gender: $gen, pregnancy: $preg}) WITH u'''
        for i in range(len(sl)):
            q = q + ''' MATCH (:Symptom {ar_name: "'''+ sl[i] +'''"})<-[:has]-(d:Disease) WITH d'''
        q = q + ''' Match (d:Disease)-[:has]->(ps:Symptom) return d.ar_name , ps.ar_name,ps.ar_description'''
        return q
    def makequery(self,sl):
        q = '''MATCH (u:User {group: $age, gender: $gen, pregnancy: $preg}) WITH u'''
        for i in range(len(sl)):
            q = q + ''' MATCH (:Symptom {name: "'''+ sl[i] +'''"})<-[:has]-(d:Disease) WITH d'''
        q = q + ''' Match (d:Disease)-[:has]->(ps:Symptom) return d.name , ps.name,ps.description'''
        return q

    def getprobs(self,li):
        _ = pd.DataFrame(li,columns=['Disease','Symptom','Description'])
        r = _.groupby('Disease').size().div(len(_)).sort_values(ascending=False)
        disprob = {}
        for i in range(len(list(r[:5].index))):
            disprob[r.index[i]] = r[i]
        return Counter(_['Symptom']).most_common(10),disprob

    def post(self, request, format=None):
        data = request.data
        if not all(elm in list(data.keys()) for elm in ['age','gender','pregnancy','symtomps']):
            return JsonResponse({"message":"required parameters are not provided"}, status=400)
        params = {'age':data['age'],'gen':data['gender'],'preg':data['pregnancy']}
        if 'language' in data.keys():
            if data['language']!='ar':
                return JsonResponse({"message":"Undefined Language"}, status=400)
            results, meta = db.cypher_query(self.makequery_ar(data['symtomps']),params)
        else:
            results, meta = db.cypher_query(self.makequery(data['symtomps']),params)
        nextsyms,disprobs = self.getprobs(results)
        res = {'Disease_probabilities':disprobs,'Next_questions':nextsyms}
        return JsonResponse(res)

#         return HttpResponse(list(data.keys()))
#         return HttpResponse(models.Symptom.nodes.all())
#         age = request.POST.get('age')
#         gen = request.POST.get('gender')
#         preg = request.POST.get('pregnancy')
#         syms = request.POST.getlist('symtomps[]')


class symsearch1(APIView):

    def post(self, request, format=None):
        data = request.data
        if 'symptom' not in data.keys():
            return JsonResponse({"message":"required parameters are not provided"}, status=400)
        res = []
        if 'language' in data.keys():
            if data['language']!='ar':
                return JsonResponse({"message":"Undefined Language"}, status=400)
            with open('arlist.pkl', 'rb') as f:
                symlist = pickle.load(f)
        else:
            with open('enlist.pkl', 'rb') as f:
                symlist = pickle.load(f)
        li = list(filter(lambda x: data['symptom'] in x, symlist))
        for i in li:
            res.append([i,symlist[i]])
        return JsonResponse({"symptoms":res})


class getsymptom(APIView):
    def post(self, request, format=None):
        data = request.data
        if 'symptom' not in data.keys():
            return JsonResponse({"message":"required parameters are not provided"}, status=400)
        params = {'sym':data['symptom']}
        if 'language' in data.keys():
            if data['language']!='ar':
                return JsonResponse({"message":"Undefined Language"}, status=400)
            results, meta = db.cypher_query("match (s:Symptom) where s.ar_name=$sym return s.ar_name,s.ar_description",params)
        else:
            results, meta = db.cypher_query("match (s:Symptom) where s.name=$sym return s.name,s.description",params)
        return JsonResponse({"symptoms":results})


class symsearch(APIView):

    def post(self, request, format=None):
        data = request.data
        if 'symptom' not in data.keys():
            return JsonResponse({"message":"required parameters are not provided"}, status=400)
        params = {'sym':data['symptom']}
        if 'language' in data.keys():
            if data['language']!='ar':
                return JsonResponse({"message":"Undefined Language"}, status=400)
            results, meta = db.cypher_query("match (s:Symptom) where s.ar_name contains $sym return s.ar_name,s.ar_description",params)
        else:
            results, meta = db.cypher_query("match (s:Symptom) where s.name contains $sym return s.name,s.description",params)
#         nextsyms,disprobs = self.getprobs(results)
        res = {'symptoms':results}

        return JsonResponse(res)


def makesymsearch(request):
    results, meta = db.cypher_query("match (s:Symptom) return s.name,s.ar_name,s.synonyms,s.ar_synonyms")
    _ = pd.DataFrame(results,columns=['name','ar_name','synonyms','ar_synonyms'])
    arlist ={}
    enlist = {}
    for index, row in _.iterrows():
        if row['synonyms']:
            for i in row['synonyms']:
                enlist[i] = row['name']
            enlist[row['name']] = row['name']
        else:
            enlist[row['name']] = row['name']
        if row['ar_synonyms']:
            for i in row['ar_synonyms']:
                arlist[i] = row['ar_name']
                arlist[row['ar_name']] = row['ar_name']
        else:
            arlist[row['ar_name']] = row['ar_name']
    with open('enlist.pkl', 'wb') as f:
        pickle.dump(enlist, f, pickle.HIGHEST_PROTOCOL)
    with open('arlist.pkl', 'wb') as f:
        pickle.dump(arlist, f, pickle.HIGHEST_PROTOCOL)
    return HttpResponse('Successfully updated symptom serach')



