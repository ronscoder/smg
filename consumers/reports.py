from .models import Raid, RechargeHistory, ConsumerGroup, Consumer
import datetime
import pandas as pd

def get_last_recharge_bygroup():
  groupid = int(input("group id"))
  cg = ConsumerGroup.objects.get(pk=1)
  cs = cg.consumer.all()
  
  reports = []
  for c in cs:
    r = RechargeHistory.objects.filter(meter_no=c.meter_no).order_by('-paid_on').first()
    report = {
    "consumer_id":c.consumer_id,
    "name": c.name,
    "address": c.address,
    "contact": c.contact_nos,
    "outstanding": c.current_outstanding,
    "bill_upto": c.bill_upto,
    "meter no": c.meter_no,
    "last recharge date": getattr(r, 'paid_on', None),
    "amount": getattr(r,'amount', None)}
    reports.append(report)
  df = pd.DataFrame(reports)
  df.to_excel(f'reports_groupid-{groupid}.xlsx')
def update_recharge():
  fname = input("fname? ")
  file = f'consumers/{fname}.xls'
  df = pd.read_excel(file, skiprows=1)
  print(df.head())
  for i,r in df.iterrows():
    rr = RechargeHistory()
    rr.connection_id = r['CONNECTION ID']
    rr.meter_no = r['METER No.']
    rr.meter_make = r['METER MAKE']
    rr.consumer_name = r['CONSUMER NAME']
    rr.amount = r['AMOUNT']
    td = datetime.timedelta(days=r['PAID ON']-2)
    rr.paid_on = datetime.date(1900, 1, 1) + td
    print(rr.paid_on)
    #break
    rr.pay_mode = r['PAYMENT MODE']
    rr.save()
  
def raids():
  dt = input('ddmmyyyy')
  dd = datetime.date(int(dt[4:]), int(dt[2:4]), int(dt[:2]))
  raids = Raid.objects.filter(date=dd)
  reports = [{
  'name': x.consumer.name,
  'address': x.consumer.address,
  'contact_no': x.consumer.contact_nos,
  'consumer_id': x.consumer.consumer_id,
  'meter_no': x.consumer.meter_no,
  'theft': 'YES' if x.theft else 'NO', 
  'is_disconnected': 'YES' if x.theft else 'NO',
  'penalty': 'YES' if any([y.revenue for y in x.cashflow_set.all()]) else 'NO',
  'penalty_amount': sum([y.amount for y in x.cashflow_set.all() if y.revenue]),
  'CR#': ",".join([y.txn_ref for y in x.cashflow_set.all() if y.revenue])
  } for x in list(raids)]
  df = pd.DataFrame(reports)
  df.to_excel(f'raid_reports-{dt}.xlsx')