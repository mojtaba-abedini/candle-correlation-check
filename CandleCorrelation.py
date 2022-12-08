import MetaTrader5 as mt5
import pytz
from datetime import datetime
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from tqdm import tqdm




scaler = MinMaxScaler()

if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())
    quit()



accountNumber = int(input(' * Enter your account number : '))
accountPassword = input(' * Enter your account password : ')
symbol = input(' * Enter symbol : ')
period = int(input(' * Enter your period for check : '))


def timeframe(item):
    if item == 1:
        return 1
    elif item == 2:
        return 5
    elif item == 3:
        return 15
    elif item == 4:
        return 30
    elif item == 5:
        return 16385
    elif item == 6:
        return 16388
    elif item == 7:
        return 16408
    else:
        return 'The time frame in not valid !'
    
timeFrameInput = int(input(""" * Enter your time frame :

    1 : M1
    2 : M5
    3 : M15
    4 : M30
    5 : H1
    6 : H4
    7 : D1         

    """))

timeFrame = timeframe(timeFrameInput)

fromYear = int(input(' * Enter from date year : '))
fromMonth = int(input(' * Enter from date month : '))
fromDay = int(input(' * Enter from date day : '))
                 
account = accountNumber
login = mt5.login(account,password=accountPassword)




timezone = pytz.timezone("Etc/UTC")
year = datetime.now().year
month = datetime.now().month
day = datetime.now().day
hour = datetime.now().hour
minute = datetime.now().minute
second = datetime.now().second


utc_from=datetime(fromYear,fromMonth,fromDay,tzinfo=timezone)
utc_to=datetime(year,month,day,hour, minute, second , tzinfo=timezone)
rates=mt5.copy_rates_range(symbol,timeFrame,utc_from,utc_to)

df = pd.DataFrame(rates)
df['time']=pd.to_datetime(df['time'], unit='s')
df=df[['time','open','high','low','close']]
df['shadowSize']=df['high']-df['low']
df['bodySize']=df['close']-df['open']


dfArr = df[['shadowSize','bodySize']].to_numpy()
dfScaled = scaler.fit_transform(dfArr)


lastPeriod = dfScaled[-period:]
lastPeriod=pd.DataFrame(lastPeriod)


test = []
resultdf=[]

for i in tqdm(range(0,df.shape[0]),total=df.shape[0],desc=' * Progressing'):
    test=dfScaled[i : i+period] 
    test=pd.DataFrame(test)
    i +=1
    result = lastPeriod.corrwith(test)
    resultdf.append(result)


final=[]
resultdf=pd.DataFrame(resultdf)
resultdf['index']=resultdf.index

resultdf = resultdf.rename(columns={0:'shadowSize',1:'bodySize'})
for i in resultdf.index:
    if(((resultdf['shadowSize'][i] > 0.90) & (resultdf['bodySize'][i] > 0.90))|((resultdf['shadowSize'][i] < -0.90) & (resultdf['bodySize'][i] < -0.90))):
        final.append(resultdf['index'][i])



finalResult=[]
for i in final:
 
    finalResult.append(df.iloc[i])

finalResult=pd.DataFrame(finalResult)
finalResult.to_csv('output.csv')
print(finalResult)
print ('The output save in output.csv file ...')


def graph_data_ohlc(dataset):
    fig = plt.figure(figsize=(16,8))
    ax1 = plt.subplot2grid((1,1), (0,0))
    closep=dataset[:,[4]]
    highp=dataset[:,[2]]
    lowp=dataset[:,[3]]
    openp=dataset[:,[1]]
    date=range(len(closep))

    x = 0
    y = len(date)
    ohlc = []
    while x < y:
        append_me = date[x], openp[x], highp[x], lowp[x], closep[x]
        ohlc.append(append_me)
        x+=1
    candlestick_ohlc(ax1, ohlc, width=0.4, colorup='#26a69a', colordown='#ef5350')
    for label in ax1.xaxis.get_ticklabels():
        label.set_rotation(45)
    ax1.xaxis.set_major_locator(mticker.MaxNLocator(10))
    ax1.grid(True)
    plt.xlabel('Candle')
    plt.ylabel('Price')
    plt.title('XAUUSD')

    plt.subplots_adjust(left=0.09, bottom=0.20, right=0.94, top=0.90, wspace=0.2, hspace=0)
    plt.show()
    
    
candleShow = 80
ohlc_data=[]
for i in final[:-1]:
    ohlc_data=[]
    print(df.iloc[i]['time'])
    for n in range(candleShow):
      
        ohlc_data.append(df.iloc[i])
        i +=1
        n +=1
      
    ohlc_data=pd.DataFrame(ohlc_data)
    graph_data_ohlc(ohlc_data.tail(80).values)



