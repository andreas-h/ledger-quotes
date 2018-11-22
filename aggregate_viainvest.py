#!/usr/bin/env python3

from sys import argv
import pandas as pd

def aggregate(filename):
    df = pd.read_excel(filename)
    df.set_index(pd.DatetimeIndex(df['Transaction date']), inplace=True)
    df1 = df.groupby([pd.Grouper(freq='M'), 'Transaction type']).sum()
    df1.rename({'Credit (€)': 'credit', 'Debit (€)': 'debit'}, inplace=True, axis=1)
    return df1


def format(df):
    print(df.index.levels[0][0].strftime('%Y-%m-%d  Monatsabrechnung VIAINVEST'))
    try:
        print('  Einnahmen:Zinsen:p2p:VIAINVEST                     € {:>8.2f}  ; Amount of interest payment received'.format(- df.loc[(slice(None), 'Amount of interest payment received'), :].credit.iloc[0]))
    except KeyError:
        pass
    try:
        print('  Aktiva:Darlehen:p2p:VIAINVEST                      € {:>8.2f}  ; Amount of principal repayment received'.format(- df.loc[(slice(None), 'Amount of principal repayment received'), :].credit.iloc[0]))
    except KeyError:
        pass
    try:
        print('  Aktiva:Darlehen:p2p:VIAINVEST                      € {:>8.2f}  ; Amount invested in loan'.format(df.loc[(slice(None), 'Amount invested in loan'), :].debit.iloc[0]))
    except KeyError:
        pass
    try:
        print('  Ausgaben:Finanzen:Steuern:VIAINVEST                € {:>8.2f}  ; Amount of Withholding Tax deducted'.format(df.loc[(slice(None), 'Amount of Withholding Tax deducted'), :].debit.iloc[0]))
    except KeyError:
        pass
    print('  Aktiva:Sparkonten:p2p:VIAINVEST')
    print()


if __name__ == '__main__':
    if len(argv) != 2:
        raise ValueError
    df = aggregate(argv[1])
    format(df)
