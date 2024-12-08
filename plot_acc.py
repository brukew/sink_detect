import csv
import matplotlib.pyplot as plt

CSV_FILE = 'train_data.csv'

# Read the data
steps = []
classes = []
corrects = []
with open(CSV_FILE, 'r', newline='') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader, start=1):
        steps.append(i)
        classes.append(int(row['cls']))
        # Convert 'True'/'False' string to boolean
        corrects.append(row['correct'].strip().lower() == 'true')

# Compute cumulative accuracy for the entire dataset
cumulative_correct = 0
overall_accuracies = []
for i, c in enumerate(corrects, start=1):
    if c:
        cumulative_correct += 1
    overall_accuracies.append(cumulative_correct / i)

# Compute cumulative accuracy per class
# We will track correctness counts and total counts per class over time
class_correct_counts = {}
class_totals = {}
class_accuracies = {}  # Will store class-wise accuracy arrays keyed by class
labels = []
total_steps = len(corrects)  # total number of steps matches the length of corrects/classes

for cls_label, is_correct in zip(classes, corrects):
    if cls_label not in class_correct_counts:
        class_correct_counts[cls_label] = 0
        class_totals[cls_label] = 0
        class_accuracies[cls_label] = []
    class_totals[cls_label] += 1
    if is_correct:
        class_correct_counts[cls_label] += 1
    class_accuracies[cls_label].append(class_correct_counts[cls_label] / class_totals[cls_label])
    for i in class_correct_counts:
        if i!=cls_label:
            class_accuracies[i].append(class_accuracies[i][-1])

# Plot the results
plt.figure(figsize=(10, 6))

# Plot overall accuracy
plt.plot(steps, overall_accuracies, label='Overall Accuracy', linewidth=2)

# Plot each class accuracy
for cls_label, acc_list in class_accuracies.items():
    plt.plot(steps[:len(acc_list)], acc_list, label=f'Class {cls_label} Accuracy', linestyle='--')

plt.title('Cumulative Accuracy Over Time')
plt.xlabel('Step')
plt.ylabel('Accuracy')
plt.ylim([0, 1])
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
