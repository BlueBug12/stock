import sys
import re
print('Number of arguments:',len(sys.argv))
print('Argument List:' ,str(sys.argv))
regex = re.compile(r"([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))")
match = regex.match((sys.argv[1]))
if match:
    print(match.group())
    p=sys.argv[1].split('-')
    print(p)
else:
    print("Invalid argument")
