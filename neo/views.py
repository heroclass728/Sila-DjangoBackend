
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
from django.core.mail import send_mail
# from collections import Counter

from django.utils.html import strip_tags

from . import models
from . import serializers
from neomodel import db
from api.models import settings as apisettings
from users.models import account_data,reports,user_data
from collections import Counter
import pandas as pd
import json


from users.models import CustomUser as user
from datetime import date
import re
from ApiSettings import *


from e_mails.models import templates as etemplates
from django.template import Context, Template
# class Symptom(generics.ListCreateAPIView):
#     queryset = models.Symptom.nodes.all()
#     serializer_class = serializers.Symptom


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
#


class qa(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def makequery_ar(self,sl):
        q = '''MATCH (u:User {group: $age, gender: $gen, pregnancy: $preg}) WITH u'''
        for i in range(len(sl)):
            q = q + ''' MATCH (:Symptom {ar_name: "'''+ sl[i] +'''"})<-[:has]-(d:Disease) WITH d'''
        q = q + ''' Match (d:Disease)-[:has]->(ps:Symptom) return d.ar_name , ps.ar_name'''
        return q
    def makequery(self,sl):
        q = '''MATCH (u:User {group: $age, gender: $gen, pregnancy: $preg}) WITH u'''
        for i in range(len(sl)):
            q = q + ''' MATCH (:Symptom {name: "'''+ sl[i] +'''"})<-[:has]-(d:Disease) WITH d'''
        q = q + ''' Match (d:Disease)-[:has]->(ps:Symptom) return d.name , ps.name''' #,ps.description
        return q
    def getdescription(self,li,ar=False):
        if ar:
            result, meta = db.cypher_query('match (s:Symptom) where s.ar_name in $symlist return s.ar_name,s.ar_description',{'symlist':li})
        else:
            result, meta = db.cypher_query('match (s:Symptom) where s.name in $symlist return s.name,s.description',{'symlist':li})
        return result
    def getprobs(self,li,skip):
        _ = pd.DataFrame(li,columns=['Disease','Symptom'])
        r = _.groupby('Disease').size().div(len(_)).sort_values(ascending=False)
        disprob = {}
        for i in range(len(list(r[:QA_DISEASE_SEND].index))):
            disprob[r.index[i]] = r[i]
#        Counter(_['Symptom']).most_common(skip+QA_SYMPTOM_SEND)[skip:QA_SYMPTOM_SEND]
        symcounter = Counter(_['Symptom']).most_common(skip+QA_SYMPTOM_SEND)[skip:QA_SYMPTOM_SEND]
        symlist = []
        for i in symcounter:
            symlist.append(i[0])
        return  symcounter,disprob,symlist #Counter(_['Symptom']).most_common(10),disprob

    def post(self, request, format=None):
        data = request.data
        ar = False
        if not all(elm in list(data.keys()) for elm in ['age','gender','pregnancy','symtomps']):
            return JsonResponse({"message":"required parameters are not provided"}, status=400)
        params = {'age':data['age'],'gen':data['gender'],'preg':data['pregnancy']}
        if 'language' in data.keys():
            if data['language']!='ar':
                return JsonResponse({"message":"Undefined Language"}, status=400)
            results, meta = db.cypher_query(self.makequery_ar(data['symtomps']),params)
            ar=True
        else:

            results, meta = db.cypher_query(self.makequery(data['symtomps']),params)
#            return JsonResponse({"message":"Inside the q&a system"}, status=400)
        if 'skip' in  data.keys():
            nextsyms,disprobs,symlist = self.getprobs(results,skip=data['skip'])
        else:
            nextsyms,disprobs,symlist = self.getprobs(results,skip=0)
        res = {'Disease_probabilities':disprobs,'Next_questions':nextsyms,'Descriptions':self.getdescription(symlist,ar)}
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
        r = re.compile(".*"+data['symptom']+".*")
        li = list(filter(r.match, symlist.keys()))
#        li = list(filter(lambda x: data['symptom'] in x, symlist))
        for i in li:
            res.append([i,symlist[i]])
        return JsonResponse({"symptoms":res,"stop_disease_count":QA_STOP_DISEASE_COUNT,"stop_loop_count":QA_STOP_LOOP_COUNT})


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


# #class symsearch(APIView):
# #    def post(self, request, format=None):
# #        data = request.data
# #        if 'symptom' not in data.keys():
# #            return JsonResponse({"message":"required parameters are not provided"}, status=400)
# #        params = {'sym':data['symptom']}
# #        if 'language' in data.keys():
# #            if data['language']!='ar':
# #                return JsonResponse({"message":"Undefined Language"}, status=400)
# #            results, meta = db.cypher_query("match (s:Symptom) where s.ar_name contains $sym return s.ar_name,s.ar_description",params)
# #        else:
# #            results, meta = db.cypher_query("match (s:Symptom) where s.name contains $sym return s.name,s.description",params)
# ##         nextsyms,disprobs = self.getprobs(results)
# #        res = {'symptoms':results}
# #        return JsonResponse(res)
#
#
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

    newarlist = arlist.copy()
    for k, v in arlist.items():
        if v is None:
            del newarlist[k]
    with open('arlist.pkl', 'wb') as f:
        pickle.dump(newarlist, f, pickle.HIGHEST_PROTOCOL)
    return HttpResponse('Successfully updated symptom search')

class getreportsdata(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    def getdiseasesdata(self,distr):
        li = distr.split(',')
        result, meta = db.cypher_query('match (s:Disease) where s.name in $dislist return s.name,s.description',{'dislist':li})
        if len(result)==0:
            result, meta = db.cypher_query('match (s:Disease) where s.ar_name in $dislist return s.ar_name',{'dislist':li})
        res = pd.DataFrame(result,columns=['name','description'])
        return res.values.tolist()
    def comstring(self,cs):
        if cs<35:
            st = CS_0_35
        if cs>=35 and cs<=60:
            st = CS_36_60
        if cs >60:
            st = CS_61_100
        return st
    permission_classes = [IsAuthenticated]
    def put(self, request, format=None):
        user = request.user
        data = json.loads(request.body)
        if "report_id" in data.keys():
            try:
                i = reports.objects.get(id = data['report_id'])
            except:
                return JsonResponse({"message":"Invalid report id"}, status=400)
            if i.user!=user:
                return JsonResponse({"message":"Current user cannot access this report"}, status=400)
            return JsonResponse({"report_id":i.id,"profile_id":i.profile.id,"symptoms":i.symptomps,"diseases":i.diseases,"description":self.getdiseasesdata(i.diseases),"dangerscore":i.danger_score,"commonscore":i.common_score,"doctors":i.doctor,"danger_string":self.comstring(i.danger_score),"date":i.date})

        if "profile_id" in data.keys():
            try:
                k = user_data.objects.get(id = data['profile_id'])
            except:
                return JsonResponse({"message":"Invalid profile id"}, status=400)
            if k.account_id != user:
                return JsonResponse({"message":"Current user cannot access this profile"}, status=400)
            profilereports = reports.objects.filter(profile=k)
            rlist = []
            for i in profilereports:
                rlist.append({'report_id':i.id,"profile_id":i.profile.id,"symptoms":i.symptomps,"diseases":i.diseases,"description":self.getdiseasesdata(i.diseases),"dangerscore":i.danger_score,"commonscore":i.common_score,"doctors":i.doctor,"danger_string":self.comstring(i.danger_score),"date":i.date})
            return JsonResponse(rlist, safe=False)

        rdata = reports.objects.filter(user = user)
        plist = []
        for i in rdata:
            plist.append({'report_id':i.id,"profile_id":i.profile.id,"symptoms":i.symptomps,"diseases":i.diseases,"description":self.getdiseasesdata(i.diseases),"dangerscore":i.danger_score,"commonscore":i.common_score,"doctors":i.doctor,"danger_string":self.comstring(i.danger_score),"date":i.date})
        return  JsonResponse(plist, safe=False)


class getreport(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def getdiseasesdataemail(self,distr):
        li = distr.split(',')
        result, meta = db.cypher_query('match (s:Disease) where s.name in $dislist return s.name,s.description,s.commom',{'dislist':li})
        if len(result)==0:
            result, meta = db.cypher_query('match (s:Disease) where s.ar_name in $dislist return s.ar_name,s.commom',{'dislist':li})
        res = pd.DataFrame(result,columns=['name','description','common'])
        return res

    def getdiseasesdata(self,li,ar):
        if ar:
            result, meta = db.cypher_query('match (s:Disease) where s.ar_name in $dislist return s.ar_name,s.ar_description, s.commom, s.urgent',{'dislist':li})
        else:
            result, meta = db.cypher_query('match (s:Disease) where s.name in $dislist return s.name,s.description, s.common, s.urgent',{'dislist':li})
        return result

    def getdoctordata(self,li,ar):
        if ar:
            result, meta = db.cypher_query('match (s:Disease) where s.ar_name in $dislist with s match (s)<-[:covers]-(d:Doctor) return d.ar_name',{'dislist':li})
        else:
            result, meta = db.cypher_query('match (s:Disease) where s.name in $dislist with s match (s)<-[:covers]-(d:Doctor) return d.name',{'dislist':li})
        return result

    def getscore(self,li,index):
        dlist = []
        for i in li:
            dlist.append(int(list(i)[index]))
        return sum(dlist)/len(dlist)

    def comstring(self,cs):
        if cs<35:
            st = CS_0_35
        if cs>=35 and cs<=60:
            st = CS_36_60
        if cs >60:
            st = CS_61_100
        return st
    def comdecode(self,df,index):
        for index,row in df.iterrows():
            row['common'] = int(list(row['common'])[index])
        return df

    def put(self, request):
        user = request.user
        data = json.loads(request.body)
        if not all(elm in list(data.keys()) for elm in ['profile_id','report_id','primary']):
            return JsonResponse({"message":"required details are not provided not provided"}, status=400)
        # ad = account_data.objects.get(user=user)
        try:
            profiledata = user_data.objects.get(id = data['profile_id'])
        except:
            return JsonResponse({"message":"Invalid profile id"}, status=400)
        if profiledata.account_id != user:
            return JsonResponse({"message":"Current user cannot access this profile"}, status=400)
        try:
            reportsdata = reports.objects.get(id = data['report_id'])
        except:
            return JsonResponse({"message":"Invalid report id"}, status=400)
        if data['primary']:
            if 'ar' in data.keys():
                if data['ar']:
                    htmlstr = etemplates.objects.get(name='reports_primary_ar').temp
                else:
                    htmlstr = etemplates.objects.get(name='reports_primary').temp
            else:
                htmlstr = etemplates.objects.get(name='reports_primary').temp
            email = user.email
            # send_mail('Test primary report mail','example mail','accounts@drsila.com',[profiledata.email],fail_silently=False)
        else:
            if profiledata.email==None:
                if 'email' not in data.keys():
                    return JsonResponse({"message":"This profile dose not have a email and it's not provided in data"}, status=400)
                else:
                    profiledata.email = data['email']
                    profiledata.save()
                    if 'ar' in data.keys():
                        if data['ar']:
                            htmlstr = etemplates.objects.get(name='reports_secondary_ar').temp
                        else:
                            htmlstr = etemplates.objects.get(name='reports_secondary').temp
                    else:
                        htmlstr = etemplates.objects.get(name='reports_secondary').temp

            email = profiledata.email

        pdf = self.getdiseasesdataemail(reportsdata.diseases)
        diseases = []
        for disname in reportsdata.diseases.split(','):
            diseases.append({'disease':disname,
                                 'common':pdf[pdf['name']==disname]['common'].values[0],
                                 'description':pdf[pdf['name']==disname]['description'].values[0]
                                })
        htm_template = Template(htmlstr)
        username = user.username
        context = Context({'reportid': reportsdata.id,'reportdate':reportsdata.date,'username':username,'doctor':reportsdata.doctor,'dangerscore':self.comstring(reportsdata.danger_score),'diseases':diseases})
        html_message = htm_template.render(context)
        # etemplates.
        # htmlstr = etemplates.objects.get(name='code_verification').temp
        # html_message = render_to_string(htmlstr, {'code': code,'content':content,'username':username})
        plain_message = strip_tags(html_message)
        send_mail('Dr.Sila Report',plain_message,'reports@drsila.com',[email],html_message=html_message,fail_silently=False)
        return JsonResponse({"message":"Email sent successfully"})

    def post(self, request):
        user = request.user
        data = json.loads(request.body)
        if not all(elm in list(data.keys()) for elm in ['symptomps','profile_id','diseases','age_index']):
            return JsonResponse({"message":"required details are not provided not provided"}, status=400)
        ad = account_data.objects.get(user=user)
        try:
            profiledata = user_data.objects.get(id = data['profile_id'])
        except:
            return JsonResponse({"message":"Invalid profile id"}, status=400)
        if profiledata.account_id != user:
            return JsonResponse({"message":"Current user cannot access this profile"}, status=400)
        if date.today() > ad.enddate:
            return JsonResponse({"message":"Your plan expired, please renew the plan"}, status=400)
        if ad.report_check:
            if ad.reports_allowed:
                ad.reports_allowed = ad.reports_allowed-1
            else:
                return JsonResponse({"message":"Your cannot make more reports, please renew the plan"}, status=400)
        ad.report_count = ad.report_count + 1
        profiledata.report_count = profiledata.report_count + 1
        symptomps = ','.join(data['symptomps'])
        diseases = ','.join(data['diseases'])
        ar = False
        if 'language' in data.keys():
            if data['language']!='ar':
                return JsonResponse({"message":"Undefined Language"}, status=400)
            ar = True
        ndata = self.getdiseasesdata(data['diseases'],ar)
        doctors  = self.getdoctordata(data['diseases'],ar)


        drli = []
        for i in doctors:
            drstr = drli.append(i[0])
        drocc = Counter(drli)
        drstr = drocc.most_common(1)[0][0]

        df = pd.DataFrame(ndata,columns=['name','description','common','urgent'])
        dangerscore = self.getscore(list(df.urgent.unique()),data['age_index'])
        commonscore = self.getscore(list(df.common.unique()),data['age_index'])
        df = self.comdecode(df,data['age_index'])
        # for i in ndata
        report = reports(user=user,profile=profiledata,symptomps=symptomps,diseases=diseases,danger_score=dangerscore*100,common_score=commonscore,doctor=drstr)
        report.save()
        ad.save()
        profiledata.save()
        return JsonResponse({"disease_data":df.drop(['urgent'], axis=1).values.tolist(),"danger_string":self.comstring(dangerscore*100),"danger_scrore":dangerscore*100,"report_id":report.id,"first_name":profiledata.name,"doctors":drstr})
