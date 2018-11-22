#!/usr/bin/env python3

from sys import argv
import pandas as pd

def aggregate(filename):
    df = pd.read_csv(filename)
    df = df[df['Paid on'] != '---']
    df.set_index(pd.DatetimeIndex(df['Paid on']), inplace=True)
    df1 = df.groupby(pd.Grouper(freq='M')).sum()
    #df1.rename({'Credit (€)': 'credit', 'Debit (€)': 'debit'}, inplace=True, axis=1)
    return df1


def format(df):
    print(df.index[0].strftime('%Y-%m-%d  Monatsabrechnung LinkedFinance'))
    try:
        print('  Einnahmen:Zinsen:p2p:LinkedFinance                 € {:>8.2f}  ; Interest Earned'.format(- df['Interest Earned'].iloc[0]))
    except KeyError:
        pass
    try:
        print('  Ausgaben:Finanzen:LinkedFinanceGebühren            € {:>8.2f}  ; Lender Fee'.format(df['Lender Fee'].iloc[0]))
    except KeyError:
        pass
    try:
        print('  Aktiva:Darlehen:p2p:LinkedFinance                  € {:>8.2f}  ; Principal Repaid'.format(- df['Principal Repaid'].iloc[0]))
    except KeyError:
        pass
    print('  Aktiva:Darlehen:p2p:LinkedFinance                  € {:>8.2f}  ; Neuanlage (manuell)'.format(0))
    print('  Aktiva:Sparkonten:p2p:LinkedFinance')
    print()


if __name__ == '__main__':
    if len(argv) != 2:
        raise ValueError
    df = aggregate(argv[1])
    format(df)
