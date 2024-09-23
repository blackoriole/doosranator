import math
import json
import random
import pandas as pd
from utils import keyConvert

# essential variables

rainProb = 1
pitch = 3

# teams

bat1 = []
bat2 = []

# define the latest average score

global G50
G50 = 245 + 10 * pitch

# resources initially available

global R1
R1 = 100
global R2
R2 = 100

# target

global target
target = 0

# reading necessary files

runodds = keyConvert(json.load(open('runodds_odi.json')))
wickodds = keyConvert(json.load(open('wickodds_odi.json')))
dl_se = pd.read_csv('DL.csv')

# incorporating rain

def getRain(inn:int, prob:int, start:int):
  rainProb = prob
  rain_yn = random.choices([0,1],[1-rainProb,rainProb])
  a = 0
  b = 0
  lost = 0
  didit = False
  abandoned = False
  duration = 0
  inn = inn
  if rain_yn[0] == 1:
    didit = True
    a = random.randint(start,300)
    ova = str(int(a/6))+'.'+str(int(a%6))
    b = min(random.randint(a,400),318)
    ovb = str(int(b/6))+'.'+str(int(b%6))
    duration = b-a
  if duration == 0:
    didit = False
    lost = 0
  elif duration > 0 and duration <= 18:
    didit = False
    lost = 0
  elif duration >= 198:
    didit = True
    abandoned = True
    lost = int((duration - 18) / 2) if inn == 1 else duration - 18
  else:
    didit = True
    lost = int((duration - 18) / 2) if inn == 1 else duration - 18
  return [a, lost, a+lost, didit, abandoned, math.ceil(lost/6)]

def getStartResources(ovs:int) -> int:
  balls = ovs*6
  resources = dl_se['0'].loc[300-balls]
  return resources

def getTotalResources(R, lst:list) -> int:
  rint = dl_se[str(lst[1][0])].loc[300-lst[1][1]]
  rstr = dl_se[str(lst[2][0])].loc[300-lst[2][1]]
  resources = R - rint + rstr
  return resources

def scoreInnings(inn_no: int, pitch: int, start: int, end:int, rain:bool, rstart: int, rend: int) -> list:
  pitch = pitch
  iter = start
  balls = 1
  score = 0
  wickets = 0
  interruptions = []
  final = []
  dist = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
  i = inn_no
  rscore = []
  while iter <= end:

    if balls%6 == 0 and (end-iter) < 6:
      balls += 1
      break

    # if it is raining, move on
    if rain == True and iter > rstart and iter <= rend:
      if iter == rstart+1:
        interruptions.append([wickets, end-iter])
        rscore = [score, wickets, balls]
      if iter == rend:
        interruptions.append([wickets, max((end-iter-1),0)])
        if i == 2:
          global R2; global R1; global target; global G50
          R2 = getTotalResources(R2, [[], interruptions[0], interruptions[1]])
          if R1 >= R2:
            target = math.ceil(target * R2/R1)
          else:
            target = math.ceil(target + G50 * (R2-R1)/100)
          # print(R2, target)
      iter += 1
      continue

    # lay down the ground rules and probabilities
    s = math.ceil(iter/6)
    r = list(runodds[i][s].keys())
    p = list(runodds[i][s].values())
    p[0] -= 0.0280 * pitch
    p[1] += 0.0165 * pitch
    p[4] += 0.0090 * pitch
    p[6] += 0.0025 * pitch
    w = [1-wickodds[i][s], wickodds[i][s]]
    w[0] += 0.0004 * pitch
    w[1] -= 0.0004 * pitch

    # has the target already been chased down?
    if i == 2 and score >= target and rend != 300:
      break
    if i == 2 and score >= target and rend == 300 and iter < rstart:
      break

    # check what happens in the delivery
    out = random.choices([0, 1], w)
    if out[0] == 1:
      wickets += 1
    if wickets == 10:
      break
    batscore = random.choices(r, p)[0]
    dist[batscore] += 1
    score += batscore

    balls += 1
    iter += 1
  final.append([score, wickets, balls])
  if interruptions:
    final.append(interruptions[0])
    if len(interruptions) >= 2:
      final.append(interruptions[1])
    else:
      final.append([0, 0])
    final.append(rscore)
  else:
    final.append([])
    final.append([])
    final.append([])
  final.append(dist)
  return final

##### SCORINATE THE MATCH! #####

