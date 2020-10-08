from util import Table, BatteryV2H, Bill
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

tab = Table()
# tab.setCons_kW()
# tab.setInjection_kWp(1.5)

year = tab.getTable()

year.groupby(year['Datetime'].dt.hour).sum().plot(kind='bar', figsize=(10,5))
plt.legend(['Consumption', 'Production'])
plt.xlabel('Hours')
# plt.ylabel('kWh')
#plt.rcParams.update({'font.size': 32})

# plt.show()
plt.savefig('figures/cons-inj-hours-day.png', bbox_inches='tight', dpi=500)