import csv
import numpy as np
import matplotlib.pyplot as plt
import argparse

def calculate_metrics(simidroid_file, repack_file):
    with open(simidroid_file, 'r') as file:
        resource_reader = csv.reader(file)
        next(resource_reader)  # Skip header
        resource_data = list(resource_reader)

    with open(repack_file, 'r') as file:
        repack_reader = csv.reader(file)
        next(repack_reader)  # Skip header
        repack_data = set(map(tuple, repack_reader))

    thresholds = np.arange(0, 1.01, 0.01)  # Step of 0.01 from 0 to 1
    precision_list = []

    for threshold in thresholds:
        true_positives = 0
        false_positives = 0
        for original, repack, distance in resource_data:
            if float(distance) >= threshold:
                if (original, repack) in repack_data or (repack, original) in repack_data:
                    true_positives += 1
                else:
                    false_positives += 1

        precision = true_positives / (true_positives + false_positives) if true_positives + false_positives > 0 else 0

        precision_list.append(precision)

    return thresholds, precision_list

def plot_metrics(thresholds, precision_list, output_path):
    plt.figure(figsize=(10, 6))
    plt.plot(thresholds, precision_list, label='Precision')
    plt.xlabel('Threshold')
    plt.ylabel('Rate')
    plt.title('Precision vs. Threshold')
    plt.legend()
    plt.grid(True)
    plt.savefig(output_path)

def main():
    parser = argparse.ArgumentParser(description="Calculate and plot precision and recall.")
    parser.add_argument("simidroid_file", help="Path to the simidroid generated CSV file")
    parser.add_argument("repack_file", help="Path to the repack CSV file")
    parser.add_argument("output_path", help="Path to save the plot image")

    args = parser.parse_args()

    thresholds, precision_list = calculate_metrics(args.simidroid_file, args.repack_file)
    plot_metrics(thresholds, precision_list, args.output_path)

if __name__ == "__main__":
    main()
