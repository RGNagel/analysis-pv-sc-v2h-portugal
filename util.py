from pandas import DataFrame, read_csv
import pandas as pd

class Table:

    def __init__(self):
        
        filename = 'datetime_consumo_injecao.xls'
        self.table = pd.read_excel(filename)

        self._splitInMonths()


    def getTable(self):
        return self.table

    def getMonths(self):
        """
        return: array (0-11) of dataframes
        """
        return self.months

    def setCons_kW(self):
        CONS_AVG_CLIENT_KWH = 3506.00
        self.table['Consumo'] = self.table['Consumo'] * CONS_AVG_CLIENT_KWH / 1000

    def setInjection_kWp(self, power_kWp):
        # fonte: https://www.sciencedirect.com/science/article/abs/pii/S1364032119301881
        e = 0.18
        PROD_AVG_CLIENT_KWH = 1600 * power_kWp * (1 - e)
        self.table['Injeção'] = self.table['Injeção'] * PROD_AVG_CLIENT_KWH / 1000

    def _splitInMonths(self):
        """

        """
        self.months = [0] * 12

        beg = 0
        end = 0

        for i in range(0, len(self.months), 1):
            
            days = self.table['Datetime'][beg].days_in_month
            
            end = beg + days * 96
            self.months[i] = self.table[beg : end]
            beg = end


    def getDaysInMonth(self, month):
        """
        month: 0-11
        """
        return self.months[month]['Datetime'].array[0].days_in_month

    def getDayInMonth(self, month, day):
        """
        month : 0-11
        day   : 0-30

        return : dataframe
        """
        beg = day * 96;
        end = beg + 96;
        return self.months[month][beg : end]

# class Fatura:
#     @staticmethod
#     def getPeakPeriodInDay(df_day):


class BatteryV2H:
    EFFICIENCY = 0.85
    #  capacidade média utilizável da bateria em kWh
    #  fonte: https://ev-database.org/cheatsheet/useable-battery-capacity-electric-car
    MAX_CAPACITY = 60.1

    _charge_level = 0

    def setChargeLevel(self, kWh):
        _charge_level = kWh;

    def getMinimumChargeLevel(self):
        available_factor = 0.5 # valor arbitrário
        return MAX_CAPACITY * available_factor # [kWh]
    
    def getMaximumChargeLevel(self):
        return MAX_CAPACITY

    def getFreeSpaceToStore(self):
        """
        get space available to store in kWh
        """
        return MAX_CAPACITY - self._getChargeLevel()

    def getFreeSpaceToDrain(self):
        """
        get space available to drain from battery in kWh
        """
        if self._getChargeLevel() > 

    def _getChargeLevel(self):
        return self._charge_level

    def getSoC():
        return self._charge_level / MAX_CAPACITY

    def getDoD():
        return 1 - self.getSoC()

    def __init__(self, sheetname):

        self.df = pd.read_excel(io='usage_periods.xls', sheet_name=sheetname)

    # def getEnergyAvailable(kWh):

    def drain(kWh):
        self._charge_level = self._charge_level - kWh

    def store(kWh):
        self._charge_level = self._charge_level + kWh

    def isAvailable(self, ts):
        """
        ts: Pandas Timestamp object 
        """

        # filter = data['week_num'] == ts.dayofweek
        # row = self.df.where(filter)
        row = self.df[ts.dayofweek : ts.dayofweek + 1]

        hh = ts.hour + ts.minute / 60
        begin = row['begin'].array[0]
        end = row['end'].array[0]

        if hh >= begin and hh <= end:
            return True
        else:
            return False


class Fatura:
    OFFPEAK_BEGIN = 22
    OFFPEAK_END = 8

    # €/kWh
    PRICE_OFFPEAK = 0.1213;
    PRICE_PEAK = 0.2262;
    # preço da injeção em EUR/kWh
    # fonte: m.omie.es/files/omie_informe_precios_pt.pdf?m=yes
    PRICE_INJECTION = 0.05745;
    
    @staticmethod
    def isWithinOffpeak(ts):
        """
        ts: Pandas Timestamp object 
        """
        within = False

        hh = ts.hour + ts.minute / 60

        if hh > OFFPEAK_BEGIN and hh <= 24:
            within = True
        elif hh > 0 and hh <= OFFPEAK_END:
            within = True

        return within

    def __init__(self):
        # kWh
        self._injection = 0
        self._consumption_peak = 0
        self._consumption_offpeak = 0
        self._waste = 0

    def addInjection(self, kwh):
        self._injection = self._injection + kwh

    def addWaste(self, kwh):
        self._waste = self._waste + kwh

    def addConsumption(self, kwh, ts):
        if isWithinOffpeak(ts):
            self._consumption_offpeak = self._consumption_offpeak + kwh
        else:
            self._consumption_peak = self._consumption_peak + kwh

    def getInjectionValue(self):
        return self._injection * PRICE_INJECTION

    def getConsumptionValue(self):
        return self._consumption_offpeak * PRICE_OFFPEAK 
             + self._consumption_peak * PRICE_PEAK

    def getFinalValue(self):
        return self.getConsumptionValue() - self.getInjectionValue()
    
    def printInfo(self):
        print(f"Total injection     : {self._injection}\n")
        print(f"Total waste         : {self._waste}\n")
        print(f"Total peak cons.    : {self._consumption_peak}\n")
        print(f"Total offpeak cons. : {self._consumption_offpeak}\n")
        print(f"Final value         : {self.getFinalValue()}\n")


