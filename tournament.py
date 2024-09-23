# importing the modules
from IPython.display import display
import pandas as pd
import odi
from utils import HiddenPrints

# 4 levels = 1: Match, 2: Inning, 3: Team/Rain/Inning/Target, 4: Team name etc.
matches = []

# creating a table DataFrame
df = pd.DataFrame(columns=['', 'Pld', 'Won', 'Lost', 'NR', 'Pts', 'NRR', 'RunsFor', 'OversFor', 'RunsAgainst', 'OversAgainst'])
df['NRR'] = df['NRR'].astype(float)
df['RunsFor'] = df['RunsFor'].astype(float)
df['OversFor'] = df['OversFor'].astype(float)
df['RunsAgainst'] = df['RunsAgainst'].astype(float)
df['OversAgainst'] = df['OversAgainst'].astype(float)

# print(df.dtypes)

# generate matches by suppressing print statements
# with HiddenPrints():
matches.append(odi.getScoreVerbose(["England", 10],["South Africa", 8], rain_prob = 1, pitch_mod = 6))

for match in matches:

  # overs lost due to rain in the first and second innings
  r = []

  # update rain
  r.append(match[0][1][5]) if match[0][1][5] else r.append(0)
  r.append(match[1][1][5]) if match[1][1][5] else r.append(0)

  ov = float(50-r[0]-r[1])

  # add the team to the table if it does not already exist
  if match[0][0][0] not in df[''].unique():
    df.loc[len(df.index)] = [match[0][0][0], 0, 0, 0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0]
  if match[1][0][0] not in df[''].unique():
    df.loc[len(df.index)] = [match[1][0][0], 0, 0, 0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0]

  # find the team and increase the number of matches played
  df.loc[df[''] == match[0][0][0], 'Pld'] += 1
  df.loc[df[''] == match[1][0][0], 'Pld'] += 1

  if ov >= 20 and match[1][1][4]!= True:
    if match[1][2][0][0] >= match[2]:
      df.loc[df[''] == match[1][0][0], 'Won'] += 1
      df.loc[df[''] == match[0][0][0], 'Lost'] += 1
    else:
      df.loc[df[''] == match[1][0][0], 'Lost'] += 1
      df.loc[df[''] == match[0][0][0], 'Won'] += 1
  else:
      df.loc[df[''] == match[1][0][0], 'NR'] += 1
      df.loc[df[''] == match[0][0][0], 'NR'] += 1

  # find the team and increase the RunsFor and RunsAgainst
  if ov >= 20 and match[1][1][4]!= True:
    df.loc[df[''] == match[0][0][0], 'RunsFor'] += match[2]-1
    df.loc[df[''] == match[0][0][0], 'RunsAgainst'] += match[1][2][0][0]
    df.loc[df[''] == match[1][0][0], 'RunsFor'] += match[1][2][0][0]
    df.loc[df[''] == match[1][0][0], 'RunsAgainst'] += match[2]-1

 
  # find the team and increase the OversFor and OversAgainst
  ov1st = 0
  ov1st = ov if float((match[0][2][0][2]-1)/6) > ov else float((match[0][2][0][2]-1)/6)

  if ov >= 20 and match[1][1][4] != True:
    if match[1][1][2] < 300:
      df.loc[df[''] == match[0][0][0], 'OversFor'] += ov1st if match[0][2][0][1] != 10 else ov
      df.loc[df[''] == match[1][0][0], 'OversAgainst'] += ov1st if match[0][2][0][1] != 10 else ov
      df.loc[df[''] == match[0][0][0], 'OversAgainst'] += float((match[1][2][0][2]-1)/6) if match[1][2][0][1] != 10 else ov
      df.loc[df[''] == match[1][0][0], 'OversFor'] += float((match[1][2][0][2]-1)/6) if match[1][2][0][1] != 10 else ov
    else:
      df.loc[df[''] == match[0][0][0], 'OversFor'] += float((match[1][2][0][2]-1)/6) if match[0][2][0][1] != 10 else ov
      df.loc[df[''] == match[1][0][0], 'OversAgainst'] += float((match[1][2][0][2]-1)/6) if match[0][2][0][1] != 10 else ov
      df.loc[df[''] == match[0][0][0], 'OversAgainst'] += float((match[1][2][0][2]-1)/6) if match[1][2][0][1] != 10 else ov
      df.loc[df[''] == match[1][0][0], 'OversFor'] += float((match[1][2][0][2]-1)/6) if match[1][2][0][1] != 10 else ov
      
# setting the points
df['Pts'] = df.Won * 2 + df.NR * 1
df['NRR'] = (df.RunsFor/df.OversFor) - (df.RunsAgainst/df.OversAgainst)

# displaying the DataFrame after setting the index
table = df[['', 'Pld', 'Won', 'Lost', 'NR', 'Pts', 'NRR', 'RunsFor', 'OversFor', 'RunsAgainst', 'OversAgainst']].copy()
table['NRR'] = table['NRR'].fillna(0)
table.sort_values(['Pts', 'NRR'], ascending = [False, False], inplace = True)
table.reset_index(drop=True, inplace=True)
table.index += 1
display(table.to_string())

# print('England' in df[''].unique())