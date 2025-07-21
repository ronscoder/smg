def bs(month_unit):
      if(month_unit>100):
        b1 = 100
      else:
        b1 = month_unit
      b3=0
      if(month_unit>200):
        b2 = 100
        b3=month_unit-200
      else:
        if(month_unit>100):
          b2=month_unit-100
        else:
          b2 = 0
      print(b1,b2,b3)

bs(int(input('units')))


