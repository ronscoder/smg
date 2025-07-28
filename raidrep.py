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
  
raid_report()