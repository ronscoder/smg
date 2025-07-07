import pandas as pd
from consumers.models import Consumer, Raid
from datetime import date
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
        c = Consumer()
        c.name = row['CONSUMER NAME']
        c.consumer_id = row['CONSUMER ID']
        c.address = row['ADDRESS']
        c.contact_nos = row['MOBILE'] if pd.notna(row['MOBILE']) else ""
        c.connection_id = row['Prepaid Conn no']       
        c.phase = row['PHASE']
        c.meter_no = row['METER NO']
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
        c.current_outstanding = row['AMOUNT PAYABLE']
        c.bill_upto = row['BILL END']
        try: 
          c.save()
        except:
          print('error', c.consumer_id)
