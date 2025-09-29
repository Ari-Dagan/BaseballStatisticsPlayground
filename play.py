import os
os.chdir(r'C:\Users\adagan\PlayPython') # Replace with your folder location
from workflows.BaseballUniverseWorkflow import BaseballUniverseWorkflow
import matplotlib.pyplot as plt

season2025DB =  BaseballUniverseWorkflow(
    season=2025,
    Players = []
)

# Run the workflow to populate all data
season2025DB.startWorkflow()

# ============ CREATE FRIDAY VS SUNDAY LEAGUE AVG COMPARISON GRAPH ============

# Get league-wide averages for Friday and Sunday (players with at least 5 games)
league_stats_df = season2025DB.get_league_average_by_weekday(min_games=5, weekdays=["Friday", "Sunday"])

# Create the bar graph
fig, ax = plt.subplots(figsize=(10, 6))

weekdays = league_stats_df['weekday'].values
avg_values = league_stats_df['AVG'].values
num_players = league_stats_df['num_players'].values

x = range(len(weekdays))
width = 0.5

bars = ax.bar(x, avg_values, width, color=['#1f77b4', '#ff7f0e'], alpha=0.8)

# Customize the plot
ax.set_xlabel('Weekday', fontsize=12, fontweight='bold')
ax.set_ylabel('League Batting Average', fontsize=12, fontweight='bold')
ax.set_title('League-Wide Batting Average: Friday vs Sunday\n(Players with at least 5 games on each day)',
             fontsize=14, fontweight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels(weekdays, fontsize=11)
ax.grid(axis='y', alpha=0.3)

# Add value labels on bars with player count
for i, (bar, num) in enumerate(zip(bars, num_players)):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
           f'{height:.3f}\n({int(num)} players)',
           ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('files/friday_sunday_league_avg_comparison.png', dpi=300, bbox_inches='tight')
print("\nGraph saved to files/friday_sunday_league_avg_comparison.png")
print(f"\nLeague Stats:\n{league_stats_df}")
plt.show()
