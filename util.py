from pandas import DataFrame, read_csv
import pandas as pd
import numpy as np
import numpy_financial as npf

class Table:
    CONS_AVG_CLIENT_KWH = 3506.00
    
    @staticmethod
    def PROD_AVG_CLIENT_KWH(kWp, e, hours):
        # src: https://www.sciencedirect.com/science/article/abs/pii/S1364032119301881
        return hours * kWp * (1 - e)

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
        self.table['Consumo'] = self.table['Consumo'] * Table.CONS_AVG_CLIENT_KWH / 1000

    def setInjection_kWp(self, power_kWp):
        prod = Table.PROD_AVG_CLIENT_KWH(power_kWp, 0.18, 1600)
        self.table['Produção'] = self.table['Produção'] * prod / 1000

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
            raise Exception(f"charge level below minimum {self._getMinimumChargeLevel()}")

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

        # TODO: handle 00:00 as not available if it is within. This is an issue related to the day changing            

        # filter = data['week_num'] == ts.dayofweek
        # row = self.df.where(filter)
        row = self.df[ts.dayofweek : ts.dayofweek + 1]

        hh = ts.hour + ts.minute / 60
        begin = row['begin'].array[0]
        end = row['end'].array[0]

        # standard NaN is the only value which returns false in a comparison with itself
        def isnan(x):
            return x != x

        if isnan(begin) and isnan(end):
            # the cells are empty which means vehicle is not being used
            return True

        if isnan(begin) and not isnan(end):
            raise Exception("Begin is nan but End is not. Wrong xls input.\n")
        if not isnan(begin) and isnan(end):
            raise Exception("End is nan but Begin is not. Wrong xls input.\n")
        if begin == end:
            raise Exception("Begin is equal to End.\n")
        if begin == 24 or end == 24:
            raise Exception("24 is not a valid hour. Use 00 instead.\n")

        iswithin = False

        if begin < end:
            if hh > begin and hh <= end:
                iswithin = True               
        else:
            # begin > end
            iswithin = True
            if hh > end and hh <= begin:
                iswithin = False


        if iswithin == True:
            # Set the charge to the level which will be available when V2H goes home. 
            self._setChargeLevel(self._getMinimumChargeLevel())
            return False
        else:
            return True


    def getTotalStored(self):
        return self._totalStored

    def getTotalDrained(self):
        return self._totalDrained

    def resetTotalStored(self):
        self._totalStored = 0

    def resetTotalDrained(self):
        self._totalDrained = 0


class Bill:
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

        if hh > Bill.OFFPEAK_BEGIN and hh < 24:
            within = True
        elif hh >= 0 and hh <= Bill.OFFPEAK_END:
            within = True

        return within

    def __init__(self):
        # kWh
        self._injection = 0
        self._consumption_peak = 0
        self._consumption_offpeak = 0
        self._waste = 0
        self._batteryTotalStored = 0
        self._batteryTotalDrained = 0

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

