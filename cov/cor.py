import os
import json

# print(os.listdir('./covm/'))

data = []

for f in os.listdir('./covm/'):
    d = json.load(open('./covm/' + f))
    
    data.append(d)


data = sorted(data, key=lambda d: d["info"][0])

for d in data:
    for i in d['cov']:
        print(i)
    # print(d['cov'][0])
    print("x: %f y: %f angle: %f" % (d['info'][0], d['info'][1], d['info'][2]))
    print()