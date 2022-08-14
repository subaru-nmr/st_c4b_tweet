import pandas as pd
a=pd.DataFrame([[1,1,1],[2,0,2],[0,3,0]])
a.columns=['F','D','M']
a.index=['Tokyo','Osaka','Nagoya']
print(a)