from util import Table, BatteryV2H, Bill, getMonthlyBillsOfYear
import numpy as np
import matplotlib.pyplot as plt

injection = True
kWp = 0.5

dict_bats = [
    {
        'bat': BatteryV2H(always=True),
        'desc': "Always available"
    },{
        'bat': BatteryV2H(never=True),
        'desc': "Never available"
    },{
        'bat': BatteryV2H('workday'),
        'desc': "Workday"
    },{
        'bat': BatteryV2H('workday_morning'),
        'desc': "Morning workday"
    },{
        'bat': BatteryV2H('workday_afternoon'),
        'desc': "Afternoon workday"
    },{
        'bat': BatteryV2H('weekend'),
        'desc': "Weekend"
    }
]

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

# Position of bars on x-axis
positions = np.arange(0, len(months))

bar_width = 0.10

for i in range(0, len(dict_bats), 1):
    bat = dict_bats[i]['bat']
    desc = dict_bats[i]['desc']

    [bills, billsNoPV] = getMonthlyBillsOfYear(injection, kWp, bat)
    finalValuesNoPV = list((map(lambda bill : bill.getFinalValue(), billsNoPV)))
    finalValues     = list((map(lambda bill : bill.getFinalValue(), bills)))
    diff = np.array(finalValuesNoPV) - np.array(finalValues)

    plt.bar(positions + i * bar_width, finalValues, bar_width, tick_label=months, label=desc)

plt.title(f"Monthly savings with PV system of {kWp} kWp {'with injection' if injection else 'without injection'}")
plt.xlabel('Months')
plt.ylabel('EUR')
plt.legend()
plt.show()