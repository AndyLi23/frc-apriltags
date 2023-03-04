import json
import os

def save_json(data, file_name):
    print('Saving to file: ' + file_name)
    json_data = json.dumps(data)
    with open(file_name, 'w') as f:
        f.write(json_data)
        
def cov(data, i, j, im, jm, N):
    s = 0
    
    for n in range(N):
        s += (data[n][i] - im) * (data[n][j] - jm)
        
    return s / (N-1)
        
for f in os.listdir('./covf/'):
    d = json.load(open('./covf/' + f))
    
    data = d['poses']
    
    N = len(data)
    
    m = [sum(data[i][j] for i in range(N)) / N for j in range(3)]
    
    mtx = [[0, 0, 0],
           [0, 0, 0],
           [0, 0, 0]]
    
    for i in range(3):
        for j in range(3):
            mtx[i][j] = cov(data, i, j, m[i], m[j], N)
            
    jd = {'cov': mtx, 'info': d['info']}
    
    save_json(jd, './covm/' + f)