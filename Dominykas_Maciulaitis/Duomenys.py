import matplotlib.pyplot as plt
import numpy as np

# Read data from training_log.txt
scores = []
rewards = []
generations = []

with open('training_log.txt', 'r') as f:
    for i, line in enumerate(f):
        try:
            # Line format example: Gen: 1, Score: 100, Reward: 605.50
            parts = line.strip().split(',')
            
            # Extract Score
            score_str = parts[1].split(':')[1]
            scores.append(float(score_str))
            
            # Extract Reward
            reward_str = parts[2].split(':')[1]
            rewards.append(float(reward_str))
            
            # Use line count as generation
            generations.append(i + 1)
        except (ValueError, IndexError):
            continue

# Create plot
plt.figure(figsize=(10, 6))

plt.plot(generations, scores, label='Score', color='blue')
plt.plot(generations, rewards, label='Reward', color='red')

plt.xlabel('Generation')
plt.ylabel('Value')
plt.title('Training Progress: Score and Reward')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('training_plot.png')
plt.show()