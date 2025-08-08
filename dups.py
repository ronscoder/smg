import difflib
from consumers.models import Consumer, MultiConsumer, ConsumerGrouping, State, ConsumerGroup
from getHistory import get_lastrecharge

def flag(c, dcs):
  mc = MultiConsumer.objects.create(consumer = c)
  mc.consumers.add(*dcs)

def add2untraceable(c):
  cg = ConsumerGroup(id=13)
  cgg = ConsumerGrouping()
  cgg.group = cg
  cgg.consumer= c
  cgg.remark = "search SM rank"
  cgg.save()
  print(c, 'added to', cgg)
def duplicate(a,b,both=False):
  try:
    mc, created = MultiConsumer.objects.get_or_create(consumer=a, consumer_b=b, duplication=True, mark_both=both)
  except Exception as ex:
    print(ex.__str__())
def start(cutoff=0.95):
  mcs = MultiConsumer.objects.all()
  mcss = [x.consumer for x in mcs]
  cggs = ConsumerGrouping.objects.all()
  gc = [x.consumer for x in cggs]
  #mcsb = [x.consumer_b for x in mcs]
  #mcss.extend(mcsb)
  
  #cs = Consumer.objects.filter(consumer_id__gt=max([x.consumer_id for x in mcss]), connection_status='ACTIVE', phase='SINGLE')
  s = State.objects.get(pk=1)
  last_cid = s.number
  print('last_cid', last_cid)
  cs = Consumer.objects.filter(connection_status='ACTIVE', phase='SINGLE', consumer_id__gte = last_cid).exclude(consumer_id__in=[x.consumer_id for x in mcss])
  #css = Consumer.objects.filter(connection_status='ACTIVE', phase='SINGLE')
  checkeds = []
  for index, c in enumerate(cs):
    ls = [x for x in cs if not x == c and c not in checkeds and x not in mcss]
    dcs = []
    for l in ls:
      #print('checking', c.consumer_id, 'against', l.consumer_id)
      matcher =difflib.SequenceMatcher(a=c.name, b=l.name)
      ratio = matcher.ratio()
      if(ratio>=cutoff):
        cg = ""
        cing = [x for x in cggs if x.consumer==c]
        if(len(cing)>0):
          cg = ", ".join([x.group.group_code for x in cing])
        lg = ""
        ling = [x for x in cggs if x.consumer==l]
        if(len(ling)>0):
          lg = ", ".join([x.group.group_code for x in ling])
        print()
        print('----')
        
        print(c.consumer_id, c.phase, c.load_kw)
        print(l.consumer_id, l.phase, l.load_kw)
        print()
        print(c.name, c.address.title(), cg, sep=",")
        print(c.meter_no, c.current_outstanding, sep=" , ")
        try:
          get_lastrecharge(c.meter_no)
        except Exception as ex:
          print('error getting recharge history')
        print()
        print(l.name, l.address.title(), lg, sep=", ")
        print(l.meter_no, l.current_outstanding, sep=" , ")
        try:
          get_lastrecharge(l.meter_no)
        except Exception as ex:
          print('error getting history')
        print()
        checkeds.append(l)
        x = input('cmd? ')
        if(x == 'a'):
          duplicate(c,l, False)
        if(x=='b'):
          duplicate(l,c,False)
        if(x=='ab'):
          duplicate(c,l,False)
          duplicate(l,c,False)
          #mcss.append(c)
        if(x=='au'):
          add2untraceable(c)
        if(x=='bu'):
          add2untraceable(l)
        if(x=='abu'):
          add2untraceable(c)
          add2untraceable(l)
        if(x == 'x'):
          mc, created = MultiConsumer.objects.get_or_create(consumer=c, consumer_b=l)
          #mc.remark = "duplicate, new connection"
          #mc.remark = "duplicate, new connection"
          mc.mark = True
          mc.save()
        if(not x == ""):
          s = State(pk=1)
          s.number = c.consumer_id
          s.save()
          mcss.append(c)
          checkeds.append(c)
          break
          #checkeds.append(l)
    #if(len(dcs)>0):
    #  flag(c, dcs)
    checkeds.append(c)
