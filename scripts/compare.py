from util import Table, BatteryV2H, Bill, getMonthlyBillsOfYear
import numpy as np
import matplotlib.pyplot as plt

kwp = 0.75

batteries = [
    # {
    #     'bat': BatteryV2H(always=True),
    #     'desc': "always\navailable"
    # },
    # {
    #     'bat': BatteryV2H('weekend'),
    #     'desc': "sat-sun\n6:00-24:00"
    # },
    # {
    #     'bat': BatteryV2H('workday_afternoon'),
    #     'desc': "mon-fri\n13:00-18:00"
    # },
    {
        'bat': BatteryV2H('workday_evening'),
        'desc': "mon-fri\n18:00-23:00"
    },
    # {
    #     'bat': BatteryV2H('workday_morning'),
    #     'desc': "mon-fri\n8:00-13:00"
    # },
    # {
    #     'bat': BatteryV2H('workday'),
    #     'desc': "mon-fri\n8:00-18:00"
    # },
    # {
    #     'bat': BatteryV2H(never=True),
    #     'desc': "not\navailable"
    # },
]


for b in batteries:
    bat   = b['bat']
    desc  = b['desc']

    for injection in [True, False]:

        [bills, billsNoPV] = getMonthlyBillsOfYear(injection, kwp, bat)
        cons_peak = 0
        cons_offpeak = 0
        inj = 0
        waste = 0
        bat_stored = 0
        bat_drained = 0

        for bill in bills:
            cons_peak    += bill.getConsumptionPeak()
            cons_offpeak += bill.getConsumptionOffpeak()
            inj          += bill.getInjection()
            waste        += bill.getWaste()
            bat_stored   += bill.getBatteryTotalStored()
            bat_drained  += bill.getBatteryTotalDrained()
        
        print("\n")
        print(f"Profile           : {desc}")
        print(f"Injection         : {injection}")
        print(f"power             : {kwp}")
        print("\n")
        print(f"Cons peak         : {cons_peak}")
        print(f"Cons offpeak      : {cons_offpeak}")
        print(f"inj               : {inj}")
        print(f"waste             : {waste}")
        print(f"bat stored        : {bat_stored}")
        print(f"bat drained       : {bat_drained}")

