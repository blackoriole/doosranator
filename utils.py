import os, sys, json

# hide prints

class HiddenPrints:
  def __enter__(self):
      self._original_stdout = sys.stdout
      sys.stdout = open(os.devnull, 'w')

  def __exit__(self, exc_type, exc_val, exc_tb):
      sys.stdout.close()
      sys.stdout = self._original_stdout

# convert keys of a 3-tier dict to int
def keyConvert(d:dict) -> dict:
  outp = {}
  for key, value in d.items():
    if isinstance(value, dict):
      outp[int(key)] = {}
      for k1, v1 in value.items():
        if isinstance(v1, dict):
          outp[int(key)][int(k1)] = {}
          for k2, v2 in v1.items():
            outp[int(key)][int(k1)][int(k2)] = v2
        else:
          outp[int(key)][int(k1)] = v1
    else:
      outp[int(key)] = value
  return outp

# read and write matchlists: read first, append if necessary, then write
class IOTools:
  def writeMatches(file:str, matches:list):
    with open(file, 'w') as f:
      json.dump(matches, f)

  def readMatches(file:str) -> list:
    with open(file, 'r') as f:
      matchlist = json.load(f)
    return (matchlist)
  
# THIS IS A USAGE EXAMPLE OF APPENDING MATCHES
# inp = readMatches('test.json')
# inp.append(matches)
# writeMatches('test.json', inp)