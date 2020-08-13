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
        self.table['Produção'] = self.table['Produção'] * PROD_AVG_CLIENT_KWH / 1000

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



"""
When V2H returns to home, we should set its charge level.
We defined the charge level to 50% of capacity when V2H returns home.
Also, the minimum charge level is 50% i.e. charge level must not be below this threshhold.
"""

class BatteryV2H:
    EFFICIENCY = 0.85
    #  capacidade média utilizável da bateria em kWh
    #  fonte: https://ev-database.org/cheatsheet/useable-battery-capacity-electric-car
    MAX_CAPACITY = 60.1
    _charge_level = 0

    def __init__(self, sheetname='', always=False, never=False):
        self._always = always
        self._never = never
        if always and never:
            raise Exception("always and never are both True")

        if not always and not never:
            self.df = pd.read_excel(io='usage_periods.xls', sheet_name=sheetname)

        self._charge_level = self._getMinimumChargeLevel()
        self._totalDrained = 0
        self._totalStored = 0

    def _setChargeLevel(self, kWh):
        _charge_level = kWh;

    def _getMinimumChargeLevel(self):
        available_factor = 0.5 # valor arbitrário
        return self.MAX_CAPACITY * available_factor # [kWh]
    
    def _getMaximumChargeLevel(self):
        return self.MAX_CAPACITY

    def getFreeSpaceToStore(self):
        """
        get space available to store in kWh
        """
        return self._getMaximumChargeLevel() - self._getChargeLevel()


    def getFreeSpaceToDrain(self):
        """
        get space available to drain from battery in kWh
        """
        return self._getChargeLevel() - self._getMinimumChargeLevel()

    def _getChargeLevel(self):
        if self._charge_level > self._getMaximumChargeLevel():
            raise Exception("Charge level is greater than maximum charge level\n")
        if self._charge_level < self._getMinimumChargeLevel():
            raise Exception("Charge level is smaller than minimum charge level\n")

        return self._charge_level

    def getSoC():
        return self._charge_level / self.MAX_CAPACITY

    def getDoD():
        return 1 - self.getSoC()


    # def getEnergyAvailable(kWh):

    def drain(self, kWh):
        self._charge_level = self._charge_level - kWh
        self._totalDrained = self._totalDrained + kWh
        if self._charge_level < self._getMinimumChargeLevel():
            raise Exception(f"charge level below minimum {self._getMinimumChargeLevel()}\n")

    def store(self, kWh):
        self._charge_level = self._charge_level + kWh
        self._totalStored = self._totalStored + kWh
        if self._charge_level > self._getMaximumChargeLevel():
            raise Exception(f"charge level above maximum {self._getMaximumChargeLevel()}")

    def isAvailable(self, ts):
        """
        ts: Pandas Timestamp object 
        """

        if self._always:
            return True
        elif self._never:
            return False

        # filter = data['week_num'] == ts.dayofweek
        # row = self.df.where(filter)
        row = self.df[ts.dayofweek : ts.dayofweek + 1]

        hh = ts.hour + ts.minute / 60
        begin = row['begin'].array[0]
        end = row['end'].array[0]

        if hh >= begin and hh <= end:
            return True
        else:
            # Set the charge to the level which will be available when V2H goes home. 
            self._setChargeLevel(self._getMinimumChargeLevel())
            return False

    def getTotalStored(self):
        return self._totalStored

    def getTotalDrained(self):
        return self._totalDrained

    def resetTotalStored(self):
        self._totalStored = 0

    def resetTotalDrained(self):
        self._totalDrained = 0


