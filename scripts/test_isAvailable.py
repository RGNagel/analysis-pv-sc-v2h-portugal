from util import Table, BatteryV2H

tab = Table()

periods = BatteryV2H('workday')

day = tab.getDayInMonth(0, 5)
# ts = day["Datetime"].array(0)

for ts in day["Datetime"].array:
    print(ts.strftime('%a %Y/%m/%d %H:%M:'))

    if periods.isAvailable(ts):
        print("Is available\n")

