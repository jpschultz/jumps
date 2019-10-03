import os
from multiprocessing import Pool
import tqdm
import random
import glob
import pygs
import pandas as pd
import threading
from queue import Queue


try:
    logPath = os.path.join(os.path.dirname(os.path.realpath(__file__)),'txt_files')
except NameError:
    logPath = os.path.join(os.getcwd(),'txt_files')
if not os.path.exists(logPath):
    os.makedirs(logPath)

avg_list = []

def calculate_average_hops(d):
    total_hops = d[0]
    trials = d[1]
    file_name = d[2]
    logPath = d[3]
    jumps_taken = []

    def get_path(total_hops):
        return [x for x in range(total_hops)]

    path = get_path(total_hops)

    for i in range(trials):
        total_jumps = 0
        while len(path) > 1:
            jump = random.randint(min(path)+1, max(path))
            total_jumps += 1

            if jump == max(path):
                jumps_taken.append(total_jumps)
                total_jumps = 0
                path = get_path(total_hops)
                break
            path = [x for x in range(jump, max(path) + 1)]

    data = ','.join([str(total_hops), str(sum(jumps_taken) / float(len(jumps_taken)))])
    full_filename = os.path.join(logPath, file_name)
    with open(full_filename, 'w') as filehandle:
        filehandle.writelines("%s\n" % data)

    return

def main():
    number_of_hops = [x for x in range(5,100000)]
    completed_files = glob.glob(os.path.join(logPath,'*.txt'))
    completed_hops = [int(x.split('.txt')[0].split('/')[-1]) for x in completed_files]
    completed_hops.sort()
    completed_hops = set(completed_hops)
    to_process = []
    for x in reversed(number_of_hops):
        if x not in completed_hops:
            to_process.append([x, 1000, str(x) + '.txt', logPath])

    if len(to_process) > 0:
        p = Pool(6)
        for _ in tqdm.tqdm(p.imap_unordered(calculate_average_hops, to_process), total=len(number_of_hops)):
            pass
        p.close()
        p.join()
        completed_files = glob.glob(os.path.join(logPath,'*.txt'))
    
    final_output = []
    for file_name in completed_files:
        f = open(file_name, 'r')
        final_output.append(f.readlines()[0].splitlines()[0].split(','))
        f.close()
    df = pd.DataFrame(final_output, columns=['hops','average'])
    df['hops'] = df['hops'].astype(int)
    df['average'] = df['average'].astype(float)
    df = df.sort_values('hops')
    pygs.update_sheet_with_df(df, spreadsheetId='1pNTUlvmw46OkcE6jiXqZ0SXfM-hY3K9H1TWKuHbAefY',sheet_name='Sheet1')
        

if __name__ == '__main__':
    main()