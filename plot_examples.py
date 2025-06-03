import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

def show_all_plots():
    # Create a figure with 2x3 subplots with reduced size
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    
    # Time-based metrics (Cycle Time and Lead Time)
    cycle_time_data = {
        'Metric': ['Cycle Time'],
        'Before': [45],
        'After': [15],
        'Unit': ['seconds']
    }
    cycle_time_df = pd.DataFrame(cycle_time_data)
    
    lead_time_data = {
        'Metric': ['Lead Time'],
        'Before': [11.25],
        'After': [1.45],
        'Unit': ['minutes']
    }
    lead_time_df = pd.DataFrame(lead_time_data)
    
    # WIP Inventory metrics
    inventory_data = {
        'Metric': ['WIP Inventory'],
        'Before': [15],
        'After': [5],
        'Unit': ['units']
    }
    inventory_df = pd.DataFrame(inventory_data)
    
    # Percentage-based metrics
    percentage_data = {
        'Metric': ['Quality Rate', 'Machine Utilization'],
        'Before': [92, 65],
        'After': [98, 85],
        'Unit': ['%', '%']
    }
    percentage_df = pd.DataFrame(percentage_data)
    
    # Space Utilization metrics
    space_data = {
        'Metric': ['Space Utilization'],
        'Before': [1000],
        'After': [400],
        'Unit': ['sq ft']
    }
    space_df = pd.DataFrame(space_data)
    
    # Set style for all plots
    sns.set_style("whitegrid")
    plt.rcParams['font.size'] = 8
    plt.rcParams['axes.titlesize'] = 10
    plt.rcParams['axes.labelsize'] = 8
    
    # Plot Cycle Time (top left)
    sns.barplot(data=cycle_time_df.melt(id_vars=['Metric', 'Unit'], value_vars=['Before', 'After']), 
                x='Metric', y='value', hue='variable', palette='Set2', ax=axes[0,0])
    axes[0,0].set_title('Cycle Time', pad=10, fontsize=10)
    axes[0,0].set_xlabel('Metric', fontsize=8)
    axes[0,0].set_ylabel('Seconds', fontsize=8)
    axes[0,0].legend(title='Time Period', fontsize=7, title_fontsize=8)
    for i, (metric, unit) in enumerate(zip(cycle_time_df['Metric'], cycle_time_df['Unit'])):
        axes[0,0].text(i, cycle_time_df['After'][i], f"{unit}", ha='center', va='bottom', fontsize=7)
    
    # Plot Lead Time (top middle)
    sns.barplot(data=lead_time_df.melt(id_vars=['Metric', 'Unit'], value_vars=['Before', 'After']), 
                x='Metric', y='value', hue='variable', palette='Set2', ax=axes[0,1])
    axes[0,1].set_title('Lead Time', pad=10, fontsize=10)
    axes[0,1].set_xlabel('Metric', fontsize=8)
    axes[0,1].set_ylabel('Minutes', fontsize=8)
    axes[0,1].legend(title='Time Period', fontsize=7, title_fontsize=8)
    for i, (metric, unit) in enumerate(zip(lead_time_df['Metric'], lead_time_df['Unit'])):
        axes[0,1].text(i, lead_time_df['After'][i], f"{unit}", ha='center', va='bottom', fontsize=7)
    
    # Plot WIP Inventory (top right)
    sns.barplot(data=inventory_df.melt(id_vars=['Metric', 'Unit'], value_vars=['Before', 'After']), 
                x='Metric', y='value', hue='variable', palette='Set2', ax=axes[0,2])
    axes[0,2].set_title('WIP Inventory', pad=10, fontsize=10)
    axes[0,2].set_xlabel('Metric', fontsize=8)
    axes[0,2].set_ylabel('Units', fontsize=8)
    axes[0,2].legend(title='Time Period', fontsize=7, title_fontsize=8)
    for i, (metric, unit) in enumerate(zip(inventory_df['Metric'], inventory_df['Unit'])):
        axes[0,2].text(i, inventory_df['After'][i], f"{unit}", ha='center', va='bottom', fontsize=7)
    
    # Plot Percentage Metrics (bottom left)
    sns.barplot(data=percentage_df.melt(id_vars=['Metric', 'Unit'], value_vars=['Before', 'After']), 
                x='Metric', y='value', hue='variable', palette='Set2', ax=axes[1,0])
    axes[1,0].set_title('Percentage-based Metrics', pad=10, fontsize=10)
    axes[1,0].set_xlabel('Metrics', fontsize=8)
    axes[1,0].set_ylabel('Percentage (%)', fontsize=8)
    axes[1,0].tick_params(axis='x', rotation=45, labelsize=8)
    axes[1,0].legend(title='Time Period', fontsize=7, title_fontsize=8)
    for i, (metric, unit) in enumerate(zip(percentage_df['Metric'], percentage_df['Unit'])):
        axes[1,0].text(i, percentage_df['After'][i], f"{unit}", ha='center', va='bottom', fontsize=7)
    
    # Plot Space Utilization (bottom middle)
    sns.barplot(data=space_df.melt(id_vars=['Metric', 'Unit'], value_vars=['Before', 'After']), 
                x='Metric', y='value', hue='variable', palette='Set2', ax=axes[1,1])
    axes[1,1].set_title('Space Utilization', pad=10, fontsize=10)
    axes[1,1].set_xlabel('Metric', fontsize=8)
    axes[1,1].set_ylabel('Square Feet', fontsize=8)
    axes[1,1].legend(title='Time Period', fontsize=7, title_fontsize=8)
    for i, (metric, unit) in enumerate(zip(space_df['Metric'], space_df['Unit'])):
        axes[1,1].text(i, space_df['After'][i], f"{unit}", ha='center', va='bottom', fontsize=7)
    
    # Hide the last subplot (bottom right)
    axes[1,2].set_visible(False)
    
    # Adjust layout and show
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    show_all_plots()
