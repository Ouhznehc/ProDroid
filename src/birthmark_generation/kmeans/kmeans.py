import json
import os
import subprocess

with open('config.json', 'r') as file:
    config = json.load(file)
    n_clusters = config['n_clusters']
    n_iters = config['n_iters']
    dataset = config['dataset']
    kmeans_output = config['kmeans_output']

subprocess.run(f'sh -c \"./kmeans -c {n_clusters} -t {n_iters} < {dataset} > {kmeans_output}\"', shell=True)

