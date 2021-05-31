import pandas as pd
import numpy as np
import torch as tc
from collections import defaultdict
from Environment.services import core


def load_obs_data():
    df = pd.read_csv(core.CSV_FILE, sep=',')

    # Ordino per data descrescente --> il primo è il più recente
    df = df.sort_values(by='Date', ascending=False)
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y %H:%M:%S')

    # 1 - Range --> (0m, range_obs)
    start_date = df['Date'].iloc[0]
    end_date = start_date - pd.to_timedelta(core.RANGE_OBS, unit='m')
    mask = (df['Date'] <= start_date) & (df['Date'] >= end_date)
    df = df.loc[mask]

    # 2 - Range --> (id, id)
    range = list_duplicates(df['Id'])
    df = df.iloc[range[0]:range[1]]

    # Opzioni -->
    # rimuovere i doppioni nel range_obs
    # nuovo range tra i doppioni e riempo i restanti

    # Tolgo la data
    df = df.drop('Date', axis=1)

    # Aggiungo zeri e tool mancanti
    width = 10 - df.shape[0]
    gz = pd.DataFrame(1.0, index=np.arange(width), columns=['Id', 'Status', 'Sec', 'Res', 'Time'])
    gz['Id'] = [x for x in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] if x not in df['Id'].to_list()]

    # Aggiungo the noise
    gz['Sec'] = np.random.randint(-3, 1, [width, ])
    gz['Res'] = np.random.randint(-3, 0.1, [width, ])
    gz['Time'] = np.random.randint(0, 10, [width, ])

    # Converto a tensor
    df = pd.concat([df, gz])
    df = df.sort_values(by='Id')
    tensor = tc.tensor(df.values)
    return tensor


def list_duplicates(seq):
    tally = defaultdict(list)
    for i, item in enumerate(seq):
        tally[item].append(i)

    min_locs = 100
    l_final = []
    for key, locs in tally.items():
        if len(locs) > 1:
            v_tot = sum(locs)
            if v_tot < min_locs:
                min_locs = v_tot
                l_final = locs[:2]
    return l_final
