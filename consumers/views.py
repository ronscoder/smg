from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from .models import Consumer, RaidGroup
import pandas as pd
def index(request):
    return render(request, "consumers/index.html")
def test_api(request):
  pass
def consumer_details(request, consumer_id):
    c = Consumer.objects.get(consumer_id=consumer_id)
    #json_data = serializers.serialize("json", [c])
   # print(json_data)
    context = {"consumer_details": c, "location": c.location, "consumer_id": c.consumer_id}
    return render(request,"consumers/consumer_details.html",context  )
    
def unrecharged_reports(request):
  rg = RaidGroup.objects.get(pk=1)
  rs = rg.raids.all()
  reps = [{
  'name': x.consumer.name,
  'address': x.consumer.address,
  'contact_no': x.consumer.contact_nos,
  'consumer_id': x.consumer.consumer_id,
  'meter_no': x.consumer.meter_no,
  'observation': x.observation,
  'actions': x.action,
  'remark': x.info} for x in list(rs)]
  
  df = pd.DataFrame(reps)
  df.to_excel("unrecharged_reps.xlsx")
  pv = pd.pivot_table(df, values='meter_no', index='actions', aggfunc='count')
  pv.to_excel("unrecharged_summary.xlsx")
  
  reptxt1 = pv.to_html(table_id="pv_unrechargeds", classes=[""])
  reptxt2 = df.to_html(table_id="rep_unrechargeds")
  data = reptxt1 + '<br>' + reptxt2
  return render(request, "consumers/reports.html", {"content": data})