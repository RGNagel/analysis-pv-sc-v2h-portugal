from util import Table, BatteryV2H, Bill, getMonthlyBillsOfYear
import numpy as np
import matplotlib.pyplot as plt

injection = True

dict_bats = [
    {
        'bat': BatteryV2H(always=True),
        'desc': "always\navailable"
    },
    {
        'bat': BatteryV2H('weekend'),
        'desc': "sat-sun\n6:00-24:00"
    },
    # {
    #     'bat': BatteryV2H('workday_afternoon'),
    #     'desc': "mon-fri\n13:00-18:00"
    # },
    # {
    #     'bat': BatteryV2H('workday_evening'),
    #     'desc': "mon-fri\n18:00-23:00"
    # },
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
    #     'desc': "not available"
    # },
]

x = list(map(lambda obj : obj['desc'], dict_bats))
y = {
    3.45: [],
    1.50: [],
    0.75: [],
    0.5: [],
}

positions = np.arange(0, len(dict_bats))

for i in range(0, len(dict_bats), 1):
    bat = dict_bats[i]['bat']
    desc = dict_bats[i]['desc']

    for kwp in y:
        [bills, billsNoPV] = getMonthlyBillsOfYear(injection, kwp, bat)    
        finalValuesNoPV = list((map(lambda bill : bill.getFinalValue(), billsNoPV)))
        finalValues     = list((map(lambda bill : bill.getFinalValue(), bills)))
        diff = np.array(finalValuesNoPV) - np.array(finalValues)
        y[kwp].append(np.average(diff))


bar_width = 0.10
plt.bar(positions, y[0.5]  , bar_width, tick_label=x, label=desc)
plt.bar(positions, y[0.75] , bar_width, tick_label=x, label=desc)
plt.bar(positions, y[1.50] , bar_width, tick_label=x, label=desc)
plt.bar(positions, y[3.45] , bar_width, tick_label=x, label=desc)


# plt.bar(x, y)
# plt.xticks(rotation='vertical')

plt.title(f"Average monthly savings {'with injection' if injection else 'without injection'}")
plt.xlabel('Period in which the vehicle (V2H) is being used or occupied')
plt.ylabel('EUR')

legend = list(map(lambda x : str(x) + ' kWp', y))
plt.legend(legend)
plt.show()