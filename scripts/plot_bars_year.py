from util import Table, BatteryV2H, Bill, getMonthlyBillsOfYear
import numpy as np
import matplotlib.pyplot as plt

injection = True
kWp = 3.45

dict_bats = [
    {
        'bat': BatteryV2H(always=True),
        'desc': "always\navailable"
    },
    {
        'bat': BatteryV2H('weekend'),
        'desc': "sat-sun\n6:00-24:00"
    },
    {
        'bat': BatteryV2H('workday_afternoon'),
        'desc': "mon-fri\n13:00-18:00"
    },
    {
        'bat': BatteryV2H('workday_evening'),
        'desc': "mon-fri\n18:00-23:00"
    },
    {
        'bat': BatteryV2H('workday_morning'),
        'desc': "mon-fri\n8:00-13:00"
    },
    {
        'bat': BatteryV2H('workday'),
        'desc': "mon-fri\n8:00-18:00"
    },
    {
        'bat': BatteryV2H(never=True),
        'desc': "not available"
    },
]

x = list(map(lambda obj : obj['desc'], dict_bats))
y = []
# Position of bars on x-axis

for i in range(0, len(dict_bats), 1):
    bat = dict_bats[i]['bat']
    desc = dict_bats[i]['desc']

    [bills, billsNoPV] = getMonthlyBillsOfYear(injection, kWp, bat)
    finalValuesNoPV = list((map(lambda bill : bill.getFinalValue(), billsNoPV)))
    finalValues     = list((map(lambda bill : bill.getFinalValue(), bills)))
    diff = np.array(finalValuesNoPV) - np.array(finalValues)

    y.append(np.average(diff))

    # plt.bar(positions + i * bar_width, diff, bar_width, tick_label=months, label=desc)


plt.bar(x,y)
# plt.xticks(rotation='vertical')

plt.title(f"Average monthly savings with PV system of {kWp} kWp {'with injection' if injection else 'without injection'}")
plt.xlabel('Period in which the vehicle (V2H) is being used or occupied')
plt.ylabel('EUR')
plt.legend()
plt.show()