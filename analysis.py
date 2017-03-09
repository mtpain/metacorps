import matplotlib.pyplot as plt
import seaborn as sns

from collections import OrderedDict
from datetime import datetime

from export_project_csv import ProjectExporter

dt = datetime

DEFAULT_DATE_RANGES = OrderedDict([
    ('Pre-Debates (September 1 - September 26 6:00 PM)',
        (dt(2016, 9, 1), dt(2016, 9, 26, 6,))),
    ('Between First and Second Debates (September 26 7:30 PM - October 9 6:00 PM)',
        (dt(2016, 9, 26, 7, 30), dt(2016, 10, 9, 6))),
    ('Between Second and Third Debates (October 9 7:30 PM - October 19 6:00 PM)',
        (dt(2016, 10, 9, 7, 30), dt(2016, 10, 19, 6))),
    ('Between Third Debate and Election (October 19 7:30 PM - November 8 11:59 PM)',
        (dt(2016, 10, 19, 7, 30), dt(2016, 11, 8, 11, 59, 59))),
    ('Election to End of November (November 9 12:00 AM - November 30)',
        (dt(2016, 11, 9), dt(2016, 11, 30, 11, 59, 59)))
])


COLUMNS_IN_ORDER = [
    'attack',
    'hit',
    'beat',
    'grenade',
    'slap',
    'knock',
    'jugular',
    'smack',
    'strangle',
    'slug',
]


def get_analyzer(year):
    '''
    Convenience method for creating a newly initialized instance of the
    Analyzer class. Currently the only argument is year since the projects all
    contain a year. In the future we may want to match some other unique
    element of a title, or create some other kind of wrapper to search
    all Project names in the metacorps database.
    '''
    if type(year) is int:
        year = str(year)

    return Analyzer(
        ProjectExporter('Viomet Sep-Nov ' + year).export_dataframe()
    )


class Analyzer:

    def __init__(self, df):
        self.df = df

    def per_network_facet_counts(self,
                                 date_ranges=DEFAULT_DATE_RANGES,
                                 data_method='daily-average'):
        """
        Arguments:
            date_ranges (dict): lookup table of date ranges and their names
        Returns:
            (dict) if distribution, dataframe of density of violence
                words for each date range given in date_ranges. If distribution
                is False, returns non-normalized values.
        """
        counts_df = _count_daily_instances(self.df)

        ret_dict = {}
        for rng_name, date_range in date_ranges.items():
            ret_dict.update(
                {
                    rng_name:
                    _select_range_and_pivot_daily_counts(
                        date_range, counts_df, data_method
                    )
                }
            )

        # we want each underlying dataframe to have the same columns for plots
        _standardize_columns(ret_dict)

        return ret_dict

    def plot_facets_by_dateranges(self,
                                  date_ranges=DEFAULT_DATE_RANGES,
                                  data_method='daily-average',
                                  pdf_output=False):

        nfc = self.per_network_facet_counts(date_ranges, data_method)

        if pdf_output:
            _pdf_plot_facets_by_dateranges(nfc, date_ranges, data_method)
        else:
            _plot_facets_by_dateranges(nfc, date_ranges, data_method)

        plt.tight_layout(w_pad=0.5, h_pad=-0.5)

    def plot_agency_counts_by_dateranges(self,
                                         subj_obj,
                                         date_ranges=DEFAULT_DATE_RANGES,
                                         pdf_output=False):

        ag = self.agency_counts_by_dateranges(subj_obj)

        if pdf_output:
            pass
        else:
            _plot_agency_counts_by_dateranges(ag, subj_obj, date_ranges)

        plt.tight_layout()

    def network_daily_timeseries(self):
        """
        Create a timeseries for every network with each column a facet.

        Arguments: None

        Returns (dict): Dictionary of timeseries as explained in description
        """
        pass

    def agency_counts_by_dateranges(self,
                                    subj_obj,
                                    date_ranges=DEFAULT_DATE_RANGES):
        """
        Arguments:
            subj_obj (str): either 'subjects' or 'objects'

        Returns (dict): dictionary with keys of date ranges as in the
            per-network facet counts. Values are dataframes with
            indexes networks and columns with clinton-object, clinton-subject,
            trump-object, trump-subject. Of course this needs to be generalized
            for 2012, but leave that as a TODO
        """
        counts_df = _count_daily_subj_obj(self.df, subj_obj)

        ret_dict = {}
        for rng_name, date_range in date_ranges.items():
            ret_dict.update(
                {
                    rng_name:
                    _select_range_and_pivot_subj_obj(
                        date_range, counts_df, subj_obj
                    )
                }
            )

        return ret_dict


def _select_range_and_pivot_subj_obj(date_range, counts_df, subj_obj):

    rng_sub = counts_df[
        date_range[0] <= counts_df.start_localtime
    ][
        counts_df.start_localtime <= date_range[1]
    ]

    rng_sub_sum = rng_sub.groupby(['network', subj_obj]).agg(sum)

    ret = rng_sub_sum.reset_index().pivot(
        index='network', columns=subj_obj, values='counts'
    )

    return ret


