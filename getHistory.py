'''
1. Search in billing consumers
2. If found, 
'''
import os
import pandas as pd
import sqlite3
conn_billingData = sqlite3.connect('./ignores/db/billingRechargeData.db')
conn_secureConsumers = sqlite3.connect('./ignores/db/secureConsumers.db')
conn_secureHistory = sqlite3.connect('./ignores/db/oldSecureHistory.db')
#conn_logs = sqlite3.connect('logs.db')

'''
CONNECTION ID METER No. CONSUMER NAME  AMOUNT  PAID ON
0    58000089932  Y0033694  LOYALAM BANK  1000.0  45183.0
'''
def sprint(s, n=20):
    print()
    for i,v in s.items():
        print(f'{i[:n]:20s}','\t\t', v)
def getConnectionNo(meter_no):
    #1. Check in billing
    #print('Checking in billing consumer database',meter_no)
    df = pd.read_sql(f'select * from consumers where "METER NO"="{meter_no}" limit 1', conn_billingData)
    if(not df.empty):
        #print(df.iloc[0])
        return df.iloc[0]['Prepaid Conn no']
    else:
        #print('Checking in the Recharge Reports...')
        df = pd.read_sql(f'select * from recharge_history where "METER No."="{meter_no}" limit 1', conn_billingData)
        if(not df.empty):
            #print(df.iloc[0])
            return df.iloc[0]['CONNECTION ID']
        else:
            #print('Checking in Secure consumer database')
            df = pd.read_sql(f'select * from liberty_old where "Meter No"="{meter_no}" limit 1', conn_secureConsumers)
            if(not df.empty):
                #print(df.iloc[0])
                return df.iloc[0]['Connection No']
            else:
                #print('Checking in (Old) Secure Recharge History')
                df = pd.read_sql(f'select * from RechargeHistory where "Meter No"="{meter_no}" limit 1', conn_secureHistory)
                if(not df.empty):
                    #print(df.iloc[0])
                    return df.iloc[0]['Connection No']
                else:
                    pass
                    #print('Consumer data not found. Meter No.', meter_no)
def fdatebilling(s):
    return pd.to_datetime(s-2, unit='D', origin='1900-01-01').dt.date

def getRechargeHistory(conn_no):
    #print('\nFetching from Recharge Reports... for', conn_no)
    columns=['CONNECTION ID', 'METER No.', 'PAID ON', 'AMOUNT']
    dfHistory = pd.DataFrame(columns = columns)
    #input()
    df1 = pd.read_sql(f'select * from recharge_history where "CONNECTION ID"="{conn_no}"', conn_billingData)
    if(not df1.empty):
        df1['PAID ON'] = fdatebilling(df1['PAID ON'])
        df1 = df1.sort_values('PAID ON', ascending=False)
        #print()
        #print(df1[columns].to_string())
        dfHistory = df1[columns]
    df2 = pd.read_sql(f'select * from RechargeHistory where "Connection No"="{conn_no}" ', conn_secureHistory)
    if(not df2.empty):
        df2['Issue Date'] = pd.to_datetime(df2['Issue Date']).dt.date
        #df21 = pd.DataFrame()
        df21=pd.DataFrame(columns=columns)
        df21['CONNECTION ID'] = df2['Connection No']
        df21['METER No.'] = df2['Meter No']
        df21['PAID ON'] = df2['Issue Date']
        df21['AMOUNT'] = df2['Transaction Amount']
        df21 = df21.sort_values('PAID ON', ascending=False)
        #print()
        #print(df21.to_string())
        dfHistory = pd.concat([dfHistory, df21], join='inner', ignore_index=True)
    return dfHistory.iloc[[0,-1]]
    
def dfprint(df):
    for i, row in df.iterrows():
        print(row)

def get_lastrecharge(meter_no):
  meter_no = meter_no.upper()
  connection_no = getConnectionNo(meter_no)
  print('connection_no', connection_no)
  if(connection_no == None):
      print('No prepaid data')
  #getConsumerInfo(int(connection_no))
  dfHistory = getRechargeHistory(conn_no=int(connection_no))
  if(dfHistory.empty):
      print('No recharge history found')
  else:
      df= dfHistory.drop(['CONNECTION ID', 'METER No.'], axis=1)
      print(df.to_string())


'''
Fetching from Recharge Reports...
SERIAL NO                    1.0
CONNECTION ID        58000089932
METER No.               Y0033694
METER MAKE                   1.0
CONSUMER NAME       LOYALAM BANK
AMOUNT                    1000.0
PAID ON                  45183.0
PAYMENT MODE     BILLDESK ONLINE
Name: 0, dtype: object
'''
'''
Fetching from (Old) Secure Recharge History
Connection No                                          58000089932
Title                                                          Mr.
First Name                                            LOYALAM BANK
Last Name                                                   IED-IV
MPAN                                                          None
Issue Date                                     2020-12-02 00:00:00
Meter No                                                  Y0033694
Transaction Amount                                            1000
Tariff Category                                                 SD
Tariff Name                                  DOMESTIC SINGLE PHASE
Tariff Id                                                      9.0
Call Centre                                                   None
Operator                                                      None
Agent Id                                                       154
Terminal Id                                                    154
Invalid Request Date                                          None
Confirmed Invalid Request Date                                None
Invalid Request Confirmed User                                None
Transaction Type                                          New Vend
Transaction Status                                             0.0
Current Date                                   2021-01-05 00:00:00
RSP Code                                                      MNPP
Com Server No                                                154.0
Terminal/Com Server Trans.Request Date         2020-12-02 00:00:00
Encryption Server Trans. No.                            53885508.0
Terminal/Com Server Trans. No.                         712093162.0
Sanctioned Load                                                2.0
Token Type                                               Vend Code
Credit Account                                                 0.0
Free Vend Amount                                               0.0
Reason Code                                                   None
Reason Code Details                                           None
Post Code                                                      SGM
Connection Type                                          Permanent
Activation Date Time                                          None
Connection Period                                             None
Connection Term                                               None
House No                                                    IED-IV
House Name                                                SM- 101N
VAT (p)/unit                                                   0.0
Cheque/Demand Draft/Statement No.                             None
Cheque/Demand Draft/Statement Expiry Date                     None
Bank Name                                                     None
Load Limit                                                     2.0
Customer Based Emergency Credit Limit                         None
'''
