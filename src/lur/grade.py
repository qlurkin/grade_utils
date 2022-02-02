import pandas as pd
import numpy as np

def load_from_csv(path):
    dt = pd.read_csv(path, sep=';', dtype={'matricule': object})
    return dt.set_index('matricule')

def fix_matricule(matricule):
    if matricule.startswith('195'):
        return '19' + matricule[3:]
    return matricule

def load_from_claco_csv(path):
    df = pd.read_csv(path, delimiter=';')
    df['matricule'] = df['username'].str.split('@', expand=True)[0]
    df['name'] = df['firstname'] + " " + df['lastname']
    df['grade'] = df['score'] / df['total_score_on']
    df = df[['matricule', 'name', 'grade']]
    df['matricule'] = df['matricule'].map(fix_matricule, na_action='ignore')
    df = df.dropna(subset=['matricule'])
    df = df.set_index('matricule')
    return df

def capwords(S):
    return ' '.join([w.capitalize() for w in S.split(' ')])

def save(df, path):
    df.to_json(path, indent=4, force_ascii=False)

def combine(**kwargs):
    res = pd.DataFrame()
    for df in kwargs.values():
        res = res.combine_first(df[['name']])
    for name, df in kwargs.items():
        res[name] = df['grade']
    return res.fillna(0.0)