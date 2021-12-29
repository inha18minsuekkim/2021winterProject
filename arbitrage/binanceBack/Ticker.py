import datetime,ssl,pathlib,websockets,asyncio,signal,json,pytz
from functools import partial
import numpy as np
import arbitrage.CoinData.CoinDataManager as cdm
class Ticker:
    def __init__(self, code, timestamp, open, high, low, close, volume):
        self.code = code
        self.timestamp = timestamp
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
    @staticmethod
    def load_from_json(js):
        return Ticker(code=js['s'],timestamp=datetime.date.fromtimestamp(js['k']['t']/1000),
                      open=js['k']['o'],high=js['k']['h'],low=js['k']['l'],close=js['k']['c'],volume=js['k']['v'])
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return f'Ticker <code: {self.code}, timestamp: {self.timestamp.strftime("%Y-%m-%d %H:%M:%S")}, '\
                f'open: {self.open}, high: {self.high}, '\
                f'low: {self.low}, close : {self.close}, volume: {self.volume}>'

async def recv_ticker():
    CDM = cdm.CoinDataManager()
    print(CDM.label)
    print(CDM.data)
    uri = 'wss://stream.binance.com:9443'
    markets = ['BTCUSDT','ETHUSDT']
    stream = 'kline_1m'
    params = '/'.join([f'{market.lower()}@{stream}' for market in markets])
    uri = uri + f'/stream?streams={params}'
    print(uri)
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    self_signed_cert = pathlib.Path(__file__).with_name("server.crt")
    ssl_context.load_verify_locations(self_signed_cert)
    async with websockets.connect(uri, ssl=ssl_context) as websocket:
        var = asyncio.Event()
        def sigint_handler(var, signal, frame):
            print(f'< recv SIG_INT')
            var.set()
        #signal.signal(signal.SIGINT, partial(sigint_handler,var))
        while not var.is_set():
            recv_data = await websocket.recv()
            #print(recv_data)
            res = Ticker.load_from_json(json.loads(recv_data)['data'])
            #print(res)
            CDM.data[CDM.label[res.code]] = np.append(CDM.data[CDM.label[res.code]],float(res.close))
            if len(CDM.getBTC()) != 0 and len(CDM.getETH()) != 0 :
                CDM.ratio = np.append(CDM.ratio,(CDM.getBTC()[-1]-CDM.getETH()[-1])/CDM.getETH()[-1])
            #print(CDM.data)
            print(CDM.ratio)
            #print(len(CDM.data[0]),len(CDM.data[1]))