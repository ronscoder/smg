from consumers.models import MultiConsumer

def start():
  cggs = MultiConsumer.objects.all()
  for cg in cggs:
    cs = cg.consumers.all()
    for c in cs:
      ncg = MultiConsumer()
      #ncg.group = cg.group
      ncg.consumer = cg.consumer
      ncg.consumer_b = c
      ncg.remark = cg.remark
      ncg.save()
    cg.delete()