import pandas as pd
import numpy as np
baseDeDonnees = pd.read_csv("Donnés\DonnesMeteorologiqueSimple2013-2024.csv")
null_prc = baseDeDonnees.apply(pd.isnull).sum()/baseDeDonnees.shape[0]
print(null_prc)