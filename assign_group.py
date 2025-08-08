import pandas as pd
from consumers.models import ConsumerGroup, ConsumerGrouping, Consumer, ConsumerNA
def start():
  fname = input('fname: ')
  file = f'ignores/{fname}'
  df = pd.read_csv(file)
  for i,r in df.iterrows():
    gname = r['Group']
    g, created = ConsumerGroup.objects.get_or_create(group_name=gname)
    if(created):
      print('created', g)
    print('checking', r['consumerid'])
    try:
      c = Consumer.objects.get(consumer_id=r['consumerid'])
      print('adding', g, c)
      cg = ConsumerGrouping()
      cg.group = g
      cg.consumer = c
      cg.save()
    except Consumer.DoesNotExist:
      print('creating ConsumerNA')
      cx = ConsumerNA()
      cx.consumer_id = r['consumerid']
      cx.name = r['consumername']
      cx.address = r['consumername']
      cx.contacts = r['mobile']
      cx.info = " | ".join([str(r['prepaidkno']), r['meterno'], r['Report Text']])
      cx.save()
      cx.tags.add(r['Group'])