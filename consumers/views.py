from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.core import serializers
from .models import Consumer, RaidGroup, RaidGrouping, Raid, ConsumerGroup, ConsumerGrouping, MultiConsumer, RaidCashFlow, DefectiveMeter
from django.http import FileResponse
import pandas as pd
from django_pandas.io import read_frame
from .forms import upload_defectives_form

def add_defective(r):
  meter_no = r['meter_no']
  dms = DefectiveMeter.objects.filter(meter_no=meter_no)
  if(dms):
    return f"{meter_no} already added"
  else:
    c = Consumer.objects.filter(meter_no=meter_no).first()
    if(not c):
      return f'{meter_no} unmigrated'
  
    try: 
      dm = DefectiveMeter()
      dm.meter_no = meter_no
      dm.consumer = c
      dm.record_date = r['record_date']
      dm.picked_date = r['picked_date']
      #dm.picked_by = r['picked_by']
      dm.reason = r['reason']
      #dm.reason = r['reason']
      #dm.custody = Staff.objects.get(name='Ronjan')
      #dm.custodyx = r['']
      dm.new_meter_no = r['new_meter_no']
      dm.remark = f"{r['status']} - {r['picked_by']}, {r['custody']}"
      dm.save()
      return f'{meter_no} added'
    except Exception as ex:
      return f'{meter_no} failed'
    
def uploaded(request):
  return render(request, 'consumers/uploaded.html')
def uploads(request):
  if(request.method == 'POST'):
    form = upload_defectives_form(request.POST, request.FILES)
    if(form.is_valid()):
      print('form is valid')
      print(form)
      file = request.FILES['file']
      if not file.name.endswith('.xlsx'):
        return render(request, 'consumers/uploads.html', {'form': form, 'error': 'Please upload a xlxs file.'})
      df = pd.read_excel(file)
      #print(df.head())
      ress = []
      for i, r in df.iterrows():
        res = add_defective(r)
        ress.append(res)
      #return redirect('uploaded')
      return render(request, 'consumers/uploaded.html', {'res': ress})
    else:
      return render(request, 'consumers/uploads.html', {'form': form})
  else:
    form = upload_defectives_form()
  return render(request, 'consumers/uploads.html', {'form': form})
  
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
  rgg = RaidGrouping.objects.filter(group=rg)
  rs = [x.raid for x in rgg]
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
  #df.to_excel("unrecharged_reps.xlsx")
  pv = pd.pivot_table(df, values='meter_no', index='actions', aggfunc='count', margins=True, margins_name='Total nos.')
  #pv.to_excel("unrecharged_summary.xlsx")
  
  reptxt1 = pv.to_html(table_id="pv_unrechargeds", classes=[""])
  reptxt2 = df.to_html(table_id="rep_unrechargeds")
  data = reptxt1 + '<br>' + reptxt2
  return render(request, "consumers/reports.html", {"content": data})
  
def raidgroups(request):
  rgg = RaidGroup.objects.all()
  context = {'raidgroups': rgg}
  return render(request, 'consumers/raidgroups.html', context)

def download_raidgroup(request, rgid):
  rg = RaidGroup.objects.get(pk=rgid)
  rgg = RaidGrouping.objects.filter(group=rg, raid__skip=False)
  rs = [x.raid for x in rgg]
  reps = [{
  'name': x.consumer.name,
  'address': x.consumer.address,
  'contact_no': x.consumer.contact_nos,
  'consumer_id': x.consumer.consumer_id,
  'meter_no': x.consumer.meter_no,
  'observation': ", ".join([o.text for o in x.observations.all()]),
  'theft': 'YES' if any([x.theft for x in x.observations.all()]) else 'NO',
  'is_disconnected': 'YES' if x.is_disconnected else 'NO',
  'penalised': 'YES' if x.penalty_paid else 'NO',
  'theft_period_days': sum([y.day_counts() for y in x.energy_assessments.all()]),
  'unit_assessed': sum([y.total_units() for y in x.energy_assessments.all()]),
  'energy_charge': sum([y.energy_charge() for y in x.energy_assessments.all()]),
  'penalised_energy_charge': sum([y.penalised_energy_charge() for y in x.energy_assessments.all()]),
  'penalty_amount': sum([y.cash_flow.amount for y in RaidCashFlow.objects.filter(raid=x) if y.cash_flow.revenue]),
  'CR#': ",".join([y.cash_flow.txn_ref for y in RaidCashFlow.objects.filter(raid=x) if y.cash_flow.revenue]),
  'comment': x.comment,
  'actions': x.action,
  'remark': f'{x.info} | {x.remark or ""}'} for x in list(rs)]
  df = pd.DataFrame(reps)
  #fname = f'{rg.name}.xlsx'
  response = HttpResponse(content_type='text/csv')
  response['Content-Disposition'] = f'attachment; filename="{rg.name}.csv"'
  df.to_csv(response, index=False)
  return response
  
