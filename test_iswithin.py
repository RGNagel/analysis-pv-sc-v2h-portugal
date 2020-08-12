from util import Table, WeekPeriods

tab = Table()

periods = WeekPeriods('weekend')

day = tab.getDayInMonth(0, 4)
# ts = day["Datetime"].array(0)

for ts in day["Datetime"].array:
    print(ts.strftime('%a: %Y/%m/%d %H:%M'))

    if periods.isWithin(ts):
        print("isWithin")


