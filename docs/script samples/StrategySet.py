import pandas as pd
from datetime import datetime
from trader.utils.strategy import StrategyTool


class StrategySet(StrategyTool):
    '''
    ===================================================================
    StrategySet is a set of strategy class for AutoTradingPlatform, it 
    inherits the StrategyTool Object for the use of common functions.

    *****
    The attributes in the __init__ are all necessary, itestablishes the 
    Funcs attribute when the system starts.
    *****

    After preparing the script, set the target script to be executed 
    in self.Funcs in init. For example, if buyStrategy1 belongs to 
    Strategy1 and is a 非當沖 buying strategy, then buyStrategy1 
    should be classified into 
    self.Funcs['Open']['非當沖']['Strategy1'], where Open means 
    opening a position, whereas Close is to close a position.
    ===================================================================
    '''

    def __init__(self, **kwargs):
        StrategyTool.__init__()

        # customized settings
        self.STRATEGIES = pd.DataFrame(
            # table of strategy set, recording each strategy name and its
            # weight of long/short perspective. If a strategy is a long
            # strategy, give an integer to its long_weight and 0 to its
            # short_weight; and vice versa.
            [
                ['Strategy1', 1, 0],
                ['Strategy2', 2, 0],
                ['Strategy3', 3, 0],
                ['Strategy4', 0, 1],
            ],
            columns=['name', 'long_weight', 'short_weight']
        )
        self.Funcs = {
            'Open': {
                '當沖': {},
                '非當沖': {
                    'Strategy1': self.buyStrategy1,
                    'Strategy2': self.sellStrategy2,
                }
            },
            'Close': {
                '當沖': {},
                '非當沖': {
                    'Strategy1': self.sellStrategy1,
                    'Strategy2': self.buyStrategy2,
                }
            }
        }

        self.QuantityFunc = {
            'Strategy1': self.quantityStrategy1
        }

    def update_indicators(self, now: datetime, kbars: dict):
        '''
        ===================================================================

        *****OPTIONAL*****

        Functions of updating indicators for all SHORT strategies. Any new
        indicator data can be created as an attribute in this module.This 
        function is OPTIONAL to use, which means if not determine this func, 
        the system will not be affected.
        ===================================================================
        '''
        pass

    def setNStockLimitLong(self, KBars: dict = None):
        '''
        ===================================================================

        *****OPTIONAL*****

        Functions of setting the number of STOCK limit to trade for all 
        LONG strategies. This function is OPTIONAL to use, which means 
        if not determine this func, the system will automatically return 
        the value of self.stock_limit_long for further operations.
        ===================================================================
        '''
        if self.is_simulation:
            return 3000
        elif self.stock_limit_type != 'constant':
            return self.stock_limit_long
        return self.stock_limit_long

    def setNFuturesLimit(self, KBars: dict = None):
        '''
        ===================================================================

        *****OPTIONAL*****

        Functions of setting the number of FUTURES limit to trade for all 
        futures strategies. This function is OPTIONAL to use, which means 
        if not determine this func, the system will automatically return 
        the value of self.futures_limit for further operations.
        ===================================================================
        '''
        if self.futures_limit_type != 'constant':
            return self.futures_limit
        return self.futures_limit

    def quantityStrategy1(self, inputs: dict, kbars: pd.DataFrame, **kwargs):
        '''
        ===================================================================

        *****OPTIONAL*****

        Functions of calculating quantity of opening stock positions. It 
        returns 2 values: quantity & quantity_limit, where quantity is 
        determined by your strategy and quantity_limit is set to default 
        1.   This function is OPTIONAL to use, which means if not deter-
        mine this func, the system will automatically return 1, 499 for
        further operations.
        ===================================================================
        '''
        quantity = 1
        quantity_limit = 499
        return quantity, quantity_limit

    def buyStrategy1(self, inputs: dict, kbars: dict, **kwargs):
        '''
        ===================================================================
        Functions of determining if the system can open a LONG stock 
        position.

        Arguments:
        inputs: daily quote data of a stock/futures security, including, 
        open, high, low, close, volume, ..., etc
        kbars: Kbar data for condition checking, supported kbar frequencies
        are 1D, 60T, 30T, 15T, 5T, 1T.

        Supported key-word arguments:
        indexQuotes: index quote data (TSE, OTC) for the specific trade-
        day.
        pct_chg_DowJones: the percentage change of the previous trade-day
        Dow-Jones index.

        The function returns a namedtuple Object, including position(%), 
        reason, and msg.
        ===================================================================
        '''
        buy_condition = inputs['price'] > inputs['open']
        if buy_condition == True:
            buy_position = 100
            return self.Action(buy_position, 'buy_type', 'buy_message')
        return self.Action()

    def sellStrategy1(self, inputs: dict, kbars: dict, **kwargs):
        '''
        ===================================================================
        Functions of determining if the system can close a LONG stock 
        position.

        Arguments:
        inputs: daily quote data of a stock/futures security, including, 
        open, high, low, close, price, volume, ..., etc
        kbars: Kbar data for condition checking, supported kbar frequencies
        are 1D, 60T, 30T, 15T, 5T, 1T.

        Supported key-word arguments:
        indexQuotes: index quote data (TSE, OTC) for the specific trade-
        day.
        pct_chg_DowJones: the percentage change of the previous trade-day
        Dow-Jones index.

        The function returns a namedtuple Object, including position(%), 
        reason, and msg.
        ===================================================================
        '''
        sell_condition = inputs['price'] < inputs['open']
        if sell_condition == True:
            sell_position = 100
            return self.Action(sell_position, 'sell_type', 'sell_message')
        return self.Action()

    def buyStrategy2(self, inputs: dict, kbars: dict, **kwargs):
        '''
        ===================================================================
        Functions of determining if the system can close a SHORT stock 
        position.

        Arguments:
        inputs: daily quote data of a stock/futures security, including, 
        open, high, low, close, volume, ..., etc
        kbars: Kbar data for condition checking, supported kbar frequencies
        are 1D, 60T, 30T, 15T, 5T, 1T.

        Supported key-word arguments:
        indexQuotes: index quote data (TSE, OTC) for the specific trade-
        day.
        pct_chg_DowJones: the percentage change of the previous trade-day
        Dow-Jones index.

        The function returns a namedtuple Object, including position(%), 
        reason, and msg.
        ===================================================================
        '''
        buy_condition = inputs['price'] > inputs['open']
        if buy_condition == True:
            buy_position = 100
            return self.Action(buy_position, 'buy_type', 'buy_message')
        return self.Action()

    def sellStrategy2(self, inputs: dict, kbars: dict, **kwargs):
        '''
        ===================================================================
        Functions of determining if the system can open a SHORT stock 
        position.

        Arguments:
        inputs: daily quote data of a stock/futures security, including, 
        open, high, low, close, price, volume, ..., etc
        kbars: Kbar data for condition checking, supported kbar frequencies
        are 1D, 60T, 30T, 15T, 5T, 1T.

        Supported key-word arguments:
        indexQuotes: index quote data (TSE, OTC) for the specific trade-
        day.
        pct_chg_DowJones: the percentage change of the previous trade-day
        Dow-Jones index.

        The function returns a namedtuple Object, including position(%), 
        reason, and msg.
        ===================================================================
        '''
        sell_condition = inputs['price'] < inputs['open']
        if sell_condition == True:
            sell_position = 100
            return self.Action(sell_position, 'sell_type', 'sell_message')
        return self.Action()
