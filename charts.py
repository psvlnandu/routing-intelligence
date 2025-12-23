"""
Functions to Generate Analysis Graphs for Algorithm Comparison Project
Input: CSV with columns [From, To, Algorithm, Distance, Nodes Expanded, Execution Time, Path Length]
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# ============================================================================
# ANALYSIS 1: Nodes Expanded vs Distance (Line Chart)
# ============================================================================

def plot_nodes_vs_distance(csv_file):
    """
    Plot: How many nodes does each algorithm explore as distance increases?
    X-axis: Distance categories (Short/Medium/Long)
    Y-axis: Average nodes expanded
    Lines: One per algorithm
    """
    df = pd.read_csv(csv_file)
    
    # Define distance categories
    
    def categorize_distance(distance):
        if distance>0 and distance < 500:
            return "Short (<500 mi)"
        elif distance>500 and distance < 1200:
            return "Medium (500-1200 mi)"
        else:
            return "Long from 1600mi"
    
    df['Distance Category'] = df['Distance'].apply(categorize_distance)
    
    # Calculate average nodes per algorithm per distance category
    grouped = df.groupby(['Distance Category', 'Algorithm'])['Nodes Expanded'].mean().reset_index()
    
    # Create plot
    plt.figure(figsize=(12, 6))
    
    for algo in grouped['Algorithm'].unique():
        data = grouped[grouped['Algorithm'] == algo]
        plt.plot(data['Distance Category'], data['Nodes Expanded'], 
                marker='o', linewidth=2.5, markersize=8, label=algo)
    
    plt.xlabel('Distance Category', fontsize=12, fontweight='bold')
    plt.ylabel('Average Nodes Expanded', fontsize=12, fontweight='bold')
    plt.title('How Distance Affects Node Exploration\n(A* vs UCS vs Greedy vs DFS)', 
              fontsize=14, fontweight='bold', pad=20)
    plt.legend(loc='best', fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('1_nodes_vs_distance.png', dpi=300, bbox_inches='tight')
    print("✅ Chart 1 saved: 1_nodes_vs_distance.png")
    # plt.show()


# ============================================================================
# ANALYSIS 2: Average Nodes Expanded (All Routes) - Bar Chart
# ============================================================================

def plot_average_nodes_all_routes(csv_file):
    """
    Plot: Which algorithm explores least nodes on average (across all 12 routes)?
    X-axis: Algorithms (sorted by efficiency)
    Y-axis: Average nodes expanded
    """
    df = pd.read_csv(csv_file)
    
    # Calculate average nodes per algorithm
    avg_nodes = df.groupby('Algorithm')['Nodes Expanded'].mean().sort_values()
    
    # Create plot
    fig, ax = plt.subplots(figsize=(12, 6))
    
    colors = ['#2ecc71' if 'A*' in algo else '#e74c3c' if 'DFS' in algo else '#f39c12' 
              if 'Greedy' in algo else '#3498db' for algo in avg_nodes.index]
    
    bars = ax.barh(range(len(avg_nodes)), avg_nodes.values, color=colors, edgecolor='black', linewidth=1.5)
    
    # Add value labels
    for i, (algo, val) in enumerate(zip(avg_nodes.index, avg_nodes.values)):
        ax.text(val, i, f'  {val:.0f}', va='center', fontweight='bold', fontsize=10)
    
    ax.set_yticks(range(len(avg_nodes)))
    ax.set_yticklabels(avg_nodes.index, fontsize=11)
    ax.set_xlabel('Average Nodes Expanded (Across All Routes)', fontsize=12, fontweight='bold')
    ax.set_title('Which Algorithm Explores Least Nodes?\n(Lower is Better)', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('2_average_nodes_all_routes.png', dpi=300, bbox_inches='tight')
    print("✅ Chart 2 saved: 2_average_nodes_all_routes.png")
    # plt.show()


# ============================================================================
# ANALYSIS 3: A* Heuristics Comparison - Why Euclidean Wins
# ============================================================================

def plot_astar_heuristics_comparison(csv_file):
    """
    Plot: Compare A* variants (Haversine, Euclidean, Manhattan, Min Graph, Weighted)
    Which heuristic is smartest?
    """
    df = pd.read_csv(csv_file)
    
    # Filter only A* algorithms
    astar_algos = df[df['Algorithm'].str.contains('A*')]
    avg_nodes = astar_algos.groupby('Algorithm')['Nodes Expanded'].mean().sort_values()
    
    # Create plot
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Color Euclidean differently (winner)
    colors = ['#2ecc71' if 'Euclidean' in algo else '#3498db' for algo in avg_nodes.index]
    
    bars = ax.bar(range(len(avg_nodes)), avg_nodes.values, color=colors, edgecolor='black', linewidth=1.5)
    
    # Add value labels
    for bar, val in zip(bars, avg_nodes.values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.0f}',
                ha='center', va='bottom', fontweight='bold', fontsize=11)
    
    ax.set_xticks(range(len(avg_nodes)))
    ax.set_xticklabels(avg_nodes.index, rotation=45, ha='right', fontsize=10)
    ax.set_ylabel('Average Nodes Expanded', fontsize=12, fontweight='bold')
    ax.set_title('A* Heuristic Comparison: Which Works Best?\n(Euclidean Wins!)', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('3_astar_heuristics_comparison.png', dpi=300, bbox_inches='tight')
    print("✅ Chart 3 saved: 3_astar_heuristics_comparison.png")
    # plt.show()


# ============================================================================
# ANALYSIS 4: Informed vs Uninformed - Gap Visualization
# ============================================================================

def plot_informed_vs_uninformed(csv_file):
    """
    Plot: Show the gap between informed (A*) and uninformed (UCS/DFS) algorithms
    """
    df = pd.read_csv(csv_file)
    
    # Categorize algorithms
    astar_algos = df[df['Algorithm'].str.contains('A*')].groupby('Algorithm')['Nodes Expanded'].mean()
    ucs = df[df['Algorithm'] == 'UCS (Dijkstra)']['Nodes Expanded'].mean()
    dfs = df[df['Algorithm'] == 'DFS']['Nodes Expanded'].mean()
    greedy = df[df['Algorithm'] == 'Greedy Best-First']['Nodes Expanded'].mean()
    
    # Create plot
    fig, ax = plt.subplots(figsize=(12, 6))
    
    categories = ['Informed\n(A* Variants)', 'Uninformed\n(UCS)', 'Other\n(Greedy)', 'Other\n(DFS)']
    values = [astar_algos.mean(), ucs, greedy, dfs]
    colors = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c']
    
    bars = ax.bar(categories, values, color=colors, edgecolor='black', linewidth=2, width=0.6)
    
    # Add value labels
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.0f}',
                ha='center', va='bottom', fontweight='bold', fontsize=12)
    
    ax.set_ylabel('Average Nodes Expanded', fontsize=12, fontweight='bold')
    ax.set_title('Informed (A*) vs Uninformed (UCS/DFS) Search\nHow Much Smarter Are Heuristics?', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.grid(axis='y', alpha=0.3)
    
    # Add percentage reduction
    reduction = ((ucs - astar_algos.mean()) / ucs * 100)
    ax.text(0, ucs + 30, f'{reduction:.0f}% reduction', ha='center', fontweight='bold', fontsize=11, 
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
    
    plt.tight_layout()
    plt.savefig('4_informed_vs_uninformed.png', dpi=300, bbox_inches='tight')
    print("✅ Chart 4 saved: 4_informed_vs_uninformed.png")
    # plt.show()


# ============================================================================
# ANALYSIS 5: All 12 Routes - Detailed Breakdown
# ============================================================================

def plot_all_routes_detailed(csv_file):
    """
    Plot: Show nodes expanded for each individual route
    Group by route, show bars for UCS, A*(Euclidean), Greedy
    """
    df = pd.read_csv(csv_file)
    
    # Create route label
    df['Route'] = df['From'].str.split(',').str[0] + '\n→\n' + df['To'].str.split(',').str[0]
    
    # Filter algorithms of interest
    algos_to_plot = ['UCS (Dijkstra)', 'A* (Euclidean)', 'Greedy Best-First']
    df_filtered = df[df['Algorithm'].isin(algos_to_plot)]
    
    # Create plot
    fig, ax = plt.subplots(figsize=(16, 8))
    
    routes = df_filtered['Route'].unique()
    x = np.arange(len(routes))
    width = 0.25
    
    for i, algo in enumerate(algos_to_plot):
        values = [df_filtered[(df_filtered['Route'] == route) & (df_filtered['Algorithm'] == algo)]['Nodes Expanded'].values[0] 
                  if len(df_filtered[(df_filtered['Route'] == route) & (df_filtered['Algorithm'] == algo)]) > 0 else 0 
                  for route in routes]
        ax.bar(x + i*width, values, width, label=algo, edgecolor='black', linewidth=1)
    
    ax.set_xlabel('Route', fontsize=12, fontweight='bold')
    ax.set_ylabel('Nodes Expanded', fontsize=12, fontweight='bold')
    ax.set_title('Nodes Expanded by Route\n(All 12 Test Cases - Detailed Breakdown)', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x + width)
    ax.set_xticklabels(routes, fontsize=9, rotation=45, ha='right')
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('5_all_routes_detailed.png', dpi=300, bbox_inches='tight')
    print("✅ Chart 5 saved: 5_all_routes_detailed.png")
    # plt.show()


# ============================================================================
# ANALYSIS 6: Greedy Trade-off (Speed vs Quality)
# ============================================================================

def plot_greedy_tradeoff(csv_file):
    """
    Plot: Greedy finds paths fast but are they optimal?
    X-axis: Nodes Expanded (speed)
    Y-axis: Path Distance (quality)
    """
    df = pd.read_csv(csv_file)
    
    # Get data for each route
    routes = df['From'].str.split(',').str[0] + ' → ' + df['To'].str.split(',').str[0]
    df['Route'] = routes
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Group by route and algorithm
    for route in df['Route'].unique():
        route_data = df[df['Route'] == route]
        
        ucs_data = route_data[route_data['Algorithm'] == 'UCS (Dijkstra)']
        greedy_data = route_data[route_data['Algorithm'] == 'Greedy Best-First']
        astar_data = route_data[route_data['Algorithm'] == 'A* (Euclidean)']
        
        if len(ucs_data) > 0:
            ax.scatter(ucs_data['Nodes Expanded'].values[0], ucs_data['Distance'].values[0], 
                      s=150, color='#3498db', marker='o', edgecolor='black', linewidth=1.5, alpha=0.7, label='UCS' if route == df['Route'].unique()[0] else '')
        
        if len(greedy_data) > 0:
            ax.scatter(greedy_data['Nodes Expanded'].values[0], greedy_data['Distance'].values[0], 
                      s=150, color='#f39c12', marker='^', edgecolor='black', linewidth=1.5, alpha=0.7, label='Greedy' if route == df['Route'].unique()[0] else '')
        
        if len(astar_data) > 0:
            ax.scatter(astar_data['Nodes Expanded'].values[0], astar_data['Distance'].values[0], 
                      s=150, color='#2ecc71', marker='s', edgecolor='black', linewidth=1.5, alpha=0.7, label='A* (Euclidean)' if route == df['Route'].unique()[0] else '')
    
    ax.set_xlabel('Nodes Expanded (Efficiency)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Route Distance (Quality)', fontsize=12, fontweight='bold')
    ax.set_title('Speed vs Quality Trade-off: Greedy is Fast But Suboptimal', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.legend(fontsize=11, loc='best')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('6_greedy_tradeoff.png', dpi=300, bbox_inches='tight')
    print("✅ Chart 6 saved: 6_greedy_tradeoff.png")
    # plt.show()

"""
Data-Driven Trade-off Visualization
Shows actual relationship between:
1. Nodes Explored (Efficiency)
2. Execution Time (Speed)
3. Path Distance (Optimality)
"""


# ============================================================================
# VISUALIZATION 1: Nodes vs Execution Time (Efficiency vs Speed)
# ============================================================================

def plot_nodes_vs_time(csv_file):
    """
    Scatter plot showing:
    X-axis: Execution Time (ms)
    Y-axis: Nodes Expanded
    
    Each algorithm shown as different color/marker
    Shows: Which is fastest? Which explores least nodes?
    """
    df = pd.read_csv(csv_file)
    
    fig, ax = plt.subplots(figsize=(13, 8))
    
    # Define colors and markers for each algorithm type
    algo_styles = {
        'UCS (Dijkstra)': {'color': '#3498db', 'marker': 'o', 'size': 150, 'label': 'UCS (No Heuristic)'},
        'A* (Haversine)': {'color': '#2ecc71', 'marker': 's', 'size': 100, 'label': 'A* (Haversine)'},
        'A* (Euclidean)': {'color': '#27ae60', 'marker': 's', 'size': 100, 'label': 'A* (Euclidean)'},
        'A* (Manhattan)': {'color': '#229954', 'marker': 's', 'size': 100, 'label': 'A* (Manhattan)'},
        'A* (Min Graph)': {'color': '#1e8449', 'marker': 's', 'size': 100, 'label': 'A* (Min Graph)'},
        'A* (Weighted)': {'color': '#196f3d', 'marker': 's', 'size': 100, 'label': 'A* (Weighted)'},
        'Greedy Best-First': {'color': '#f39c12', 'marker': '^', 'size': 120, 'label': 'Greedy (Fast but Risky)'},
        'DFS': {'color': '#e74c3c', 'marker': 'v', 'size': 120, 'label': 'DFS (Unpredictable)'}
    }
    
    # Plot each algorithm
    for algo, style in algo_styles.items():
        algo_data = df[df['Algorithm'] == algo]
        ax.scatter(algo_data['Execution Time'], algo_data['Nodes Expanded'],
                  color=style['color'], marker=style['marker'], s=style['size'],
                  edgecolor='black', linewidth=1.5, alpha=0.7, label=style['label'], zorder=3)
    
    # Add quadrant dividers to show trade-offs
    median_time = df['Execution Time'].median()
    median_nodes = df['Nodes Expanded'].median()
    
    ax.axvline(x=median_time, color='gray', linestyle='--', linewidth=1.5, alpha=0.4)
    ax.axhline(y=median_nodes, color='gray', linestyle='--', linewidth=1.5, alpha=0.4)
    
    # Add quadrant labels
    ax.text(0.1, 0.95, 'IDEAL\n(Fast & Few Nodes)', transform=ax.transAxes,
           fontsize=11, fontweight='bold', color='green', ha='left', va='top',
           bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.6))
    
    ax.text(0.9, 0.95, 'SLOW\n(Slow & Few Nodes)', transform=ax.transAxes,
           fontsize=11, fontweight='bold', color='blue', ha='right', va='top',
           bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.6))
    
    ax.text(0.1, 0.05, 'FAST BUT RISKY\n(Fast & Many Nodes)', transform=ax.transAxes,
           fontsize=11, fontweight='bold', color='orange', ha='left', va='bottom',
           bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.6))
    
    ax.set_xlabel('Execution Time (ms)', fontsize=13, fontweight='bold')
    ax.set_ylabel('Nodes Explored', fontsize=13, fontweight='bold')
    ax.set_title('Speed vs Efficiency Trade-off\nWhich Algorithm is Fastest AND Explores Fewest Nodes?',
                 fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='best', fontsize=10, framealpha=0.95)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('8_nodes_vs_time_tradeoff.png', dpi=300, bbox_inches='tight')
    print("✅ Chart saved: 8_nodes_vs_time_tradeoff.png")
    # plt.show()


# ============================================================================
# VISUALIZATION 2: Path Distance vs Execution Time (Optimality vs Speed)
# ============================================================================

def plot_distance_vs_time(csv_file):
    """
    Scatter plot showing:
    X-axis: Execution Time (ms)
    Y-axis: Path Distance (miles)
    
    Shows which algorithms find SHORT paths (optimal) vs LONG paths (suboptimal)
    """
    df = pd.read_csv(csv_file)
    
    fig, ax = plt.subplots(figsize=(13, 8))
    
    algo_styles = {
        'UCS (Dijkstra)': {'color': '#3498db', 'marker': 'o', 'size': 150, 'label': 'UCS (Optimal)'},
        'A* (Haversine)': {'color': '#2ecc71', 'marker': 's', 'size': 100, 'label': 'A* Variants (Optimal)'},
        'A* (Euclidean)': {'color': '#27ae60', 'marker': 's', 'size': 100, 'label': ''},
        'A* (Manhattan)': {'color': '#229954', 'marker': 's', 'size': 100, 'label': ''},
        'A* (Min Graph)': {'color': '#1e8449', 'marker': 's', 'size': 100, 'label': ''},
        'A* (Weighted)': {'color': '#196f3d', 'marker': 's', 'size': 100, 'label': ''},
        'Greedy Best-First': {'color': '#f39c12', 'marker': '^', 'size': 120, 'label': 'Greedy (Suboptimal ⚠️)'},
        'DFS': {'color': '#e74c3c', 'marker': 'v', 'size': 120, 'label': 'DFS (Unpredictable ❌)'}
    }
    
    # Get optimal distance for reference
    optimal_distances = df[df['Algorithm'] == 'UCS (Dijkstra)'].set_index('From')['Distance'].to_dict()
    
    # Plot each algorithm
    plotted_labels = set()
    for algo, style in algo_styles.items():
        algo_data = df[df['Algorithm'] == algo]
        
        label = style['label'] if style['label'] not in plotted_labels else ''
        if style['label']:
            plotted_labels.add(style['label'])
        
        ax.scatter(algo_data['Execution Time'], algo_data['Distance'],
                  color=style['color'], marker=style['marker'], s=style['size'],
                  edgecolor='black', linewidth=1.5, alpha=0.7, label=label, zorder=3)
    
    # Add quadrant dividers
    median_time = df['Execution Time'].median()
    median_distance = df['Distance'].median()
    
    ax.axvline(x=median_time, color='gray', linestyle='--', linewidth=1.5, alpha=0.4)
    ax.axhline(y=median_distance, color='gray', linestyle='--', linewidth=1.5, alpha=0.4)
    
    # Add quadrant labels
    ax.text(0.1, 0.95, '✅ BEST\n(Fast & Optimal)', transform=ax.transAxes,
           fontsize=11, fontweight='bold', color='green', ha='left', va='top',
           bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.6))
    
    ax.text(0.9, 0.95, '⏱️ SLOW\n(Slow & Optimal)', transform=ax.transAxes,
           fontsize=11, fontweight='bold', color='blue', ha='right', va='top',
           bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.6))
    
    ax.text(0.1, 0.05, '❌ WRONG\n(Fast & Suboptimal)', transform=ax.transAxes,
           fontsize=11, fontweight='bold', color='red', ha='left', va='bottom',
           bbox=dict(boxstyle='round', facecolor='#FFB6C6', alpha=0.6))
    
    ax.set_xlabel('Execution Time (ms)', fontsize=13, fontweight='bold')
    ax.set_ylabel('Path Distance (miles)', fontsize=13, fontweight='bold')
    ax.set_title('Optimality vs Speed Trade-off\nWhich Algorithms Find Shortest Paths FAST?',
                 fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='best', fontsize=10, framealpha=0.95)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('8b_distance_vs_time_tradeoff.png', dpi=300, bbox_inches='tight')
    print("✅ Chart saved: 8b_distance_vs_time_tradeoff.png")
    


# ============================================================================
# VISUALIZATION 3: 3-Way Comparison (Nodes + Time + Distance)
# ============================================================================

def plot_three_way_comparison(csv_file):
    """
    Three subplots showing different trade-offs:
    1. Nodes vs Execution Time
    2. Path Distance vs Execution Time  
    3. Nodes vs Path Distance
    """
    df = pd.read_csv(csv_file)
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    algo_colors = {
        'UCS (Dijkstra)': '#3498db',
        'A* (Haversine)': '#2ecc71',
        'A* (Euclidean)': '#27ae60',
        'A* (Manhattan)': '#229954',
        'A* (Min Graph)': '#1e8449',
        'A* (Weighted)': '#196f3d',
        'Greedy Best-First': '#f39c12',
        'DFS': '#e74c3c'
    }
    
    algo_markers = {
        'UCS (Dijkstra)': 'o',
        'A* (Haversine)': 's',
        'A* (Euclidean)': 's',
        'A* (Manhattan)': 's',
        'A* (Min Graph)': 's',
        'A* (Weighted)': 's',
        'Greedy Best-First': '^',
        'DFS': 'v'
    }
    
    # ===== SUBPLOT 1: Nodes vs Time =====
    for algo in df['Algorithm'].unique():
        algo_data = df[df['Algorithm'] == algo]
        axes[0].scatter(algo_data['Execution Time'], algo_data['Nodes Expanded'],
                       color=algo_colors.get(algo, '#808080'), 
                       marker=algo_markers.get(algo, 'o'), s=100,
                       edgecolor='black', linewidth=1, alpha=0.7, label=algo)
    
    axes[0].set_xlabel('Time (ms)', fontsize=11, fontweight='bold')
    axes[0].set_ylabel('Nodes Explored', fontsize=11, fontweight='bold')
    axes[0].set_title('⚡ Speed vs Efficiency', fontsize=12, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    
    # ===== SUBPLOT 2: Distance vs Time =====
    for algo in df['Algorithm'].unique():
        algo_data = df[df['Algorithm'] == algo]
        axes[1].scatter(algo_data['Execution Time'], algo_data['Distance'],
                       color=algo_colors.get(algo, '#808080'),
                       marker=algo_markers.get(algo, 'o'), s=100,
                       edgecolor='black', linewidth=1, alpha=0.7)
    
    axes[1].set_xlabel('Time (ms)', fontsize=11, fontweight='bold')
    axes[1].set_ylabel('Path Distance (mi)', fontsize=11, fontweight='bold')
    axes[1].set_title('✅ Speed vs Quality', fontsize=12, fontweight='bold')
    axes[1].grid(True, alpha=0.3)
    
    # ===== SUBPLOT 3: Nodes vs Distance =====
    for algo in df['Algorithm'].unique():
        algo_data = df[df['Algorithm'] == algo]
        axes[2].scatter(algo_data['Nodes Expanded'], algo_data['Distance'],
                       color=algo_colors.get(algo, '#808080'),
                       marker=algo_markers.get(algo, 'o'), s=100,
                       edgecolor='black', linewidth=1, alpha=0.7)
    
    axes[2].set_xlabel('Nodes Explored', fontsize=11, fontweight='bold')
    axes[2].set_ylabel('Path Distance (mi)', fontsize=11, fontweight='bold')
    axes[2].set_title('🎯 Efficiency vs Quality', fontsize=12, fontweight='bold')
    axes[2].grid(True, alpha=0.3)
    
    fig.suptitle('Three-Way Trade-off Analysis: All Metrics at Once', 
                 fontsize=15, fontweight='bold', y=1.02)
    
    # Legend outside the plots
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, -0.02), 
              ncol=4, fontsize=9, framealpha=0.95)
    
    plt.tight_layout()
    plt.savefig('8c_three_way_comparison.png', dpi=300, bbox_inches='tight')
    print("✅ Chart saved: 8c_three_way_comparison.png")
     


# ============================================================================
# VISUALIZATION 4: Average Metrics Comparison (Bar + Line Combined)
# ============================================================================

def plot_average_tradeoff_comparison(csv_file):
    """
    Show average metrics for each algorithm type:
    Bars: Nodes Explored
    Line overlay: Execution Time
    """
    df = pd.read_csv(csv_file)
    
    # Calculate averages by algorithm
    avg_metrics = df.groupby('Algorithm')[['Nodes Expanded', 'Execution Time', 'Distance']].mean().reset_index()
    avg_metrics = avg_metrics.sort_values('Nodes Expanded')
    
    fig, ax1 = plt.subplots(figsize=(14, 7))
    
    # Colors based on algorithm type
    colors = []
    for algo in avg_metrics['Algorithm']:
        if 'A*' in algo:
            colors.append('#2ecc71')
        elif 'UCS' in algo:
            colors.append('#3498db')
        elif 'Greedy' in algo:
            colors.append('#f39c12')
        else:  # DFS
            colors.append('#e74c3c')
    
    x_pos = np.arange(len(avg_metrics))
    
    # Plot 1: Nodes Explored (Bars)
    bars = ax1.bar(x_pos, avg_metrics['Nodes Expanded'], color=colors, 
                   edgecolor='black', linewidth=1.5, alpha=0.8, label='Nodes Explored')
    ax1.set_xlabel('Algorithm', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Average Nodes Explored', fontsize=12, fontweight='bold', color='black')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(avg_metrics['Algorithm'], rotation=45, ha='right', fontsize=10)
    ax1.tick_params(axis='y', labelcolor='black')
    ax1.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    # Plot 2: Execution Time (Line on secondary axis)
    ax2 = ax1.twinx()
    line = ax2.plot(x_pos, avg_metrics['Execution Time'], 'o-', 
                   color='#e74c3c', linewidth=3, markersize=10, label='Execution Time (ms)')
    ax2.set_ylabel('Average Execution Time (ms)', fontsize=12, fontweight='bold', color='#e74c3c')
    ax2.tick_params(axis='y', labelcolor='#e74c3c')
    
    # Add value labels on line
    for i, (x, y) in enumerate(zip(x_pos, avg_metrics['Execution Time'])):
        ax2.text(x, y + 1, f'{y:.2f}ms', ha='center', va='bottom', fontweight='bold', fontsize=9, color='#e74c3c')
    
    fig.suptitle('Average Trade-off: Nodes vs Execution Time', fontsize=14, fontweight='bold', y=0.98)
    
    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=11)
    
    plt.tight_layout()
    plt.savefig('8d_average_tradeoff_bars_line.png', dpi=300, bbox_inches='tight')
    print("✅ Chart saved: 8d_average_tradeoff_bars_line.png")
     

def plot_tradeoff_by_distance_category(csv_file):
    """
    Create 3 side-by-side scatter plots:
    - Short routes (200-350 mi)
    - Medium routes (450-580 mi)
    - Long routes (2200-2900 mi)
    
    This shows how algorithms perform differently by distance!
    """
    df = pd.read_csv(csv_file)
    
    # Define distance categories
    def categorize_distance(distance):
        if distance < 400:
            return "Short"
        elif distance < 700:
            return "Medium"
        else:
            return "Long"
    
    df['Distance Category'] = df['Distance'].apply(categorize_distance)
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    algo_colors = {
        'UCS (Dijkstra)': '#3498db',
        'A* (Haversine)': '#2ecc71',
        'A* (Euclidean)': '#27ae60',
        'A* (Manhattan)': '#229954',
        'A* (Min Graph)': '#1e8449',
        'A* (Weighted)': '#196f3d',
        'Greedy Best-First': '#f39c12',
        'DFS': '#e74c3c'
    }
    
    algo_markers = {
        'UCS (Dijkstra)': 'o',
        'A* (Haversine)': 's',
        'A* (Euclidean)': 's',
        'A* (Manhattan)': 's',
        'A* (Min Graph)': 's',
        'A* (Weighted)': 's',
        'Greedy Best-First': '^',
        'DFS': 'v'
    }
    
    categories = ['Short', 'Medium', 'Long']
    
    for idx, category in enumerate(categories):
        ax = axes[idx]
        cat_data = df[df['Distance Category'] == category]
        
        # Plot each algorithm
        for algo in cat_data['Algorithm'].unique():
            algo_data = cat_data[cat_data['Algorithm'] == algo]
            ax.scatter(algo_data['Execution Time'], algo_data['Distance'],
                      color=algo_colors.get(algo, '#808080'),
                      marker=algo_markers.get(algo, 'o'),
                      s=120, edgecolor='black', linewidth=1.5, alpha=0.7)
        
        # Add quadrant dividers
        ax.axvline(x=cat_data['Execution Time'].median(), color='gray', 
                  linestyle='--', linewidth=1, alpha=0.4)
        ax.axhline(y=cat_data['Distance'].median(), color='gray', 
                  linestyle='--', linewidth=1, alpha=0.4)
        
        ax.set_xlabel('Execution Time (ms)', fontsize=11, fontweight='bold')
        ax.set_ylabel('Path Distance (miles)', fontsize=11, fontweight='bold')
        ax.set_title(f'{category} Routes\n({cat_data["Distance"].min():.0f} - {cat_data["Distance"].max():.0f} mi)',
                    fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
    
    fig.suptitle('Trade-off Analysis by Distance Category\n(Shows why Greedy/DFS fail on long routes)',
                fontsize=14, fontweight='bold', y=1.02)
    
    # Add one legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#3498db', 
               markersize=10, markeredgecolor='black', label='UCS'),
        Line2D([0], [0], marker='s', color='w', markerfacecolor='#2ecc71', 
               markersize=8, markeredgecolor='black', label='A* Variants'),
        Line2D([0], [0], marker='^', color='w', markerfacecolor='#f39c12', 
               markersize=10, markeredgecolor='black', label='Greedy'),
        Line2D([0], [0], marker='v', color='w', markerfacecolor='#e74c3c', 
               markersize=10, markeredgecolor='black', label='DFS'),
    ]
    fig.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.02),
              ncol=4, fontsize=11, framealpha=0.95)
    
    plt.tight_layout()
    plt.savefig('9_tradeoff_by_distance_category.png', dpi=300, bbox_inches='tight')
    



def generate_all_charts(csv_file):
    """
    Generate all 6 analysis charts
    """
    print("\n" + "="*70)
    print("GENERATING ANALYSIS CHARTS")
    print("="*70)
    
    print("\n📊 Generating Chart 1: Nodes vs Distance...")
    plot_nodes_vs_distance(csv_file)
    
    print("\n📊 Generating Chart 2: Average Nodes (All Routes)...")
    plot_average_nodes_all_routes(csv_file)
    
    print("\n📊 Generating Chart 3: A* Heuristics Comparison...")
    plot_astar_heuristics_comparison(csv_file)
    
    print("\n📊 Generating Chart 4: Informed vs Uninformed...")
    plot_informed_vs_uninformed(csv_file)
    
    print("\n📊 Generating Chart 5: All Routes Detailed...")
    plot_all_routes_detailed(csv_file)
    
    print("\n📊 Generating Chart 6: Greedy Trade-off...")
    plot_greedy_tradeoff(csv_file)

    print("\n📊 Chart 7: Nodes vs Execution Time (Speed & Efficiency)")
    plot_nodes_vs_time(csv_file)
    
    print("\n📊 Chart 8: Path Distance vs Execution Time (Speed & Quality)")
    plot_distance_vs_time(csv_file)
    
    print("\n📊 Chart 9: Three-Way Comparison (All Metrics)")
    plot_three_way_comparison(csv_file)
    
    print("\n📊 Chart 10: Average Metrics (Bars + Line)")
    plot_average_tradeoff_comparison(csv_file)

    plot_tradeoff_by_distance_category(csv_file)


if __name__ == "__main__":
    # Replace with your actual CSV file path
    csv_file = "AI_data.csv"
    
    # Generate all charts
    generate_all_charts(csv_file)
    