from .. import API
from . import get_contract


class Subscriber:
    def __init__(self):
        # 即時成交資料, 所有成交資料, 下單資料
        self.quotes_now_s = {}
        self.quotes_now_i = {}
        self.quotes_now_f = {}
        self.quotes_all_s = {}
        self.quotes_all_i = {'TSE001': [], 'OTC101': []}
        self.quotes_all_f = {}
        self.BidAsk = {}

    def _set_target_quote_default(self, targets: str, market: str = 'Stocks'):
        '''初始化股票/期權盤中資訊'''
        keys = ['price', 'amount', 'total_amount', 'volume', 'total_volume', 'tick_type']
        if market == 'Stocks':
            self.quotes_all_s = {s: {k: [] for k in keys} for s in targets}
        elif market == 'Futures':
            self.quotes_all_f = {t: {k: [] for k in keys} for t in targets}

    def _set_index_quote_default(self):
        '''初始化指數盤中資訊'''
        self.quotes_all_i = {'TSE001': [], 'OTC101': []}

    def index_v0(self, quote: dict):
        if quote['Code'] == '001':
            self.quotes_now_i['TSE001'] = quote
            self.quotes_all_i['TSE001'].append(quote)
        elif quote['Code'] == '101':
            self.quotes_now_i['OTC101'] = quote
            self.quotes_all_i['OTC101'].append(quote)

    def stk_quote_v1(self, tick):
        '''處理股票即時成交資料'''
        tick_data = dict(tick)
        for k in [
            'open', 'close', 'high', 'low', 'amount', 'total_amount', 'total_volume',
            'avg_price', 'price_chg', 'pct_chg'
        ]:
            tick_data[k] = float(tick_data[k])
        tick_data['price'] = tick_data['close']

        for k in ['price', 'amount', 'total_amount', 'volume', 'total_volume', 'tick_type']:
            self.quotes_all_s[tick.code][k].append(tick_data[k])

        self.quotes_now_s[tick.code] = tick_data
        return tick_data

    def fop_quote_v1(self, symbol: str, tick):
        '''處理期權即時成交資料'''
        tick_data = dict(tick)
        for k in [
            'open', 'close', 'high', 'low', 'amount', 'total_amount',
            'underlying_price', 'avg_price', 'price_chg', 'pct_chg'
        ]:
            tick_data[k] = float(tick_data[k])

        tick_data['price'] = tick_data['close']
        tick_data['symbol'] = symbol

        for k in ['price', 'amount', 'total_amount', 'volume', 'total_volume', 'tick_type']:
            self.quotes_all_f[symbol][k].append(tick_data[k])

        self.quotes_now_f[symbol] = tick_data
        return tick_data

    def subscribe_index(self):
        '''訂閱指數盤中資訊'''

        API.quote.subscribe(API.Contracts.Indexs.TSE.TSE001, quote_type='tick')
        API.quote.subscribe(API.Contracts.Indexs.OTC.OTC101, quote_type='tick')
        self._set_index_quote_default()

    def unsubscribe_index(self):
        '''取消訂閱指數盤中資訊'''

        API.quote.unsubscribe(API.Contracts.Indexs.TSE.TSE001, quote_type='tick')
        API.quote.unsubscribe(API.Contracts.Indexs.OTC.OTC101, quote_type='tick')

    def subscribe_targets(self, targets: list, quote_type: str = 'tick'):
        '''訂閱股票/期貨盤中資訊'''

        for t in targets:
            target = get_contract(t)
            API.quote.subscribe(target, quote_type=quote_type, version='v1')

    def unsubscribe_targets(self, targets, quote_type: str = 'tick'):
        '''取消訂閱股票盤中資訊'''

        for t in targets:
            target = get_contract(t)
            API.quote.unsubscribe(target, quote_type=quote_type, version='v1')

    def subscribe_all(self, targetLists: dict):
        '''訂閱指數、tick、bidask資料'''

        self.subscribe_index()
        for market, targets in targetLists.items():
            self.subscribe_targets(targets, 'tick')
            self.subscribe_targets(targets, 'bidask')
            self._set_target_quote_default(targets, market)

    def unsubscribe_all(self, targetLists: dict):
        '''取消訂閱指數、tick、bidask資料'''

        self.unsubscribe_index()
        for _, targets in targetLists.items():
            self.unsubscribe_targets(targets, 'tick')
            self.unsubscribe_targets(targets, 'bidask')
