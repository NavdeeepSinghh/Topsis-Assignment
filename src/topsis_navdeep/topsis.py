import sys
import pandas as pd
import numpy as np


def topsis(input_file, weights, impacts, output_file):

    df = pd.read_csv(input_file)

    if df.shape[1] < 3:
        raise Exception("Input file must have at least 3 columns")

    data = df.iloc[:, 1:].astype(float)

    if len(weights) != data.shape[1] or len(impacts) != data.shape[1]:
        raise Exception("Weights/Impacts count mismatch")

    norm = np.sqrt((data ** 2).sum())
    norm_data = data / norm
    weighted = norm_data * weights

    ideal_best = []
    ideal_worst = []

    for i in range(len(impacts)):
        if impacts[i] == '+':
            ideal_best.append(weighted.iloc[:, i].max())
            ideal_worst.append(weighted.iloc[:, i].min())
        else:
            ideal_best.append(weighted.iloc[:, i].min())
            ideal_worst.append(weighted.iloc[:, i].max())

    ideal_best = np.array(ideal_best)
    ideal_worst = np.array(ideal_worst)

    d_best = np.sqrt(((weighted - ideal_best) ** 2).sum(axis=1))
    d_worst = np.sqrt(((weighted - ideal_worst) ** 2).sum(axis=1))

    score = d_worst / (d_best + d_worst)

    df['Topsis Score'] = score
    df['Rank'] = df['Topsis Score'].rank(ascending=False).astype(int)

    df.to_csv(output_file, index=False)


def main():
    if len(sys.argv) != 5:
        print("Usage: topsis <input.csv> <weights> <impacts> <output.csv>")
        sys.exit(1)

    _, input_file, weights, impacts, output_file = sys.argv

    weights = list(map(float, weights.split(',')))
    impacts = impacts.split(',')

    topsis(input_file, weights, impacts, output_file)
