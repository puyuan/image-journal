import dateutil.parser
import re
from findImage import findImage


def discardEmptyLine(line):
    if (re.search(r'^\s*$', line)):
        return 1
    else:
        return 0
    
def parseDate(line):
    try:
        yourdate = dateutil.parser.parse(line)
    except:
        yourdate=0
    return yourdate


f=open("sianjimountain.txt", "r");
for line in f: 
    line=line.strip()
    if (discardEmptyLine(line)==1):
        continue

    date=parseDate(line)
    if date!=0:
       print line
       print  findImage(line)

   