class Fatura:
    OFFPEAK_BEGIN = 22
    OFFPEAK_END = 8

    # €/kWh
    PRICE_OFFPEAK = 0.1213
    PRICE_PEAK = 0.2262
    # preço da injeção em EUR/kWh
    # fonte: m.omie.es/files/omie_informe_precios_pt.pdf?m=yes
    PRICE_INJECTION = 0.05745
    
    @staticmethod
    def isWithinOffpeak(ts):
        """
        ts: Pandas Timestamp object 
        """
        within = False

        hh = ts.hour + ts.minute / 60

        if hh > Fatura.OFFPEAK_BEGIN and hh <= 24:
            within = True
        elif hh > 0 and hh <= Fatura.OFFPEAK_END:
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
        if self.isWithinOffpeak(ts):
            self._consumption_offpeak = self._consumption_offpeak + kwh
        else:
            self._consumption_peak = self._consumption_peak + kwh

    def getInjectionValue(self):
        return self._injection * self.PRICE_INJECTION

    def getConsumptionValue(self):
        return self._consumption_offpeak * self.PRICE_OFFPEAK \
             + self._consumption_peak * self.PRICE_PEAK

    def getFinalValue(self):
        return self.getConsumptionValue() - self.getInjectionValue()
    
    def setBatteryTotalStored(self, kWh):
        self._batteryTotalStored = kWh
    def setBatteryTotalDrained(self, kWh):
        self._batteryTotalDrained = kWh

    def getBatteryTotalStored(self):
        return self._batteryTotalStored

    def getBatteryTotalDrained(self):
        return self._batteryTotalDrained

    def printInfo(self):
        print(f"Total injection     : {self._injection} kWh\n")
        print(f"Total waste         : {self._waste} kWh\n")
        print(f"Total peak cons.    : {self._consumption_peak} kWh\n")
        print(f"Total offpeak cons. : {self._consumption_offpeak} kWh\n")
        print(f"Final value         : {self.getFinalValue()} EUR\n")
        print(f"Total bat. stored   : {self.getBatteryTotalStored()} kWh\n")
        print(f"Total bat. drained  : {self.getBatteryTotalDrained()} kWh\n")


def getFaturasYear(injection, kWp, batteryV2H_obj):

    if injection is not True and injection is not False:
        raise Exception("Injection must be true or false\n")

    kwps = [0.5, 0.75, 1.5, 3.45]
    if kWp not in kwps:
        raise Exception(f"kWp must be one of {kwps}")

    if not isinstance(batteryV2H_obj, BatteryV2H):
        raise Exception("Not an instance of BatteryV2H\n")

    bat = batteryV2H_obj
    
    tab = Table()
    tab.setCons_kW()
    tab.setInjection_kWp(kWp)

    months = tab.getMonths()

    faturas = []

    for m in range(0, 12, 1):
        
        fat = Fatura()

        days = tab.getDaysInMonth(m)
        for d in range(0, days, 1):
        
            day_df = tab.getDayInMonth(m, d)

            exc = (day_df["Produção"] - day_df["Consumo"]).array

            for interval in range(0, 96, 1):
                # every 15 min of this day

                if exc[interval] >= 0:
                    # produção >= consumo
                    
                    if bat.isAvailable(day_df["Datetime"].array[interval]):
                        
                        space = bat.getFreeSpaceToStore()

                        if space >= exc[interval]:
                            bat.store(exc[interval])
                        else:
                            # exc > space
                            bat.store(space)
                            remaining = exc[interval] - space
                            if injection is True:
                                fat.addInjection(remaining)
                            else:
                                fat.addWaste(remaining)

                    else:
                        # battery not available
                        if injection is True:
                            fat.addInjection(exc[interval])
                        else:
                            fat.addWaste(exc[interval])

                else:
                    # consumo > produção
                    exc[interval] = abs(exc[interval])

                    if bat.isAvailable(day_df["Datetime"].array[interval]):
                        space = bat.getFreeSpaceToDrain()

                        if space >= exc[interval]:
                            # all energy required is supplied by battery
                            bat.drain(exc[interval])
                            # fat.addConsumption(exc[interval], day_df["Datetime"].array[interval])
                        else:
                            # exc > space
                            # partial energy required is supplied by battery
                            bat.drain(space)
                            fat.addConsumption(space, day_df["Datetime"].array[interval])
                    else:
                        # battery not available
                        fat.addConsumption(exc[interval], day_df["Datetime"].array[interval])

        # end of month

        # save battery drained and stored values for info/debug later
        fat.setBatteryTotalDrained(bat.getTotalDrained())
        fat.setBatteryTotalStored(bat.getTotalStored())
        bat.resetTotalDrained()
        bat.resetTotalStored()

        faturas.append(fat)

    return faturas