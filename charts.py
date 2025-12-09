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
        if distance < 400:
            return "Short (200-350 mi)"
        elif distance < 700:
            return "Medium (450-580 mi)"
        else:
            return "Long (2200-2900 mi)"
    
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
    plt.show()


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
    plt.show()


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
    plt.show()


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
    plt.show()


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
    plt.show()


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
    plt.show()


# ============================================================================
# RUN ALL ANALYSES
# ============================================================================

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
    
    print("\n" + "="*70)
    print("✅ ALL CHARTS GENERATED!")
    print("="*70)
    print("\nFiles created:")
    print("  1. 1_nodes_vs_distance.png")
    print("  2. 2_average_nodes_all_routes.png")
    print("  3. 3_astar_heuristics_comparison.png")
    print("  4. 4_informed_vs_uninformed.png")
    print("  5. 5_all_routes_detailed.png")
    print("  6. 6_greedy_tradeoff.png")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    # Replace with your actual CSV file path
    csv_file = "AI_data.csv"
    
    # Generate all charts
    generate_all_charts(csv_file)
    
    # Or generate individual charts:
    # plot_nodes_vs_distance(csv_file)
    # plot_average_nodes_all_routes(csv_file)
    # plot_astar_heuristics_comparison(csv_file)
    # plot_informed_vs_uninformed(csv_file)
    # plot_all_routes_detailed(csv_file)
    # plot_greedy_tradeoff(csv_file)