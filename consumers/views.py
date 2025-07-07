from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from .models import Consumer
def index(request):
    return render(request, "consumers/index.html")

def consumer_details(request, consumer_id):
    c = Consumer.objects.get(consumer_id=consumer_id)
    #json_data = serializers.serialize("json", [c])
   # print(json_data)
    context = {"consumer_details": c, "location": c.location, "consumer_id": c.consumer_id}
    return render(request,"consumers/consumer_details.html",context  )

# In your Django views.py
#from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
#from .models import YourModel # Import your model

@csrf_exempt # Use this if you are handling PUT/POST without a form, otherwise ensure CSRF token is handled
def update_location(request, consumer_id):
    print("updating location")
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            new_value = data.get('value')
            
            item = Consumer.objects.get(pk=consumer_id)
            print("old location", item.location, new_value)
            item.location = new_value
            item.save()
            return JsonResponse({'success': True, 'message': 'Location updated successfully.'})
        except Consumer.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Item not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)