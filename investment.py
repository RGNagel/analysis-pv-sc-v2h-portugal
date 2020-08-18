from util import Investment, BatteryV2H
import numpy as np
import pandas as pd

batteries = [
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

kwps = [0.5, 0.75, 1.5, 3.45]

injections = [True, False]

tables = {}

for kwp in kwps:
    tables[kwp] = {
        'grid injection': [],
        'V2H occupied periods': [],
        'NPV': [],
        'IRR': [],
        'PI': [],
        'DPP': [],
        'LCOE': []
    }
    # for with and without injection
    for inj in injections:
        for b in batteries:
            bat  = b['bat']
            desc = b['desc']

            investment = Investment(25, kwp, inj, bat)

            tables[kwp]['grid injection'].append(inj)
            desc = desc.replace("\n", " ")
            tables[kwp]['V2H occupied periods'].append(desc)
            NPV  = investment.getNPV()
            IRR  = investment.getIRR()
            PI   = investment.getPI()
            DPP  = investment.getDPP()
            # if DPP < 0:
            #     DPP = '>25'
            LCOE = investment.getLCOE()
            tables[kwp]['NPV'].append(NPV)
            tables[kwp]['IRR'].append(IRR)
            tables[kwp]['PI'].append(PI)
            tables[kwp]['DPP'].append(DPP)
            tables[kwp]['LCOE'].append(LCOE)
            
    # get df and export to .xls
    df = pd.DataFrame(data=tables[kwp])

    kwp_fmt = str(kwp).replace(".", "_")
    filename = f"results/{kwp_fmt}.xls"

    df.to_excel(excel_writer=filename, 
                float_format="%.4f",
                index=False)

    filename = f"results/{kwp_fmt}.tex"
    caption  = f"Economical parameter for {kwp} kWp setup"
    label    = f"tab:results-{kwp}"
    df.to_latex(buf=filename, 
                float_format="%.4f",
                index=False,
                caption=caption,
                label=label)
    