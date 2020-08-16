from util import Table, BatteryV2H, Bill

tab = Table()

day = tab.getDayInMonth(1,0)

day = day['Datetime'].array

for period in day:
    print(period.strftime('%a %Y/%m/%d %H:%M:'))
    if (Bill.isWithinOffpeak(period)):
        print("Iswithin Offpeak")
