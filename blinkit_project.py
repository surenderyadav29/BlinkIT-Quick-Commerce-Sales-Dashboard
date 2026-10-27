# ====================================================================
# PROJECT: PREMIUM BLINKIT QUICK-COMMERCE ANALYTICS DASHBOARD (FIXED)
# TECH STACK: PANDAS, NUMPY, MATPLOTLIB
# ====================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Premium corporate styling implementation
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

# --- 1. DATA LOADING & ROBUST CLEANING (Pandas) ---
try:
    df = pd.read_csv('BlinkIT_Grocery_Data.csv')
except FileNotFoundError:
    df = pd.read_csv('blinkit_data.csv')

# Typos Standardisation
df['Item Fat Content'] = df['Item Fat Content'].replace({
    'low fat': 'Low Fat', 'LF': 'Low Fat', 'reg': 'Regular'
})

# Missing Strings Handling: Blanks ko Unspecified mark karna
df['Outlet Size'] = df['Outlet Size'].fillna('Unspecified')

# Advanced Data Imputation: Weight parameters fill karna
df['Item Weight'] = df.groupby('Item Type')['Item Weight'].transform(lambda x: x.fillna(x.mean()))


# --- 2. ADVANCED MATHEMATICAL ANALYSIS (NumPy) ---
sales_array = df['Sales'].to_numpy()
visibility_array = df['Item Visibility'].to_numpy()

# NumPy Feature Engineering: Mathematical Segmentation using Percentiles
p75_sales = np.percentile(sales_array, 75)
df['Sales_Bracket'] = np.where(df['Sales'] >= p75_sales, 'Premium Tier', 'Standard Tier')

# FIX 1: Item Visibility ko quartile "bins" me todna, kyunki raw scatter
# me visibility vs sales ka correlation ~0 hai (bilkul flat/messy cloud dikhta tha,
# koi trend samajh nahi aata tha). Ab hum visibility ko 4 buckets me baant kar
# average sales dikhayenge -> chart clean aur meaningful ban jayega.
df['Visibility_Bucket'] = pd.qcut(df['Item Visibility'], q=4,
                                   labels=['medium\n(Q1)', 'Low\n(Q2)',
                                           'High\n(Q3)', 'Medium-low\n(Q4)'])
visibility_bucket_sales = df.groupby('Visibility_Bucket', observed=True)['Sales'].mean()

# Data Aggregations (Pandas GroupBy)
category_sales = df.groupby('Item Type')['Sales'].sum().sort_values(ascending=False)

# FIX 2 (v2): Purana chart "Total Sales by Store Size" dikha raha tha, jo
# MISLEADING insight tha. Har size ke records/outlets ki ginti alag hai
# (High=1753 rows/4 outlets, Medium=3631 rows/6, Small=3139 rows/6), isliye
# zyada records wale size ka Total Sales apne aap zyada dikhega -- ismein
# store-size ki asli "performance" ka koi role nahi hai.
# Proof: per-record average sales teeno sizes me practically same hai
# (~₹140), matlab store size ka per-transaction sales pe koi real fark
# nahi padta -- fark sirf record count ka hai.
# FAIR INSIGHT: isliye ab "Average Sales" dikha rahe hain (Total ki jagah),
# jo count-bias hata kar asli tulna deta hai. Order natural (Small->Medium
# ->High), color fixed dictionary se taaki har size ka color consistent rahe.
size_order = ['Small', 'Medium', 'High']
outlet_size_sales_raw = df.groupby('Outlet Size')['Sales'].mean()
outlet_size_sales = outlet_size_sales_raw.reindex(
    [s for s in size_order if s in outlet_size_sales_raw.index]
)
color_map = {'Small': '#72EFDD', 'Medium': '#56CFE1', 'High': '#4EA8DE'}
outlet_colors = [color_map.get(s, '#999999') for s in outlet_size_sales.index]

yearly_sales = df.groupby('Outlet Establishment Year')['Sales'].mean()
bracket_counts = df['Sales_Bracket'].value_counts()


# --- 3. EXECUTE FLAWLESS SYMMETRICAL 2x3 DASHBOARD (Matplotlib) ---
print("\n...Generating Final Verified Dashboard Window...")
fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(18, 11))

fig.suptitle('BlinkIT Executive Sales & Operational Performance Dashboard',
             fontsize=18, fontweight='bold', color='#1A252C')

