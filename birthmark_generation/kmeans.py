import numpy as np
import json
from collections import Counter

def hex_to_bin(hash_hex):
    return bin(int(hash_hex, 16))[2:].zfill(len(hash_hex) * 4)
  
def bin_to_hex(hash_bin):
    return hex(int(hash_bin, 2))[2:].zfill(len(hash_bin) // 4)

def hamming_distance(hash1, hash2):
    return sum(c1 != c2 for c1, c2 in zip(hash1, hash2))

def mode_of_positions(dhashes):
    if not dhashes:
        return None
    n = len(dhashes[0])
    mode_hash = ''
    for i in range(n):
        position_chars = [dhash[i] for dhash in dhashes]
        most_common_char, _ = Counter(position_chars).most_common(1)[0]
        mode_hash += most_common_char
    return mode_hash

def kmeans_plus_plus(dhashes, n_clusters, n_iters):
  dhashes_bin = [hex_to_bin(dhash) for dhash in dhashes]
  centers = [dhashes_bin[0]]  # Initialize the first center randomly
  labels = np.zeros(len(dhashes_bin))

  for _ in range(1, n_clusters):
    print('Center', _)
    distances = []
    for dhash_bin in dhashes_bin:
      min_distance = min(hamming_distance(dhash_bin, center) for center in centers)
      distances.append(min_distance)
    probabilities = np.array(distances) / sum(distances)
    new_center_index = np.random.choice(len(dhashes_bin), p=probabilities)
    centers.append(dhashes_bin[new_center_index])

  for _ in range(n_iters):
    print('Iteration', _)
    for i, dhash_bin in enumerate(dhashes_bin):
      distances = [hamming_distance(dhash_bin, center) for center in centers]
      labels[i] = np.argmin(distances)

    new_centers = []
    for j in range(n_clusters):
      members = [dhash for dhash, label in zip(dhashes_bin, labels) if label == j]
      new_center = mode_of_positions(members)
      if new_center:
        new_centers.append(new_center)
      else:
        new_centers.append(centers[j])
    centers = new_centers

  return labels, [bin_to_hex(center) for center in centers]

with open('config.json', 'r') as file:
    config = json.load(file)
    n_clusters = config['n_clusters']
    n_iters = config['n_iters']
    dataset = config['dataset']
    kmeans_output = config['kmeans_output']

with open(dataset, 'r') as file:
    dhashes = file.read().splitlines()

labels, centers = kmeans_plus_plus(dhashes, n_clusters, n_iters)


with open(kmeans_output, 'w') as file:
    for center, label in zip(centers, labels):
        file.write(f"Center: {center}, Label: {label}\n")
