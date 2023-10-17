import websocket
import _thread
from datetime import datetime
import json
import time
import valeurstest
import listetest
import statistics

chronoList = []

tnow = 99

def traitementMessage(message):
    #print(type(message))
    if  message.find("heartbeat") == -1:
        print( "%s" % message)
    
def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def ws_message (ws,message):
    global tnow
    #print(message)
    if datetime.now().second != tnow:
        tnow=datetime.now().second
        m=json.loads(message)
        #print("json : ",m)
        if m['e']=='kline':
            work( m['s'],m['E'],m['k']['t'],m['k']['T'],m['k']['s'], m['k']['i'],m['k']['f'],m['k']['L'],m['k']['o'],m['k']['c'],m['k']['h'],m['k']['l'],m['k']['v'],m['k']['n'],m['k']['x'],m['k']['q'],m['k']['V'],m['k']['Q'],m['k']['B'])

def ws_open(ws):
    s = '{ "method": "SUBSCRIBE", "params": ["btcusdt@kline_1s"], "id": 1}'
    ws.send(s)

def ws_thread(*args):
    ws = websocket.WebSocketApp("wss://stream.binance.com:9443/ws", on_open = ws_open, on_message = ws_message,on_error=on_error,on_close=on_close)
    ws.run_forever()

def work(s,E,kt,kT,ks,ki,kf,kL,ko,kc,kh,kl,kv,kn,kx,kq,kV,kQ,kB):

    open = float(ko)
    close = float(kc)
    high  = float(kh)
    low = float(kl)
    trueRange1 = 0
    positiveDM1 = 0
    negativeDM1 = 0
    trueRange14 = 0
    positiveDM14 = 0
    negativeDM14 = 0
    positiveDI14 = 0
    negativeDI14 = 0
    DIdifference14 = 0
    DIsummary14 = 0
    DX14 = 0
    ADX14 =0

    SMA20 = 0
    EcartType = 0
    listEcartType = []
    BBsup = 0
    BBinf = 0

    worklist = [s,E,kt,kT,ks,ki,kf,kL,float(ko),float(kc),float(kh),float(kl),kv,kn,kx,kq,kV,kQ,kB]

    if(len(chronoList) > 200):
        l = chronoList.pop(0)

    if(len(chronoList)>0):
        closeprev = float(chronoList[len(chronoList)-1][9])
        highprev = float(chronoList[len(chronoList)-1][10])
        lowprev = float(chronoList[len(chronoList)-1][11])
        ADX14prev = float(chronoList[len(chronoList)-1][30])
        trueRange1 = round(max(high-low,abs(high-closeprev),abs(low-closeprev)),6)
        if (high-highprev) > (lowprev-low): positiveDM1  = round(max((high-highprev),0),6)
        if (lowprev-low) > (high-highprev): negativeDM1  = round(max((lowprev-low),0),6) 

    if (len(chronoList) >= 14):
        for l in chronoList[len(chronoList)-13 : len(chronoList)]:
            trueRange14 += l[19]
            positiveDM14 += l[20]
            negativeDM14 += l[21]
            positiveDI14 += l[22]
            negativeDI14 += l[23]
            DIdifference14 += l[24]
            DIsummary14 += l[25]
            DX14 += l[26]
        trueRange14 += trueRange1
        positiveDM14 += positiveDM1
        negativeDM14 += negativeDM1
        if trueRange14!=0:
            positiveDI14 = (positiveDM14/trueRange14)*100
            negativeDI14 = (negativeDM14/trueRange14)*100
        DIdifference14 = abs(positiveDI14-negativeDI14)
        DIsummary14 = positiveDI14 + negativeDI14
        if DIsummary14!=0 : DX14 = (DIdifference14/DIsummary14)*100

    if (len(chronoList) >= 20):
        for l in chronoList[len(chronoList)-19 : len(chronoList)]:
            SMA20 += l[9]
            listEcartType.append(l[9])
        SMA20  +=  close
        listEcartType.append(close)
        SMA20 = round((SMA20/20),6)
        EcartType = round(statistics.pstdev(listEcartType),6)
        BBsup = round((SMA20 + (2*EcartType)),6)
        BBinf = round((SMA20 - (2*EcartType)),6)

    if (len(chronoList) >= 28):
        for i in chronoList[len(chronoList)-13 : len(chronoList)]:
            ADX14 += i[29]
        ADX14 += DX14
        ADX14/=14


    #trueRange14 /= 14
    worklist.append(trueRange1)     # 19
    worklist.append(positiveDM1)    # 20
    worklist.append(negativeDM1)    # 21
    worklist.append(trueRange14)    # 22
    worklist.append(positiveDM14)   # 23
    worklist.append(negativeDM14)   # 24
    worklist.append(positiveDI14)   # 25
    worklist.append(negativeDI14)   # 26
    worklist.append(DIdifference14) # 27
    worklist.append(DIsummary14)    # 28
    worklist.append(DX14)           # 29
    worklist.append(ADX14)          # 30
    worklist.append(SMA20)          # 31
    worklist.append(EcartType)      # 32
    worklist.append(BBsup)          # 33
    worklist.append(BBinf)          # 34

    #print("résultat: ",trueRange1,positiveDM1,negativeDM1,trueRange14,positiveDM14,negativeDM14,"PDI14", positiveDI14,"NDI14", negativeDI14, DIdifference14,DIsummary14,DX14,ADX14)
    #print("SMA20: ",SMA20, "EcartType: ", EcartType, "BBsup: ", BBsup, "BBinf: ", BBinf)
    
    # conditions
    # adx
    if ( ADX14 > 27 ) and ( negativeDI14 > positiveDI14 ) : 
        print("strong bearish")
        if ( ADX14 > ADX14prev ) and ( ADX14 > positiveDI14 ) : 
            print("adx vendre")
    elif ( ADX14 > 27 ) and ( positiveDI14 > negativeDI14 ) : 
        print("strong bullish")
        if ( ADX14 > ADX14prev ) and ( ADX14 > negativeDI14 ) :
            print("adx acheter")
    # bb
    if close>BBsup  : print("bb vendre")
    if close<BBinf : print("bb acheter")
    
    chronoList.append(worklist.copy())
    #print("chronolist: ",chronoList)

#for l in valeurstest.ltest:
    #print(0,0,0,0,0,0,0,0,l[9],l[11],l[12],l[10],0,0,0,0,0,0,0)
    work(0,0,0,0,0,0,0,0,l[9],l[11],l[12],l[10],0,0,0,0,0,0,0)

#for s in listetest.liste:
    #print(0,0,0,0,0,0,0,0,0,s,0,0,0,0,0,0,0,0,0)
    work(0,0,0,0,0,0,0,0,0,s,0,0,0,0,0,0,0,0,0)

pause=input("pause")
_thread.start_new_thread(ws_thread, ())

while True:
    yves = 1
    
