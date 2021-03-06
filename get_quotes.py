#!/usr/bin/env python3

__version__ = '0.0.4'

PATH_DB = '/home/andreash/doc/finanzen/ledger/quotedb.h5'
PATH_CSV = '/home/andreash/doc/finanzen/ledger/quotes.ledger'

URL_CONSORS = 'https://www.consorsbank.de/euroWebDe/-?currentpage=financeinfosHome.Desks.searchresult&%24%24event_minisearch=minisearch&%24part=Home.security-search&fieldselector=quote&pattern={}&searchSubmit=Suchen&%24part=financeinfosHome.Desks.searchresult.ev.PageHead.security-search&%24%24%24event_search=search'

URL_TRIODOS = 'https://www.triodos.de/investieren/triodos-aktienaehnliche-rechte'

LEDGERLINE = 'P {date:%Y/%m/%d} {fonds:25} €{price:.2f}  ; retrieved on {now}'

# P 2016/01/23 22:48:23 690004  € 115.06

FONDS = {'LU0458538880': ('FairWorldFonds', 'consors'),
         'DE000A1W2CK8': ('GLSAktienFonds', 'consors'),
         'AT0000815006': ('KeplerEthikfondsA', 'consors'),
         'LU0229773345': ('JSSOekoSar', 'consors'),
         'LU0271656133': ('PioneerGlobalEco', 'consors'),
         'LU0061928585': ('OekoVisionClassic', 'consors'),
         'LU0800346016': ('OekoworldGrowingMarkets', 'consors'),
         'IE0005895655': ('GreenEffects', 'consors'),
         'LU0278272413': ('TriodosSustainableEquity', 'consors'),
         'DE000ETFL474': ('DekaOekomEuroETF', 'consors'),
         'LU0504302604': ('TriodosSustainableMixed', 'consors'),
         'XX000TRIODOS': ('TriodosAktienRechte', 'triodos'),
         }


from datetime import datetime
import logging
import re
import urllib.request

from bs4 import BeautifulSoup
import pandas as pd


def get_triodos(isin):
    r = str(urllib.request.urlopen(URL_TRIODOS).read())
    quote_regex = re.compile('Aktueller Kurs: \d{2},\d{2}')
    quote_regex = re.compile('<h3>Aktueller Kurs</h3><p>\d{2},\d{2}')
    quote_str = quote_regex.findall(r)[0].split(
            '<p>')[1].replace(',', '.')
    quote = float(quote_str)
    date_regex = re.compile('Stand: \d{2}[-/]\d{2}[-/]\d{4}')
    date_str = date_regex.findall(r)[0].split()[1]
    date = datetime.strptime(date_str, '%d-%m-%Y').date()
    return date, quote


def get_consors(isin):
    r = urllib.request.urlopen(URL_CONSORS.format(isin)).read()
    soup = BeautifulSoup(r, 'lxml')
    div = soup.find('div', class_='quote-data')
    pricestr = div.find('strong', class_='price').get_text().strip()
    timestr = div.find('span', class_='time').get_text().strip()
    currstr = div.find('span', class_='currency').get_text().strip()
    date = datetime.strptime(timestr.split('\xa0')[1], '%d.%m.%Y').date()
    quote = float(pricestr.replace(',', '.'))
    assert currstr == 'EUR'
    return date, quote


def update_db(quiet=True, firstrun=False):
    log = logging.getLogger('get_fondskurse')
    new = pd.DataFrame(columns=['date', 'isin', 'currency', 'quote',
                                'retrieved_on', 'retrieved_with_version'])

    if not firstrun:
        old = pd.read_hdf(PATH_DB, 'kurse')

    for isin, (name, source) in FONDS.items():

        if source == 'consors':
            get_ = get_consors
        elif source == 'triodos':
            get_ = get_triodos
        else:
            raise ValueError('Cannot determine source function for {} from '
                             'string {}'.format(isin, source))

        try:
            log.info('Getting quote for {}'.format(isin))
            date, quote = get_(isin)
        except Exception:
            log.error('Error while getting quote for {}'.format(isin))
            if not quiet:
                raise
            continue

        # jump to next fonds if we don't need to update
        if not firstrun:
            if old[old['isin'] == isin].date.max() >= pd.Timestamp(date):
                continue

        # write new data to file
        df = pd.DataFrame([[pd.Timestamp(date), isin, 'EUR', quote,
                            pd.Timestamp(datetime.now()), __version__]],
                          columns=['date', 'isin', 'currency', 'quote',
                                   'retrieved_on', 'retrieved_with_version'])
        try:
            df.to_hdf(PATH_DB, 'kurse', append=True)
            new = new.append(df)
        except Exception:
            log.error('Error while writing data for {} to {}'.format(
                              isin, PATH_DB))

    return new


def export_prices(path_db, path_export):
    df = pd.read_hdf(path_db, 'kurse')
    df.sort_values(by=['date', 'isin'], ascending=[False, True], inplace=True)
    txt = []
    txt.append('; generated on {} by get_quotes.py version {}'.format(
            datetime.now().isoformat(), __version__))
    for row in df.itertuples(index=False):
        txt.append(LEDGERLINE.format(date=row.date.date(),
                                     fonds=FONDS[row.isin][0],
                                     price=row.quote,
                                     now=row.retrieved_on.isoformat()))
    txt[-1] += '\n'
    with open(path_export, 'w') as f_:
        f_.writelines('\n'.join(txt))


if __name__ == '__main__':
    log = logging.getLogger('get_fondskurse')
    log.setLevel('INFO')
    update = update_db(quiet=True, firstrun=False)
    log.info('The following data have been updated:', update)
    export_prices(PATH_DB, PATH_CSV)
