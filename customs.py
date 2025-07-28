import pandas as pd
from consumers.models import Consumer, Raid, ConsumerGroup, RaidGroup
from datetime import date
from django.utils import timezone

def check():
  file = input('filename ')
  df = pd.read_excel(file, sheet_name='non-conflict')
  print(df.head())
  #g = ConsumerGroup.objects.get(pk=2)
  #gcs = g.consumer.all()
  for i, r in df.iterrows():
    try: 
      c = Consumer.objects.get(pk=r['consumerid'])
    except Consumer.DoesNotExist:
      print(r['consumerid'])
def update_unrechargeds():
  file = input('filename ')
  df = pd.read_excel(file, sheet_name='non-conflict')
  df = df.fillna('')
  print(df.head())
  #g = ConsumerGroup.objects.get(pk=2)
  #gcs = g.consumer.all()
  rg = RaidGroup.objects.get(pk=1)
  raids = rg.raids.all()
  for i, r in df.iterrows():
    c = Consumer.objects.get(consumer_id=r['consumerid'])
    raid = next(x for x in raids if x.consumer == c)
    print(raid)
    raid.info = " - ".join([str(x) for x in [r['region'], r['Remark'], r['Report Text'], r['Action text']]])
    raid.observation = r['observation']
    raid.action = r['actions']
    raid.save()
    
    

def raid_report():
  
  d = date(int(input('yyyy')), int(input('mm')), int(input('dd')))
  reps = Raid.objects.filter(date=d)
  if(len(reps)>0):
    df = pd.DataFrame(list(reps.values()))
    df.to_excel(f'raid_{d.month}{d.day}.xlsx')
  else:
    print('no raid data')
  
  
def add_consumers():
    file = input("filename")
    df = pd.read_excel(file)

    for i,row in df.iterrows():
        print(i)
        qs = Consumer.objects.filter(consumer_id=row['CONSUMER ID'])
        if(qs.exists()):
          continue
        c = Consumer()
        c.name = row['CONSUMER NAME']
        c.consumer_id = row['CONSUMER ID']
        c.address = row['ADDRESS']
        c.contact_nos = row['MOBILE'] if pd.notna(row['MOBILE']) else ""
        c.connection_id = row['Prepaid Conn no']       
        c.phase = row['PHASE']
        c.meter_no = row['METER NO']
        c.current_outstanding = row['AMOUNT PAYABLE']
        c.connection_type = row['CONNECTION TYPE']
        c.bill_upto = row['BILL END']
        c.connection_status = row['CONSUMER STATUS']
        c.save()

def update_fields():
   # file = input('filename ')
    df = pd.read_excel('cdata.xls')
    for i,row in df.iterrows():
       # print(i)
        c = Consumer.objects.get(consumer_id=row['CONSUMER ID'])
        #c.meter_no = row['METER NO']
        #c.connection_id = row['Prepaid Conn no']
        #c.contact_nos = row['MOBILE'] if pd.notna(row['MOBILE']) else ""
        c.connection_type = row['CONNECTION TYPE']
        #c.bill_upto = row['BILL END']
        try: 
          c.save()
        except:
          print('error', c.consumer_id)
