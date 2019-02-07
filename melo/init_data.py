# -*- coding: utf-8 -*-


import pandas as pd
from pathlib import Path


DEFAULT_ELO = 1300


def init_data(players, output_path):
    df = pd.DataFrame({'player': players})
    df['elo'] = DEFAULT_ELO
    df['games'] = 0
    df['loss'] = 0
    df['win'] = 0
    df['draw'] = 0
    df.to_csv(output_path, index=False)





if __name__ == "__main__":
    # Generate initial data
    players = ["yassine", "gaetan", "paul", "theo", "thomas"]
    output_path = Path(__file__).absolute().parent.joinpath('data', 'melo.csv')
    init_data(players, output_path)
    output_path = Path(__file__).absolute().parent.joinpath('data', 'test_melo.csv')
    init_data(players, output_path)
