from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from .models import Consumer
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