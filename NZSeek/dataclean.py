import pandas as pd
import numpy as np

pd.set_option('display.max_colwidth', None)

DICT_AREA_INDEX = {'Admin': 3, 'Banking': 3, 'Education': 3, 'Manufacture': 3}
DICT_DATE_INDEX = {'Admin': 4, 'Banking': 5, 'Education': 5, 'Manufacture': 5}
DICT_CLASSFICATION_INDEX = {'Admin': 5, 'Banking': 6, 'Education': 6, 'Manufacture': 6}
DICT_SALARY_FLOOR = {'Admin': 35000, 'Banking': 53000, 'Education': 48000, 'Manufacture': 24600}
DICT_SALARY_CEILING = {'Admin': 55000, 'Banking': 85000, 'Education': 79000, 'Manufacture': 116000}
DICT_DUPLICATE_INDEX = {'Banking': 4, 'Education': 4, 'Manufacture': 4}
LIST_DUPLICATE = ['Banking', 'Education', 'Manufacture']
LOCATION_INDEX = 9
CLASSIFICATION_INDEX = 15
HOUR_SALARY_TO_ANNUAL = 8 * 200


def deduplication(x):
    # deduplication of str
    trim = x.strip()
    index = (trim + trim).find(trim, 1)
    if index != -1:
        return trim[:index]


def apply_salary(x):
    if 'classification:' in x:
        return 'unknown'
    else:
        return x


def apply_classification(x):
    if 'classification' in x:
        return x[CLASSIFICATION_INDEX:]
    else:
        return 'unknown'


def apply_posted_time(x):
    if 'd' in x:
        return -int(x[:-1])
    else:
        return 0


def clean_area(df, area_index):
    df[area_index] = df[area_index].str.split(',', expand=True)[0]
    df[['location', 'area']] = df[area_index].str.split('area:', expand=True)
    df['location'] = df['location'].apply(lambda x: x[LOCATION_INDEX:])
    df['location'] = df['location'].apply(deduplication)
    df['area'].fillna(value='unknown', inplace=True)
    df['area'] = df['area'].apply(deduplication)
    return df


def clean_classification(df, classification_index):
    df[['subclassification', 'classification']] = df[classification_index].str.split('subClassification:', n=1,
                                                                                     expand=True)
    df['classification'].fillna('unknown', inplace=True)
    df['classification'] = df['classification'].apply(deduplication)
    df['salary'] = df['subclassification'].apply(apply_salary)
    df['subclassification'] = df['subclassification'].apply(apply_classification)
    df[['classification1', 'classification2', 'classification3']] = df['subclassification'].str.split('&', n=2,
                                                                                                      expand=True).fillna(
        'unknown')
    return df


def clean_posted_date(df, posted_date_index):
    df[['posted time', 'featurned at']] = df[posted_date_index].str.split(',', expand=True)[[0, 2]]
    df['featurned at'].fillna('unknown', inplace=True)
    df['posted time'] = df['posted time'].str.extract('(\d+[a-z])')
    df['posted time'].fillna('unknown', inplace=True)
    df['posted time'] = df['posted time'].astype('string')
    df['posted time'] = df['posted time'].apply(apply_posted_time)
    return df


def clean_salary(df, salary_floor, salary_ceiling):
    df['salary'] = df[df['salary'].str.contains('\d', na=False)]['salary'].str.replace(' to ', '-', regex=True)
    df['salary'] = df[df['salary'].str.contains('\d', na=False)]['salary'].str.replace('\d\%', '', regex=True)
    df['salary'] = df[df['salary'].str.contains('\d', na=False)]['salary'].str.replace(',', '', regex=True)
    df['salary'] = df[df['salary'].str.contains('\d', na=False)]['salary'].str.replace(' ', '', regex=True)
    df['salary'].fillna('unknown', inplace=True)
    df[['low_salary', 'high_salary']] = df['salary'].str.split('-', n=1, expand=True).fillna('unknown')
    df['low_salary'] = df['low_salary'].str.extract('(\d+\.\d+|\d+ \d+|\d+k|\d+)')
    df['high_salary'] = df['high_salary'].str.extract('(\d+\.\d+|\d+ \d+|\d+k|\d+)')
    df['low_salary'] = df[df['low_salary'].str.contains('\d', na=False)]['low_salary'].str.replace('k', '000',
                                                                                                   regex=True)
    df['high_salary'] = df[df['high_salary'].str.contains('\d', na=False)]['high_salary'].str.replace('k', '000',
                                                                                                      regex=True)
    df['low_salary'] = df['low_salary'].fillna('unknown')
    df['high_salary'] = df['high_salary'].fillna('unknown')
    df.loc[df['low_salary'] == 'unknown', 'low_salary'] = df['high_salary']
    df.loc[df['high_salary'] == 'unknown', 'high_salary'] = df['low_salary']

    ##set random salary
    for r, row in enumerate(df['low_salary'].values):
        if row == 'unknown':
            df['low_salary'][r] = np.random.randint(salary_floor, salary_ceiling, size=1)[0]

    for r, row in enumerate(df['high_salary'].values):
        if row == 'unknown':
            df['high_salary'][r] = max(np.random.randint(salary_floor, salary_ceiling, size=1)[0], df['low_salary'][r])

    df['low_salary'] = df['low_salary'].astype('float32')
    df['high_salary'] = df['high_salary'].astype('float32')
    df.loc[df['low_salary'] < 50, 'low_salary'] = df['low_salary'] * HOUR_SALARY_TO_ANNUAL
    df.loc[df['high_salary'] < 50, 'high_salary'] = df['high_salary'] * HOUR_SALARY_TO_ANNUAL

    return df


def clean_redundancies(df, job_name):
    df.rename(columns={0: 'Job title', 1: 'website', 2: 'company name'}, inplace=True)
    df['company name'].fillna(df['featurned at'], inplace=True)
    df['company name'] = df['company name'].str.replace('at ', '', regex=True)
    # Drop unuseful columns
    df.drop(DICT_AREA_INDEX[job_name], axis=1, inplace=True)
    df.drop(DICT_DATE_INDEX[job_name], axis=1, inplace=True)
    df.drop(DICT_CLASSFICATION_INDEX[job_name], axis=1, inplace=True)
    df.drop('subclassification', axis=1, inplace=True)
    df.drop('featurned at', axis=1, inplace=True)

    if job_name in LIST_DUPLICATE:
        df.drop(DICT_DUPLICATE_INDEX[job_name], axis=1, inplace=True)
    return df


def clean_jobs(path, job_name):
    df = pd.read_excel(path, header=None)
    df = clean_area(df, DICT_AREA_INDEX[job_name])
    df = clean_posted_date(df, DICT_DATE_INDEX[job_name])
    df = clean_classification(df, DICT_CLASSFICATION_INDEX[job_name])
    df = clean_salary(df, DICT_SALARY_FLOOR[job_name], DICT_SALARY_CEILING[job_name])
    df = clean_redundancies(df, job_name)
    return df


df_admin = clean_jobs("NZ_Admin_JOBS.xlsx", 'Admin')
df_admin['Domain'] = 'Admin'
# df_banking['Domain'] = 'Banking'
# df_manufacture['Domain'] = 'Manufacture'
# df_education['Domain'] = 'Education'
# result_df = pd.concat([df_admin, df_banking, df_manufacture,df_education], ignore_index=True, sort=False)
df_admin_location_count = df_admin.groupby(['location'])["Job title"].count().reset_index(name="count")
df_admin.to_excel('result.xlsx')