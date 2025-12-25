import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load the data
print("Loading data...")
ratings = pd.read_csv('ratings.csv')

print(f"Loaded {len(ratings)} ratings")
print(f"Ratings range from {ratings['rating'].min()} to {ratings['rating'].max()}")

# Count the frequency of each rating
rating_counts = ratings['rating'].value_counts().sort_index()

print("\nRating Distribution:")
print(rating_counts)

# Calculate percentages
total_ratings = len(ratings)
rating_percentages = (rating_counts / total_ratings * 100).round(2)

# Get all unique ratings in sorted order
unique_ratings = sorted(rating_counts.index)
num_bars = len(unique_ratings)

# Create categorical x positions - THIS PREVENTS OVERLAP
x_pos = list(range(num_bars))  # Creates [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
bar_width = 0.7  # Bars are 0.7 wide, leaving 0.3 gap between them

# Professional color gradient
base_colors = ['#c1272d', '#d33f49', '#e15759', '#ef7d5d', '#f28e2b', 
               '#ffa94d', '#76b7b2', '#59a5a8', '#4e8fa7', '#4e79a7']
colors = base_colors[:num_bars]

# Get values in correct order matching unique_ratings
counts_ordered = [rating_counts[r] for r in unique_ratings]
percentages_ordered = [rating_percentages[r] for r in unique_ratings]

# Create the figure
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 7))

# ===== LEFT PLOT: COUNTS =====
bars1 = ax1.bar(x_pos, counts_ordered, width=bar_width, color=colors, 
                edgecolor='white', linewidth=2, alpha=0.9)

# Add labels on bars
for i in range(num_bars):
    height = counts_ordered[i]
    ax1.text(x_pos[i], height, f'{int(height):,}',
            ha='center', va='bottom', fontsize=10, fontweight='bold')

ax1.set_xlabel('Rating', fontsize=13, fontweight='bold')
ax1.set_ylabel('Number of Ratings', fontsize=13, fontweight='bold')
ax1.set_title('Distribution of Movie Ratings (Count)', fontsize=15, fontweight='bold', pad=15)
ax1.set_xticks(x_pos)
ax1.set_xticklabels([str(r) for r in unique_ratings], fontsize=11)
ax1.grid(axis='y', alpha=0.8, linestyle='-', linewidth=0.5)
ax1.set_axisbelow(True)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.margins(x=0.02)

# Second plot: Percentages
bars2 = ax2.bar(x_pos, percentages_ordered, width=bar_width, color=colors,
                edgecolor='white', linewidth=2, alpha=0.9)

# Add labels on bars
for i in range(num_bars):
    height = percentages_ordered[i]
    ax2.text(x_pos[i], height, f'{height:.1f}%',
            ha='center', va='bottom', fontsize=10, fontweight='bold')

ax2.set_xlabel('Rating', fontsize=13, fontweight='bold')
ax2.set_ylabel('Percentage of Ratings (%)', fontsize=13, fontweight='bold')
ax2.set_title('Distribution of Movie Ratings (Percentage)', fontsize=15, fontweight='bold', pad=15)
ax2.set_xticks(x_pos)
ax2.set_xticklabels([str(r) for r in unique_ratings], fontsize=11)
ax2.grid(axis='y', alpha=0.8, linestyle='-', linewidth=0.5)
ax2.set_axisbelow(True)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.margins(x=0.02)

plt.tight_layout()

# Save the figure
plt.savefig('rating_distribution.png', dpi=300, bbox_inches='tight')
print("\nVisualization saved as 'rating_distribution.png'")

plt.show()

# Print statistics
print("\n" + "="*50)
print("RATING STATISTICS")
print("="*50)
print(f"Total ratings: {total_ratings:,}")
print(f"Average rating: {ratings['rating'].mean():.2f} stars")
print(f"Median rating: {ratings['rating'].median():.1f} stars")
print(f"Most common rating: {rating_counts.idxmax():.1f} stars ({rating_percentages.max():.1f}%)")
print(f"Standard deviation: {ratings['rating'].std():.2f}")

if rating_counts.idxmax() >= 4.0:
    print("\nInsight: Users tend to be generous raters!")
elif rating_counts.idxmax() <= 2.0:
    print("\nInsight: Users tend to be harsh critics!")
else:
    print("\nInsight: Users provide balanced ratings.")

print("\n" + "="*50)
print("Done!")