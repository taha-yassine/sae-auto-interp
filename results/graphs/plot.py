# %%

import os
import json
import pandas as pd
from collections import Counter, defaultdict
import random

directory = "scores/fuzz_70b/simple_local_70b"

def load_data(directory):
    data = []
    for file in os.listdir(directory):
        if file.endswith(".txt"):
            with open(os.path.join(directory, file), "r") as f:
                data.append(
                    (file, json.load(f))
                )
    return data

def clean(df):
    def _clean(text):
        return text.replace("<<", "").replace(">>", "")
    
    for col in df.columns:
        if "text" in col:
            df[col] = df[col].apply(_clean)
    return df


def repreat_precision(df):
    grouped = df.groupby("id")
    results = []

    # Iterate through the groups
    for name, group in grouped:

        if len(group) == 2:
            print(group)
            first_pass = group[
                (group['highlighted'] == False) 
                & (group['ground_truth'] == True)
            ]
            second_pass = group[
                (group['highlighted'] == True)
                & (group['ground_truth'] == True)
            ]
            

            if not first_pass.empty and not second_pass.empty:
                first_marked_correct = first_pass.iloc[0]['predicted']
                second_marked_correct = second_pass.iloc[0]['predicted']
                quantile = group.iloc[0]['quantile']
                
                if first_marked_correct and second_marked_correct:
                    both_correct = "both"
                elif first_marked_correct:
                    both_correct = "first"
                elif second_marked_correct:
                    both_correct = "second"
                else:
                    both_correct = "neither"
                
                results.append({
                    'text': name,
                    'correct': both_correct,
                    'quantile': quantile
                })

    result_df = pd.DataFrame(results)


    quantile_grouped = result_df.groupby("quantile")

    per_quantile = {}

    for name, group in quantile_grouped:
        print(name)
        count = Counter(group['correct'])
        per_quantile[name] = {
            'first': count['first'],
            'second': count['second'],
            'both': count['both'],
            'neither': count['neither']
        }

    return per_quantile


def get_stats(data):
    df = pd.DataFrame(data)
    df = clean(df)

    per_quantile_repeat_precision = repreat_precision(df)

    return per_quantile_repeat_precision


# %%

### MAIN ###

data = load_data(directory)

layer_stats = defaultdict(dict)


# %%

from collections import defaultdict
import heapq

def find_top_n_files_with_most_both_per_layer(data, n=2):
    both_counts_per_layer = defaultdict(list)
    
    for file, scores in data:
        layer = int(file.split("_")[0].split("layer")[-1])
        
        both_count = sum(1 for score in scores if score['highlighted'] and score['ground_truth'] and score['predicted'])
        
        # Use a min-heap of size n to keep track of top n files
        if len(both_counts_per_layer[layer]) < n:
            heapq.heappush(both_counts_per_layer[layer], (both_count, file))
        elif both_count > both_counts_per_layer[layer][0][0]:
            heapq.heapreplace(both_counts_per_layer[layer], (both_count, file))
    
    # Convert heaps to sorted lists
    top_n_per_layer = {
        layer: sorted([(count, file) for count, file in files], reverse=True)
        for layer, files in both_counts_per_layer.items()
    }
    
    return top_n_per_layer

# Example usage:
n = 3  # Change this to get top N files
result = find_top_n_files_with_most_both_per_layer(data, n)

# sort to a better structure

_result = defaultdict(dict)

for layer, file_data in result.items():
    for count, file in file_data:
        feature = file.split("_")[1].split(".")[0].split("feature")[-1]
        _result[layer][feature] = count

with open("top_features.json", "w") as f:
    json.dump(_result, f, indent=2)
# %%

for file, scores in data:
    layer = int(
        file.split("_")[0].split("layer")[-1]
    )
    stats = get_stats(scores)

    
    for quantile, stat in stats.items():
        if quantile not in layer_stats[layer]:
            layer_stats[layer][quantile] = Counter(stat)
        
        layer_stats[layer][quantile] += Counter(stat)
    
# %%

import matplotlib.pyplot as plt
from collections import defaultdict

# Create a figure and set of subplots
fig, axs = plt.subplots(3, 2, figsize=(10, 15))  # Adjust the number of rows and columns as needed

# Flatten the array of subplots for easy iteration
axs = axs.flatten()

# Define a color map for categories
category_colors = {
    "first": "green",
    "second": "orange",
    "both": "blue",
    "neither": "red"
}

# Iterate over layers
for i, layer_idx in enumerate(range(0, 12, 2)):
    per_category_quantile_stats = defaultdict(dict)

    for quantile, stat in layer_stats[layer_idx].items():   
        for category, count in stat.items():
            per_category_quantile_stats[category][quantile] = count

    # Plot lines per category for the current subplot
    ax = axs[i]
    sorted_categories = sorted(per_category_quantile_stats.keys())
    
    for category in sorted_categories:
        stats = per_category_quantile_stats[category]

        # Go through categories in order so legends are consistent
        if category not in category_colors:
            category_colors[category] = ax._get_lines.get_next_color()
        ax.plot(stats.keys(), stats.values(), label=category, color=category_colors[category], linewidth=2)  # Thicker lines

    ax.legend()
    ax.set_xlabel('Quantile')
    ax.set_ylabel('Count')
    ax.set_ylim(0, 200)  # Adjust the y-axis limits as needed
    ax.set_title(f'Quantile Distribution by Category (Layer {layer_idx})')

# Adjust layout for better spacing
plt.tight_layout()
plt.show()