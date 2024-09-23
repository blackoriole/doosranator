import csv

def getGroupsCSV(file:str) -> list:

  groups = {}
  max_rank = 0
  flag = False
  current_group = ''

  with open(file, encoding="utf-8-sig", mode ='r')as f:
    csvLines = csv.reader(f)
    for line in csvLines:
      if flag == True:
        current_group = line[0]
        groups[current_group] = []
        flag = False
        continue
      if line[0] == 'max_rank':
        max_rank = line[1]
      elif line[0] == '':
        flag = True
      elif current_group in groups:
        temp = []
        temp.append(line[0])
        if len(line) > 1:
          for col in line[1:]:
            try:
              x = float(col)
            except:
              x = 0.0
              print("Could not convert", col, "which is a string to a float rank.")
            temp.append(x)
        groups[current_group].append(temp)
      else:
        continue
  return([max_rank, groups])

print("Max rank:", getGroupsCSV('groups.csv')[0])
print("Groups:", getGroupsCSV('groups.csv')[1])