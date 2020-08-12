from util import Table, BatteryV2H, Fatura, getFaturasYear

injection = True
profile = 'workday'
kWp = 0.5

faturas = getFaturasYear(injection, profile, kWp)

print(f"Injection={injection}, profile={profile}, kWp={kWp}\n\n")

for f in faturas:
    f.printInfo()


