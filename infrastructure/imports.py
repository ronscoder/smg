from .models import DTR, Feeder
import pandas as pd

def importdtrs():
  df = pd.read_csv('infrastructure/dtrs.csv')
  print(df.head())
  for i, r in df.iterrows():
    d = DTR()
    d.dtr_id = r['DTR ID']
    d.feeder = Feeder.objects.get(feeder_id=r['FEEDER ID'])
    d.name = r['DTR NAME']
    d.capacity_kva = '100'
    d.save()