def raidgroupings(request, rgid):
  rg = RaidGroup.objects.get(pk=rgid)
  rgg = RaidGrouping.objects.filter(group=rg, raid__skip=False)
  rs = [x.raid for x in rgg]
  context = {'rg': rg, 'rs': rs}
  return render(request, 'consumers/raidgroupings.html', context)

def raid(request, rid):
  r = Raid.objects.get(pk=rid)
  return render(request, 'consumers/raid.html', {'raid':r.__dict__})
  
def consumergroups(request):
  cgs = ConsumerGroup.objects.all()
  return render(request, 'consumers/consumergroups.html', {'groups': cgs})
  
def consumergroup(request, cgid):
  cg = ConsumerGroup.objects.get(pk=cgid)
  #cs = cg.consumer.all()
  cggs = ConsumerGrouping.objects.filter(group=cg)
  cs = [cgg.consumer for cgg in cggs]
  return render(request, 'consumers/consumergroup.html', {'consumers': cs, 'group':f'{cg.group_code} | {cg.group_name}'})
  
def download_consumergroup(request, cgid):
  cg = ConsumerGroup.objects.get(pk=cgid)
  #cs = cg.consumer.all()
  cggs = ConsumerGrouping.objects.filter(group=cg)
  cs = [cgg.consumer for cgg in cggs]
  reps = [{
  'consumer_id': x.consumer_id,
  'name': x.name,
  'address': x.address,
  'contact_no': x.contact_nos,
  'meter_no': x.meter_no,
  'load_kw': x.load_kw,
  } for x in list(cs)]
  df = pd.DataFrame(reps)
  df['group'] = cg.group_name
  response = HttpResponse(content_type='text/csv')
  response['Content-Disposition'] = f'attachment; filename="{cg.group_name}_{cg.group_code}.csv"'
  df.to_csv(response, index=False)
  return response
 
def get_duplicacy_report():
  ds = MultiConsumer.objects.filter(duplication=True)
  return ds
def duplicacy_report(request):
  ds = get_duplicacy_report()
  return render(request, 'consumers/duplicacy_report.html', {'data': ds})
  
def download_duplicates(request):
  mcs = MultiConsumer.objects.filter(duplication=True)
  cs = [(x.consumer_b, x.consumer) if x.dup_is_b else (x.consumer, x.consumer_b) for x in mcs]
  reps =[{
    'duplicate_consumer_id': x.consumer_id,
    'name': x.name,
    'address': x.address,
    'meter_no': x.meter_no,
    'connid':x.connection_id,
    'ref_consumer_id':y.consumer_id,
    'ref_name':y.name,
    'ref_address':y.address,
    'ref_meter_no':y.meter_no,
    'ref_connid':y.connection_id
  } for (x,y) in cs]
  df = pd.DataFrame(reps)
  response = HttpResponse(content_type='text/csv')
  response['Content-Disposition'] = f'attachment; filename="duplicates.csv"'
  df.to_csv(response, index=False)
  return response

#from consumers.models import ConsumerWork, Work2
def fix_db_changes(request):
  # this is a changing code... dont use again
  return HttpResponse("Done")