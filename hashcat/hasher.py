import hashlib
import sys

for line in sys.stdin:
    line = line.strip()
    hasher = hashlib.md5()
    hasher.update(line.encode('utf-8'))
    print(hasher.hexdigest())