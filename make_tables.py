import pickle
import os

import pandas as pd

from projects.viomet.analysis import (
    by_network_subj_obj_table, by_network_word_table,
    fit_all_networks, partition_info_table
)
from projects.common import get_project_data_frame

YEARS = [2012, 2016]

FORMATTERS = {
    '$f^g$': '{:,.2f}'.format,
    '$f^e$': '{:,.2f}'.format,
    'totals': lambda n: '{:, d}'.format(int(n)),
    '\% change': '{:,.1f}'.format
}

for year in YEARS:

    print('creating tables for {}'.format(year))

    metaphors_url = \
        'http://metacorps.io/static/data/' \
        'viomet-{}-snapshot-project-df.csv'.format(year)

    iatv_corpus_name = 'Viomet Sep-Nov {}'.format(year)

    viomet_df = get_project_data_frame(metaphors_url)
    date_range = pd.date_range(
        str(year) + '-9-1', str(year) + '-11-30', freq='D'
    )

    # Find the best-fit step-function model. Load from disk if chkpt available.
    fits_path = 'fits{}.pickle'.format(year)
    if os.path.exists(fits_path):
        print('loading model fits for {} from disk'.format(year))
        with open(fits_path, 'br') as f:
            fits = pickle.load(f)
    else:
        print('fitting model for {} and saving to disk'.format(year))
        fits = fit_all_networks(viomet_df, date_range, iatv_corpus_name)
        with open(fits_path, 'wb') as f:
            pickle.dump(fits, f)

    partition_infos = {
        network: fits[network][0]
        for network in ['MSNBCW', 'CNNW', 'FOXNEWSW']
    }

    pi_table = partition_info_table(viomet_df, date_range, partition_infos)
    print(pi_table)
    with open('Table1-{}.tex'.format(year), 'w') as f:
        pi_table.to_latex(f, escape=False,
                          formatters=FORMATTERS)

    net_word = by_network_word_table(viomet_df, date_range, partition_infos)
    print(net_word)
    with open('Table2-{}.tex'.format(year), 'w') as f:
        net_word.to_latex(f, formatters=FORMATTERS, escape=False)

    if year == 2012:
        subjects = ['Barack Obama', 'Mitt Romney']
        objects = ['Barack Obama', 'Mitt Romney']
    elif year == 2016:
        subjects = ['Hillary Clinton', 'Donald Trump']
        objects = ['Hillary Clinton', 'Donald Trump']
    net_subobj = by_network_subj_obj_table(
        viomet_df, date_range, partition_infos,
        subjects=subjects, objects=objects
    )
    print(net_subobj)
    with open('Table3-{}.tex'.format(year), 'w') as f:
        net_subobj.to_latex(f, formatters=FORMATTERS, escape=False)