def _count_daily_subj_obj(df, sub_obj):

    subs = df[['start_localtime', 'network', 'subjects', 'objects']]

    subs.subjects = subs.subjects.map(lambda s: s.strip().lower())
    subs.objects = subs.objects.map(lambda s: s.strip().lower())

    try:
        trcl = subs[
            (subs[sub_obj].str.contains('hillary clinton') |
             subs[sub_obj].str.contains('donald trump')) &
            subs[sub_obj].str.contains('/').map(lambda b: not b) &
            subs[sub_obj].str.contains('campaign').map(lambda b: not b)
        ]
    except KeyError:
        raise RuntimeError('sub_obj must be "subjects" or "objects"')

    c = trcl.groupby(['start_localtime', 'network', sub_obj]).size()

    ret_df = c.to_frame()
    ret_df.columns = ['counts']
    ret_df.reset_index(inplace=True)

    # cleanup anything like 'republican nominee'
    ret_df.loc[
        :, sub_obj
    ][

        ret_df[sub_obj].str.contains('donald trump')

    ] = 'donald trump'

    ret_df.loc[
        :, sub_obj
    ][

        ret_df[sub_obj].str.contains('hillary clinton')

    ] = 'hillary clinton'

    return ret_df


def _standardize_columns(df_dict):

    cols = set()
    for df in df_dict.values():
        cols.update(df.columns)

    for idx, df in enumerate(df_dict.values()):
        for c in cols:
            if c not in df.columns:
                df[c] = 0.0

    # for some reason can't do this in loop above and must use key
    for k in df_dict:
        df_dict[k] = df_dict[k][COLUMNS_IN_ORDER]


def _pdf_plot_facets_by_dateranges(nfc, date_ranges, data_method):
    pass


def _plot_agency_counts_by_dateranges(ag, subj_obj, date_ranges):

        sns.set(style="white", context="talk")
        sns.set_palette(sns.color_palette(["#e74c3c", "#34495e"]))

        max_y = 0.0
        for df in ag.values():
            max_y = max(max_y, df.max().max())

        print(max_y)

        fig, axes = plt.subplots(
            figsize=(7, 9.5), ncols=1, nrows=len(list(ag.keys()))
        )

        for i, k in enumerate(date_ranges.keys()):

            ag[k].plot(kind='bar', ax=axes[i], rot=0., legend=False)
            axes[i].set_title(k)
            axes[i].set_ylim([0.0, max_y + 5])

            axes[i].set_xlabel('')
            axes[i].yaxis.grid()

        legend = axes[0].legend(
                loc='upper center', borderaxespad=0.,
                ncol=5, prop={'size': 12},
                frameon=True
        )

        sns.despine(left=True)

        legend.get_frame().set_facecolor('0.95')
        legend.get_frame().set_linewidth(1.5)

        if subj_obj == 'objects':
            title = 'Object of metaphorical violence'
        elif subj_obj == 'subjects':
            title = 'Subject of metaphorical violence'

        fig.suptitle(title, fontsize=22)


def _plot_facets_by_dateranges(nfc, date_ranges, data_method):

    max_y = 0.0
    for df in nfc.values():
        max_y = max(max_y, df.max().max())

    fig, axes = plt.subplots(
        figsize=(7, 9.5), ncols=1, nrows=len(list(nfc.keys()))
    )

    for i, k in enumerate(date_ranges.keys()):
        nfc[k].plot(kind='bar', ax=axes[i], rot=0., legend=False)
        # sns.barplot(data=nfc[k], ax=axes[i])
        axes[i].set_title(k)
        axes[i].set_ylim([0.0, max_y + 0.25])

        if data_method == 'distribution':
            axes[i].set_ylabel('relative usage')
        elif data_method == 'daily-average':
            axes[i].set_ylabel('Average Daily Usage')

        axes[i].set_xlabel('')
        axes[i].yaxis.grid()

    legend = axes[0].legend(
            loc='upper center', borderaxespad=0., ncol=5, prop={'size': 12},
            frameon=True
    )

    sns.despine(left=True)

    legend.get_frame().set_facecolor('0.95')
    legend.get_frame().set_linewidth(1.5)


def _count_daily_instances(df):
    """

    """
    subs = df[['start_localtime', 'network', 'facet_word']]

    c = subs.groupby(['start_localtime', 'network', 'facet_word']).size()

    ret_df = c.to_frame()
    ret_df.columns = ['counts']
    ret_df.reset_index(inplace=True)

    return ret_df


def _select_range_and_pivot_daily_counts(date_range, df, data_method):

    # subset only dates in given date range; earlier date assumed first
    rng_sub = df[
        date_range[0] <= df.start_localtime
    ][
        df.start_localtime <= date_range[1]
    ][
        ['network', 'facet_word', 'counts']
    ]

    rng_sub_sum = rng_sub.groupby(['network', 'facet_word']).agg(sum)

    # create pivot table so we can barplot color coded by facet word
    # ret = rng_sub_sum.reset_index().pivot(
    #     index='network', columns='facet_word', values='counts'
    # )
    ret = rng_sub_sum.reset_index().pivot(
        index='network', columns='facet_word', values='counts'
    )

    ret.fillna(0.0, inplace=True)

    # normalize the counts if desired
    if data_method == 'distribution':
        for i in range(len(ret)):
            ret.ix[i] = ret.ix[i] / sum(ret.ix[i])
    # make daily average if desired
    elif data_method == 'daily-average':
        days_list = [
            (el[1] - el[0]).days for el in DEFAULT_DATE_RANGES.values()
        ]
        for i in range(len(ret)):
            ret.ix[i] = ret.ix[i] / float(days_list[i])

    return ret