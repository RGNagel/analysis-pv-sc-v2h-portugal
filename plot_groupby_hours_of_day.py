from util import Table, BatteryV2H, Bill
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

tab = Table()
tab.setCons_kW()
tab.setInjection_kWp(0.5)

year.groupby(year['Datetime'].dt.hour).sum().plot(kind='bar')

plt.show()