def getScoreVerbose(entry1:list, entry2: list, rain_prob: float, pitch_mod:float) -> list:

  global rainProb; global pitch
  rainProb = rain_prob
  pitch = pitch_mod

  global team1; global team2; global bat1; global bat2

  team1 = entry1
  team2 = entry2

  # decide who bats first

  if random.randint(0,1)==0:
    bat1 = team1
    bat2 = team2
  else:
    bat1 = team2
    bat2 = team1

  global R2; global R1; global target; global G50

  r1 = getRain(1, rainProb, 1)

  print("1ST INNINGS:", bat1[0])
  # print(r1)
  inning1 = scoreInnings(1, pitch, 1, 300, r1[3], r1[0], r1[2])

  target = inning1[0][0]

  if r1[3] == True:
    if inning1[3]:
      time = math.ceil((r1[1]+18)*0.75)
      if time >= 60:
        print(math.floor(time/60), "hour(s)", time%60, "min(s) of rain after", str(inning1[3][0])+"/"+str(inning1[3][1]), "in", str(math.floor((inning1[3][2]-1)/6))+'.'+str((inning1[3][2])%6), "over(s).", r1[5], "over(s) lost per innings.")
      else:
        print(time, "min(s) of rain after", str(inning1[3][0])+"/"+str(inning1[3][1]), "in", str(math.floor((inning1[3][2]-1)/6))+'.'+str((inning1[3][2])%6), "over(s).", r1[5], "over(s) lost per innings.")
      R1 = getTotalResources(100, inning1)
      R2 = getStartResources(50-r1[5])
    if r1[5] == 0:
      print("A slight drizzle did not cause any loss of overs.")

  print("Total:", str(inning1[0][0])+"/"+str(inning1[0][1]), "in", str(math.floor((inning1[0][2]-1)/6))+'.'+str((inning1[0][2]-1)%6), "("+str(50-r1[5])+")", "overs.")
  print(inning1[4])

  if R1 >= R2:
    target = target * R2/R1
  else:
    target = target + G50 * (R2-R1)/100

  target = math.floor(target + 1)

  if r1[3] and inning1[3]:
    print("\nTarget:", target, "(D/L method) off", 50-r1[5], "over(s).")
  else:
    print("\nTarget:", target, "off 50 overs.")


  print("\n2ND INNINGS:", bat2[0])
  r2 = getRain(2, rainProb, (r1[5]*6)+1)
  # print(r2)
  inning2 = scoreInnings(2, pitch, (r1[5]*6)+1, 300, r2[3], r2[0], r2[2])
  # inn_no: int, pitch: int, target: int, start: int, end:int

  ov = 50-r1[5]-r2[5]
  if r2[2] == 300:
    ovtext = "over(s)."
  else:
    ovtext = "("+str(ov)+") over(s)."

  if r2[3] == True:
    if inning2[3]:
      time = math.ceil((r2[1]+18)*0.75)
      if r2[2] == 300:
        if time >= 60:
          print(math.floor(time/60), "hour(s)", time%60, "min(s) of rain after", str(inning2[3][0])+"/"+str(inning2[3][1]), "in", str(math.floor((inning2[3][2]-1)/6))+'.'+str((inning2[3][2])%6), "over(s). Innings cut short.")
        else:
          print(time, "min(s) of rain after", str(inning2[3][0])+"/"+str(inning2[3][1]), "in", str(math.floor((inning2[3][2]-1)/6))+'.'+str((inning2[3][2])%6), "over(s). Innings cut short.")
      else:
        if time >= 60:
          print(math.floor(time/60), "hour(s)", time%60, "min(s) of rain after", str(inning2[3][0])+"/"+str(inning2[3][1]), "in", str(math.floor((inning2[3][2]-1)/6))+'.'+str((inning2[3][2])%6), "over(s).", r2[5], "over(s) lost.")
        else:
          print(time, "min(s) of rain after", str(inning2[3][0])+"/"+str(inning2[3][1]), "in", str(math.floor((inning2[3][2]-1)/6))+'.'+str((inning2[3][2])%6), "over(s).", r2[5], "over(s) lost.")
    if r2[5] == 0:
      print("A slight drizzle did not cause any loss of overs.")

  if not r2[4] or inning2[0][2] >= 180:
    if ov > 20:
      print("Total:", str(inning2[0][0])+"/"+str(inning2[0][1]), "in", str(math.floor((inning2[0][2]-1)/6))+'.'+str((inning2[0][2]-1)%6), ovtext)
      print(inning2[4])

      if r2[3] and inning2[3]:
        print("Revised target:", target)
        print("Par score:", target-1)

      print("\nRESULT")
      if (r1[3] and inning1[3]) or (r2[3] and inning2[3]):
        if inning2[0][0] >= target:
          if inning2[0][2] < ov*6:
            print(bat2[0], "win by", 10-inning2[0][1], "wicket(s) (D/L method).\n\n")
          else:
            print(bat2[0], "win by", inning2[0][0]-target+1, "run(s) (D/L method).\n\n")
        elif inning2[0][0] == (target-1):
          print("Match tied. (D/L method).\n\n")
        else:
          print(bat1[0], "win by", target-inning2[0][0]-1, "run(s) (D/L method).\n\n")
      else:
        if inning2[0][0] >= target:
          print(bat2[0], "win by", 10-inning2[0][1], "wicket(s).\n\n")
        elif inning2[0][0] == (target-1):
          print("Match tied.")
        else:
          print(bat1[0], "win by", target-inning2[0][0]-1, "run(s).\n\n")
    else:
      print("Match abandoned due to rain.\n\n")
  else:
    print("Match abandoned due to rain.\n\n")

  return [[bat1, r1, inning1], [bat2, r2, inning2], target]