# [PLOT 1] Top 7 Categories (Bar Chart with Dynamic Labels)
top_7 = category_sales.head(7)
bars = axes[0, 0].bar(top_7.index, top_7.values, color='#2E4057', edgecolor='black', alpha=0.85)
axes[0, 0].set_title('Top 7 Revenue Generating Categories', fontsize=11, fontweight='bold')
axes[0, 0].tick_params(axis='x', rotation=30, labelsize=9)
axes[0, 0].set_ylabel('Total Revenue (₹)')
for bar in bars:
    yval = bar.get_height()
    axes[0, 0].text(bar.get_x() + bar.get_width()/2, yval + 2000, f'₹{yval/1000:.1f}k',
                     ha='center', va='bottom', fontsize=8)

# [PLOT 2] FIXED: Item Visibility vs Sales -> Binned Bar Chart (no more messy scatter)
vb_bars = axes[0, 1].bar(visibility_bucket_sales.index, visibility_bucket_sales.values,
                          color='#E76F51', edgecolor='black', alpha=0.85, width=0.6)
axes[0, 1].set_title('Avg Sales by Item Visibility Level', fontsize=11, fontweight='bold')
axes[0, 1].set_xlabel('Visibility Bucket (Quartiles)')
axes[0, 1].set_ylabel('Average Sales (₹)')
axes[0, 1].tick_params(axis='x', labelsize=8)
for bar in vb_bars:
    yval = bar.get_height()
    axes[0, 1].text(bar.get_x() + bar.get_width()/2, yval + 1, f'₹{yval:.0f}',
                     ha='center', va='bottom', fontsize=8, fontweight='bold')

# [PLOT 3] FIXED: Average Sales by Store Size (fair, count-bias-free comparison)
y_pos = np.arange(len(outlet_size_sales))
hbar = axes[0, 2].barh(y_pos, outlet_size_sales.values, color=outlet_colors,
                        edgecolor='black', height=0.5)
axes[0, 2].set_yticks(y_pos)
axes[0, 2].set_yticklabels(outlet_size_sales.index, fontsize=10, fontweight='bold')
axes[0, 2].set_title('Average Sales per Transaction by Store Size', fontsize=11, fontweight='bold')
axes[0, 2].set_xlabel('Average Sales (₹)')
axes[0, 2].set_xlim(0, max(outlet_size_sales.values) * 1.25)
for i, patch in enumerate(hbar):
    width = patch.get_width()
    axes[0, 2].text(width + (max(outlet_size_sales.values)*0.02), patch.get_y() + patch.get_height()/2,
                     f'₹{width:.1f}', ha='left', va='center',
                     fontsize=9, fontweight='bold')

# [PLOT 4] Sales Density Distribution (Box Plot)
data_to_plot = [df[df['Item Fat Content'] == 'Low Fat']['Sales'],
                df[df['Item Fat Content'] == 'Regular']['Sales']]
box = axes[1, 0].boxplot(data_to_plot, patch_artist=True, tick_labels=['Low Fat', 'Regular'], widths=0.5)
for patch, color in zip(box['boxes'], ['#83C5BE', '#EDF6F9']):
    patch.set_facecolor(color)
axes[1, 0].set_title('Sales Distribution by Fat Content', fontsize=11, fontweight='bold')
axes[1, 0].set_ylabel('Sales (₹)')

# [PLOT 5] Timeline Performance (Shaded Line Chart)
axes[1, 1].plot(yearly_sales.index, yearly_sales.values, marker='o', color='#E63946',
                 linestyle='-', linewidth=2.5, markersize=6)
axes[1, 1].fill_between(yearly_sales.index, yearly_sales.values, color='#E63946', alpha=0.1)
axes[1, 1].set_title('Average Historical Sales Progression', fontsize=11, fontweight='bold')
axes[1, 1].set_xlabel('Store Establishment Year')
axes[1, 1].set_ylabel('Avg Store Ticket (₹)')

# [PLOT 6] Volume Mix Segmentation (Horizontal Bar Chart)
axes[1, 2].barh(bracket_counts.index, bracket_counts.values, color=['#457B9D', '#A8DADC'],
                 edgecolor='black', height=0.5)
axes[1, 2].set_title('Product Volume Mix (NumPy Segmentation)', fontsize=11, fontweight='bold')
axes[1, 2].set_xlabel('Total Order Count')


# --- 4. OVERLAPPING FIXES & PRODUCTION IMAGE EXPORT ---
plt.tight_layout()
plt.subplots_adjust(top=0.90, hspace=0.35, wspace=0.48)

plt.savefig('blinkit_dashboard.png', dpi=300, bbox_inches='tight')
print("🎉 Fixed corporate-ready dashboard saved successfully as 'blinkit_dashboard.png'!")

plt.show()
