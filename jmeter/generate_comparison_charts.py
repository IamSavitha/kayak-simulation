#!/usr/bin/env python3
"""
Generate comparison charts from JMeter results for presentation
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

def load_results():
    """Load all test results"""
    results_dir = "results"
    configurations = [
        ("base", "B\n(Base)"),
        ("base_s", "B+S\n(+Redis)"),
        ("base_s_k", "B+S+K\n(+Kafka)"),
        ("base_s_k_x", "B+S+K+X\n(All Opts)")
    ]
    
    data = []
    for config_id, config_name in configurations:
        stats_file = f"{results_dir}/{config_id}_report/statistics.json"
        
        if os.path.exists(stats_file):
            with open(stats_file) as f:
                stats = json.load(f)
                overall = stats.get('Total', {})
                
                data.append({
                    'Configuration': config_name,
                    'Total_Requests': overall.get('sampleCount', 0),
                    'Error_Rate': overall.get('errorPct', 0.0),
                    'Avg_Response_Time': overall.get('meanResTime', 0),
                    'PCT95_Response_Time': overall.get('pct3ResTime', 0),
                    'Throughput': overall.get('throughput', 0.0)
                })
    
    return pd.DataFrame(data)

def create_response_time_chart(df, output_dir):
    """Create average response time comparison chart"""
    plt.figure(figsize=(10, 6))
    
    colors = ['#e74c3c', '#f39c12', '#3498db', '#2ecc71']
    bars = plt.bar(df['Configuration'], df['Avg_Response_Time'], color=colors)
    
    plt.xlabel('Configuration', fontsize=12, fontweight='bold')
    plt.ylabel('Average Response Time (ms)', fontsize=12, fontweight='bold')
    plt.title('Average Response Time Comparison\n100 Concurrent Users', 
              fontsize=14, fontweight='bold', pad=20)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)} ms',
                ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/avg_response_time.png', dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_dir}/avg_response_time.png")
    plt.close()

def create_error_rate_chart(df, output_dir):
    """Create error rate comparison chart"""
    plt.figure(figsize=(10, 6))
    
    # Color code: red if > 5%, yellow if 3-5%, green if < 3%
    colors = ['#e74c3c' if x > 5 else '#f39c12' if x > 3 else '#2ecc71' 
              for x in df['Error_Rate']]
    bars = plt.bar(df['Configuration'], df['Error_Rate'], color=colors)
    
    # Add 5% target line
    plt.axhline(y=5.0, color='red', linestyle='--', linewidth=2, 
                label='5% Target Threshold', alpha=0.7)
    
    plt.xlabel('Configuration', fontsize=12, fontweight='bold')
    plt.ylabel('Error Rate (%)', fontsize=12, fontweight='bold')
    plt.title('Error Rate Comparison\nTarget: < 5%', 
              fontsize=14, fontweight='bold', pad=20)
    plt.legend()
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        status = '✅' if height < 5.0 else '❌'
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}% {status}',
                ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/error_rate.png', dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_dir}/error_rate.png")
    plt.close()

def create_throughput_chart(df, output_dir):
    """Create throughput comparison chart"""
    plt.figure(figsize=(10, 6))
    
    colors = ['#e74c3c', '#f39c12', '#3498db', '#2ecc71']
    bars = plt.bar(df['Configuration'], df['Throughput'], color=colors)
    
    plt.xlabel('Configuration', fontsize=12, fontweight='bold')
    plt.ylabel('Throughput (requests/second)', fontsize=12, fontweight='bold')
    plt.title('Throughput Comparison\n100 Concurrent Users', 
              fontsize=14, fontweight='bold', pad=20)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f} req/s',
                ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/throughput.png', dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_dir}/throughput.png")
    plt.close()

def create_percentile_chart(df, output_dir):
    """Create 95th percentile response time chart"""
    plt.figure(figsize=(10, 6))
    
    colors = ['#e74c3c', '#f39c12', '#3498db', '#2ecc71']
    bars = plt.bar(df['Configuration'], df['PCT95_Response_Time'], color=colors)
    
    plt.xlabel('Configuration', fontsize=12, fontweight='bold')
    plt.ylabel('95th Percentile Response Time (ms)', fontsize=12, fontweight='bold')
    plt.title('95th Percentile Response Time Comparison\n100 Concurrent Users', 
              fontsize=14, fontweight='bold', pad=20)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)} ms',
                ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/pct95_response_time.png', dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_dir}/pct95_response_time.png")
    plt.close()

def create_summary_table(df, output_dir):
    """Create a summary table image"""
    fig, ax = plt.subplots(figsize=(14, 4))
    ax.axis('tight')
    ax.axis('off')
    
    # Prepare table data
    table_data = []
    table_data.append(['Configuration', 'Total\nRequests', 'Error\nRate (%)', 
                      'Avg Response\nTime (ms)', '95th %ile\n(ms)', 
                      'Throughput\n(req/s)', 'Status'])
    
    for _, row in df.iterrows():
        status = '✅ PASS' if row['Error_Rate'] < 5.0 else '❌ FAIL'
        table_data.append([
            row['Configuration'].replace('\n', ' '),
            f"{int(row['Total_Requests']):,}",
            f"{row['Error_Rate']:.2f}",
            f"{int(row['Avg_Response_Time'])}",
            f"{int(row['PCT95_Response_Time'])}",
            f"{row['Throughput']:.1f}",
            status
        ])
    
    table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                    colWidths=[0.18, 0.12, 0.12, 0.15, 0.12, 0.13, 0.12])
    
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    
    # Style header row
    for i in range(7):
        cell = table[(0, i)]
        cell.set_facecolor('#3498db')
        cell.set_text_props(weight='bold', color='white')
    
    # Style data rows
    for i in range(1, len(table_data)):
        for j in range(7):
            cell = table[(i, j)]
            if i % 2 == 0:
                cell.set_facecolor('#ecf0f1')
            
            # Highlight pass/fail
            if j == 6:  # Status column
                if 'PASS' in table_data[i][j]:
                    cell.set_facecolor('#2ecc71')
                    cell.set_text_props(weight='bold', color='white')
                else:
                    cell.set_facecolor('#e74c3c')
                    cell.set_text_props(weight='bold', color='white')
    
    plt.title('Performance Test Summary - 100 Concurrent Users', 
              fontsize=14, fontweight='bold', pad=20)
    plt.savefig(f'{output_dir}/summary_table.png', dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_dir}/summary_table.png")
    plt.close()

def main():
    """Generate all comparison charts"""
    print("=" * 60)
    print("GENERATING PERFORMANCE COMPARISON CHARTS")
    print("=" * 60)
    print()
    
    output_dir = "results/charts"
    os.makedirs(output_dir, exist_ok=True)
    
    # Load results
    print("Loading test results...")
    df = load_results()
    
    if df.empty:
        print("❌ No test results found!")
        print("Run tests first with: ./run_all_performance_tests.sh")
        return
    
    print(f"✅ Loaded {len(df)} configurations")
    print()
    
    # Generate charts
    print("Generating charts...")
    create_response_time_chart(df, output_dir)
    create_error_rate_chart(df, output_dir)
    create_throughput_chart(df, output_dir)
    create_percentile_chart(df, output_dir)
    create_summary_table(df, output_dir)
    
    print()
    print("=" * 60)
    print("CHARTS GENERATED SUCCESSFULLY!")
    print("=" * 60)
    print()
    print(f"Output directory: {output_dir}/")
    print()
    print("Files created:")
    print("  1. avg_response_time.png")
    print("  2. error_rate.png")
    print("  3. throughput.png")
    print("  4. pct95_response_time.png")
    print("  5. summary_table.png")
    print()
    print("Use these charts in your presentation!")
    print()

if __name__ == "__main__":
    main()
