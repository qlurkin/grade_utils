import pandas as pd
import numpy as np

def load_grade(path):
	dt = pd.read_csv(path, sep=';', dtype={'matricule': object})
	return dt.set_index('matricule')

def capwords(S):
	return ' '.join([w.capitalize() for w in S.split(' ')])