class Investment:

    def __init__(self, years, kWp, injection, battery):
        kwps = [0.5, 0.75, 1.50, 3.45]
        if kWp not in kwps:
            raise Exception("kWp value is not valid")

        if injection != True and injection != False:
            raise Exception("Injection is neither True or False")

        if not isinstance(battery, BatteryV2H):
            raise Exception("battery is not BatteryV2H object")

        self._years = years
        self._kWp = kWp
        self._injection = injection
        self._inflows = np.zeros(years)
        self._outflows = np.zeros(years)

        self._discount_rate_Y = 0.04
        self._discount_rate_M = (1 + self._discount_rate_Y) ** (1 / 12) - 1
        self._depreciation = 0.075 # 0.75%/ano
        # maintenance & ops costs
        self._maintenance_ops = 0.01 # 1% of total investiment

        self._addEquipmentCosts(self._kWp)
        self._addTaxCosts(self._kWp, self._injection)

        self._addBillIncome(injection, kWp, battery)

        # after all costs and incomes calculated:
        self._addMaintenanceAndOpsCosts()
        self._flows = self._inflows - self._outflows

        if self._flows[0] >= 0:
            raise Exception("Year 0 has positive income. How?")

    def _addMaintenanceAndOpsCosts(self):

        for y in range(1, self._years, 1):
            # total costs until year y
            cost = np.sum(self._outflows[0:y])
            self.addOutflow(y, cost * self._maintenance_ops)

    @staticmethod
    def futureValue(rate, cashflow):
        factor = 1 + rate
        fv = 0
        n = len(cashflow)
        for i in range(0, n, 1):
            fv = fv + cashflow[i] * factor ** (n - i)

        return fv

    # def getAnnualIncome(self): 
    #     return Investment.futureValue(self._discount_rate_M, income)
    
    def _addBillIncome(self, injection, kWp, battery):
        [bills, billsNoPV] = getMonthlyBillsOfYear(injection, kWp, battery)

        finalValuesNoPV = list((map(lambda bill : bill.getFinalValue(), billsNoPV)))
        finalValues     = list((map(lambda bill : bill.getFinalValue(), bills)))
        # savings for every month
        income = np.array(finalValuesNoPV) - np.array(finalValues)
        
        annual_income = Investment.futureValue(self._discount_rate_M, income)

        for y in range(1, self._years, 1):
            self.addInflow(y, annual_income)

    def getNPV(self):
        return npf.npv(self._discount_rate_Y, self._flows)
    
    def getIRR(self):
        return npf.irr(self._flows)

    def getPI(self):
        subflow = self._flows[1 : self._years]
        subflow = np.concatenate([[0], subflow])
        return npf.npv(self._discount_rate_Y, subflow) / abs(self._flows[0])

    def getDPP(self):
        
        value = abs(self._flows[0])
        
        for y in range(1, self._years):
            factor = (1 + self._discount_rate_Y ) ** y
            value = value - self._flows[y] / factor
            if value == 0:
                return y
            elif value < 0:
                value = value + self._flows[y] / factor # undo line above
                # DPP between i and i + 1
                return y + value / self._flows[y] / factor 

        return -1

    def getLCOE(self):
        annual_kwh = Table.CONS_AVG_CLIENT_KWH * np.ones(self._years)
        total_kwh = npf.npv(self._discount_rate_Y, annual_kwh)
        total_cost = npf.npv(self._discount_rate_Y, self._outflows)
        return total_cost / total_kwh

    def printInfo(self):
        print(f"Injection={self._injection} kWp={self._kWp}")

        print(f"NPV    : {self.getNPV() }\n")
        print(f"IRR    : {self.getIRR() }\n")
        print(f"PI     : {self.getPI()  }\n")
        print(f"DPP    : {self.getDPP() }\n")
        print(f"LCOE   : {self.getLCOE()}\n")

    def _checkYear(self, year):
        if year < 0 or year >= self._years:
            raise Exception("year index out of bound")

    def addInflow(self, year, value):
        self._checkYear(year)
        self._inflows[year] = self._inflows[year] + value

    def addOutflow(self, year, value):
        self._checkYear(year)
        self._outflows[year] = self._outflows[year] + value

    def _addEquipmentCosts(self, kWp):
        filename = 'equipment.xls'
        df = pd.read_excel(filename)

        # TODO MAYBE better way to iterate over df?
        for i in range(0, len(df), 1):
            if df['kWp'][i] == kWp:
                # add to year 0
                self.addOutflow(0, df['price'][i])
                # TODO handle salvage value here when duration < 25 years

    def _addTaxCosts(self, kWp, injection):
        """
        src: https://dre.pt/application/file/a/66321064
        every 10 year 20% of initial cost is charged
        """
        tax = 0
        if injection is False and kWp >= 1.5 and kWp <= 5:
            tax = 70
        elif injection is True and kWp <= 1.5:
            tax = 30
        elif injection is True and kWp >= 1.5 and kWp <= 5:
            tax = 100

        self.addOutflow(0, tax)

        self.addOutflow(9, tax * 0.2)
        self.addOutflow(19, tax  * 0.2)

def getMonthlyBillsOfYear(injection, kWp, batteryV2H_obj):

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

    bills = []
    billsNoPV = []

    for m in range(0, 12, 1):
        
        bill = Bill()
        billNoPV = Bill()

        days = tab.getDaysInMonth(m)
        for d in range(0, days, 1):
        
            day_df = tab.getDayInMonth(m, d)

            exc = (day_df["Produção"] - day_df["Consumo"]).array

            for interval in range(0, 96, 1):
                # every 15 min of this day

                billNoPV.addConsumption(day_df["Consumo"].array[interval], 
                                        day_df["Datetime"].array[interval])

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
                                bill.addInjection(remaining)
                            else:
                                bill.addWaste(remaining)

                    else:
                        # battery not available
                        if injection is True:
                            bill.addInjection(exc[interval])
                        else:
                            bill.addWaste(exc[interval])

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
                            # partial or none energy required is supplied by battery
                            bat.drain(space)
                            remaining = exc[interval] - space
                            bill.addConsumption(remaining, day_df["Datetime"].array[interval])
                    else:
                        # battery not available
                        bill.addConsumption(exc[interval], day_df["Datetime"].array[interval])

        # end of month

        # save battery drained and stored values for info/debug later
        bill.setBatteryTotalDrained(bat.getTotalDrained())
        bill.setBatteryTotalStored(bat.getTotalStored())
        billNoPV.setBatteryTotalDrained(0)
        billNoPV.setBatteryTotalStored(0)
        
        bat.resetTotalDrained()
        bat.resetTotalStored()

        bills.append(bill)
        billsNoPV.append(billNoPV)

    return [bills, billsNoPV]