import sys
import pandas as pd

df = pd.read_csv(sys.argv[1])
df = df / float(sys.argv[2])
df.to_csv(sys.argv[1], index=False)
