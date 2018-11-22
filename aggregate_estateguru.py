#!/usr/bin/env python3

from sys import argv
import pandas as pd

STRINGS_DE = {
    'payment_date': 'Zahlungsdatum',
    'cash_flow_status': 'Cashflow-Status',
    'cash_flow_type': 'Cashflow-Typ',
    'approved': 'Genehmigt',
    'amount': 'Betrag',
    'investment_auto': 'Investition(Auto Invest)',
    'referral': 'Empfehlungsbonus',
    'interest': 'Zins',
}

STRINGS_EN = {
    'payment_date': 'Payment Date',
    'cash_flow_status': 'Cash Flow Status',
    'cash_flow_type': 'Cash Flow Type',
    'approved': 'Approved',
    'amount': 'Amount',
    'investment_auto': 'Investment(Auto Invest)',
    'referral': 'Referral',
    'interest': 'Interest',
}

def aggregate(filename, string_translation):
    df = pd.read_csv(filename)
    df.set_index(pd.DatetimeIndex(df[string_translation['payment_date']], dayfirst=True), inplace=True)
    df = df[~df.index.isnull()]
    df = df[df[string_translation['cash_flow_status']] == string_translation['approved']]
    df1 = df.groupby([pd.Grouper(freq='M'), string_translation['cash_flow_type']])[string_translation['amount']].sum()
    return df1


def format(df, string_translation):
    print(df.index.levels[0][0].strftime('%Y-%m-%d  Monatsabrechnung Estateguru'))
    try:
        print('  Einnahmen:Zinsen:p2p:Estateguru                    € {:>8.2f}  ; Interest'.format(- df.loc[(slice(None), string_translation['interest'])].iloc[0]))
    except (pd.core.indexing.IndexingError, KeyError):
        pass
    try:
        print('  Einnahmen:Finanzen:Boni:p2p:EstateGuru             € {:>8.2f}  ; Referral'.format(- df.loc[(slice(None), string_translation['referral'])].iloc[0]))
    except (pd.core.indexing.IndexingError, KeyError):
        pass
    try:
        print('  Aktiva:Darlehen:p2p:Estateguru                     € {:>8.2f}  ; Investment(Auto Invest)'.format(- df.loc[(slice(None), string_translation['investment_auto'])].iloc[0]))
    except (pd.core.indexing.IndexingError, KeyError):
        pass
    print('  Aktiva:Sparkonten:p2p:Estateguru')
    print()


if __name__ == '__main__':
    if len(argv) != 2:
        raise ValueError
    for lang in [STRINGS_DE, STRINGS_EN]:
        try:
            df = aggregate(argv[1], lang)
            format(df, lang)
            break
        except (KeyError, AttributeError):
            pass
