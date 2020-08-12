from util import Table, BatteryV2H, Fatura

tab = Table()
bat = BatteryV2H('workday')

tab.setCons_kW()
tab.setInjection_kWp(0.5)

months = tab.getMonths()

injection = True

faturas = []

for m in range(0, 12, 1):
    
    fat = Fatura()

    days = tab.getDaysInMonth(m)
    for d in range(0, days, 1):
    
        day_df = tab.getDayInMonth(m, d)

        exc = (day_df["Produção"] - day_df["Consumo"]).array

        for interval in range(0, 96, 1):
            # every 15 min of this day

            if exc[interval] >= 0:
                # produção >= consumo
                
                if bat.isAvailable(day_df["Datetime"].array[interval]):
                    
                    space = bat.getFreeSpaceToStore()

                    if space >= exc[interval]:
                        bat.store(exc[interval])
                    else:
                        # exc > space
                        bat.store(space)
                        remaining = exc - space
                        if injection is True:
                            fat.addInjection(remaining)
                        else:
                            fat.addWaste(remaining)

                else:
                    # battery not available
                    if injection is True:
                        fat.addInjection(exc[interval])
                    else:
                        fat.addWaste(exc[interval])

            else:
                # consumo > produção
                exc[interval] = abs(exc[interval])

                if bat.isAvailable(day_df.array[interval]):
                    space = bat.getFreeSpaceToDrain()

                    if space >= exc[interval]:
                        bat.drain(exc[interval])
                        fat.addConsumption(exc[interval], day_df["Datetime"].array[interval])
                    else:
                        # exc > space
                        bat.drain(space)
                        fat.addConsumption(space, day_df["Datetime"].array[interval])
                else:
                    # battery not available
                    fat.addConsumption(exc[interval], day_df["Datetime"].array[interval])

    # end of month
    faturas.append(fat)
