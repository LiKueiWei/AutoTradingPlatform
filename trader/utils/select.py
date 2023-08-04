import logging
import numpy as np
import pandas as pd
from datetime import timedelta

from ..config import PATH, TODAY_STR, TODAY
from .time import TimeTool
from .file import FileHandler
from .crawler import readStockList
from .database import db, KBarTables
from .database.tables import SelectedStocks
try:
    from ..scripts.conditions import SelectConditions
except:
    logging.warning('Cannot import SelectConditions from package.')
    SelectConditions = None


class SelectStock(TimeTool, FileHandler):
    def __init__(self, scale='1D'):
        self.scale = scale
        self.Preprocess = {}
        self.METHODS = {}
        self.categories = {
            1: '水泥工業',
            2: '食品工業',
            3: '塑膠工業',
            4: '紡織纖維',
            5: '電機機械',
            6: '電器電纜',
            21: '化學工業',
            22: '生技醫療業',
            8: '玻璃陶瓷',
            9: '造紙工業',
            10: '鋼鐵工業',
            11: '橡膠工業',
            12: '汽車工業',
            24: '半導體業',
            25: '電腦及週邊設備業',
            26: '光電業',
            27: '通信網路業',
            28: '電子零組件業',
            29: '電子通路業',
            30: '資訊服務業',
            31: '其他電子業',
            14: '建材營造',
            15: '航運業',
            16: '觀光事業',
            17: '金融業',
            18: '貿易百貨',
            23: '油電燃氣業',
            19: '綜合',
            20: '其他',
            32: '文化創意業',
            33: '農業科技業',
            34: '電子商務',
            80: '管理股票'
        }

    def setScripts(self, methods: list = []):
        '''Set preprocess & stock selection scripts'''

        if SelectConditions:
            scripts = SelectConditions()
            self.Preprocess = {
                m: getattr(scripts, f'preprocess_{m}') for m in methods}
            self.METHODS = {
                m: getattr(scripts, f'condition_{m}') for m in methods}

            if hasattr(scripts, 'preprocess_index'):
                self.Preprocess.update({
                    'preprocess_index': scripts.preprocess_index})

    def load_and_merge(self):
        if db.HAS_DB:
            start = TODAY - timedelta(days=365*2)
            condition = KBarTables[self.scale].Time >= start
            df = db.query(KBarTables[self.scale], condition)
        else:
            dir_path = f'{PATH}/Kbars/{self.scale}'
            df = self.read_tables_in_folder(dir_path)

        df = df.drop_duplicates(['name', 'Time'], keep='last')
        df = df.sort_values(['name', 'Time'])
        return df

    def preprocess(self, df: pd.DataFrame):
        df = df.groupby('name').tail(365).reset_index(drop=True)
        df.name = df.name.astype(int).astype(str)
        df.Close = df.Close.replace(0, np.nan).fillna(method='ffill')

        for col in ['Open', 'High', 'Low', 'Close']:
            df.loc[
                (df.name == '8070') & (df.Time < '2020-08-17'), col] /= 10
            df.loc[
                (df.name == '6548') & (df.Time < '2019-09-09'), col] /= 10

        if 'preprocess_index' in self.Preprocess:
            df = self.Preprocess['preprocess_index'](df)

        return df

    def pick(self, *args):
        df = self.load_and_merge()
        df = self.preprocess(df)

        for m, func in self.Preprocess.items():
            if m != 'preprocess_index':
                df = func(df)

        for i, (m, func) in enumerate(self.METHODS.items()):
            df.insert(i+2, m, func(df, *args))

        # insert columns
        stockids = readStockList()
        stockids.category = stockids.category.astype(int)
        stockids = stockids.set_index('code')

        df.insert(1, 'company_name', df.name.map(stockids.name.to_dict()))
        df.insert(2, 'category', df.name.map(
            stockids.category.to_dict()).map(self.categories))

        return df

    def melt_table(self, df: pd.DataFrame, columns=[]):
        '''Melt the "strategy" columns into values of a table'''

        if not columns:
            columns = [
                'name', 'company_name', 'category', 'Time',
                'Open', 'High', 'Low', 'Close', 'Volume', 'Amount',
            ]
        select_methods = list(self.METHODS)

        df = df[columns + select_methods]
        df = df.melt(
            id_vars=columns,
            value_vars=select_methods,
            var_name='Strategy',
            value_name='isMatch'
        )
        df.Strategy *= df.isMatch
        df = df[df.Strategy != '']

        df = df.reset_index(drop=True).drop('isMatch', axis=1)
        df = df.rename(columns={'name': 'code'})
        df = df.sort_values(['Strategy', 'code'])

        return df

    def export(self, df: pd.DataFrame):
        if db.HAS_DB:
            db.dataframe_to_DB(df, SelectedStocks)
        else:
            self.save_table(df, f'{PATH}/selections/all.csv')
            self.save_table(
                df, f'{PATH}/selections/history/{TODAY_STR}-all.csv')

    def get_selection_files(self):
        '''取得選股清單'''

        day = self.last_business_day()

        if db.HAS_DB:
            df = db.query(SelectedStocks, SelectedStocks.Time == day)
        else:
            df = self.read_table(
                filename=f'{PATH}/selections/all.csv',
                df_default=pd.DataFrame(columns=[
                    'code', 'company_name', 'category', 'Time',
                    'Open', 'High', 'Low', 'Close',
                    'Volume', 'Amount', 'Strategy'
                ])
            )
            df.Time = pd.to_datetime(df.Time)
            df.code = df.code.astype(str)
            df = df[df.Time == day]

        return df
