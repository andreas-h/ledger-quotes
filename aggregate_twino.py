#!/usr/bin/env python3

from sys import argv
import pandas as pd

def aggregate(filename):
    df = pd.read_excel(filename, skiprows=2)
    df.set_index('Booking Date', inplace=True)
    df1 = df.groupby([pd.Grouper(freq='M'), 'Type', 'Description'])
    return df1['Amount, EUR'].sum()


def format(df):
    print(df.index.levels[0][0].strftime('%Y-%m-%d  Monatsabrechnung TWINO'))
    print('  Einnahmen:Zinsen:p2p:TWINO                         € {:>8.2f}'.format(- df[:, :, 'INTEREST'].sum()))
    print('  Aktiva:Darlehen:p2p:TWINO                          € {:>8.2f}'.format(- df[:, :, 'PRINCIPAL'].sum()))
    print('  Aktiva:Sparkonten:p2p:TWINO')
    print()


if __name__ == '__main__':
    if len(argv) != 2:
        raise ValueError
    df = aggregate(argv[1])
    format(df)
