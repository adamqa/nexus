import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
import warnings
warnings.filterwarnings('ignore')

# ── Style ─────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    'font.family'      : 'DejaVu Sans',
    'axes.spines.top'  : False,
    'axes.spines.right': False,
    'axes.grid'        : True,
    'grid.alpha'       : 0.3,
    'grid.linestyle'   : '--',
    'figure.dpi'       : 150,
})

PRIMARY  = '#003366'
ACCENT   = '#0066CC'
RED      = '#CC0000'
ORANGE   = '#CC6600'
YELLOW   = '#CC9900'
GREEN    = '#006600'
LIGHT_BG = '#F5F8FF'

# ══════════════════════════════════════════════════════════════════════════════
# STEP 1 — LOAD DATA
# ══════════════════════════════════════════════════════════════════════════════
print("="*60)
print("  STEP 1 — LOADING DATA")
print("="*60)

# Load from Excel or CSV — works with both
try:
    df_p = pd.read_excel('products_clean.xlsx')
    print("  Loaded products_clean.xlsx")
except:
    df_p = pd.read_csv('products_clean.csv')
    print("  Loaded products_clean.csv")

try:
    df_c = pd.read_excel('consumption_clean.xlsx')
    print("  Loaded consumption_clean.xlsx")
except:
    df_c = pd.read_csv('consumption_clean.csv')
    print("  Loaded consumption_clean.csv")

print(f"\n  Products    : {len(df_p):,} rows x {df_p.shape[1]} columns")
print(f"  Consumption : {len(df_c):,} rows x {df_c.shape[1]} columns")
print(f"\n  Products columns   : {list(df_p.columns)}")
print(f"  Consumption columns: {list(df_c.columns)}")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 2 — NORMALIZATION
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("  STEP 2 — NORMALIZATION (Min-Max Scaling)")
print("="*60)

risk_variables = [
    'criticality',
    'substitutability',
    'avg_lead_time',
    'lead_time_std',
    'nb_suppliers',
    'demand_variability',
    'stockout_history',
]

# Variables where higher = lower risk (need to be inverted)
vars_to_invert = ['substitutability', 'nb_suppliers']

scaler = MinMaxScaler()
df_norm = df_p[risk_variables].copy()
df_norm_scaled = pd.DataFrame(
    scaler.fit_transform(df_norm),
    columns=[f'{col}_norm' for col in risk_variables]
)

# Invert direction for substitutability and nb_suppliers
for col in vars_to_invert:
    df_norm_scaled[f'{col}_norm'] = 1 - df_norm_scaled[f'{col}_norm']

# Add normalized columns to main dataframe
df_p = pd.concat([df_p, df_norm_scaled], axis=1)

print(f"\n  Variables normalized : {len(risk_variables)}")
print(f"  Variables inverted   : {vars_to_invert}")
print(f"\n  Normalization check (all values should be 0-1):")
for col in [f'{v}_norm' for v in risk_variables]:
    mn = df_p[col].min()
    mx = df_p[col].max()
    print(f"    {col:<30} min={mn:.3f}  max={mx:.3f}")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 3 — WEIGHTED RISK SCORING (RRS)
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("  STEP 3 — WEIGHTED RISK SCORING (RRS)")
print("="*60)

weights = {
    'criticality'       : 0.25,
    'substitutability'  : 0.20,
    'avg_lead_time'     : 0.15,
    'lead_time_std'     : 0.15,
    'nb_suppliers'      : 0.10,
    'demand_variability': 0.10,
    'stockout_history'  : 0.05,
}

print(f"\n  Weight table:")
print(f"  {'Variable':<25} {'Weight':>8}")
print(f"  {'-'*35}")
for var, w in weights.items():
    print(f"  {var:<25} {w:>8.2f}")
print(f"  {'-'*35}")
print(f"  {'TOTAL':<25} {sum(weights.values()):>8.2f}")

# Calculate RRS
df_p['RRS'] = sum(
    weights[col] * df_p[f'{col}_norm']
    for col in weights.keys()
)

print(f"\n  RRS Statistics:")
print(f"    Min    : {df_p['RRS'].min():.4f}")
print(f"    Max    : {df_p['RRS'].max():.4f}")
print(f"    Mean   : {df_p['RRS'].mean():.4f}")
print(f"    Median : {df_p['RRS'].median():.4f}")
print(f"    Std    : {df_p['RRS'].std():.4f}")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 4 — RISK CLASSIFICATION (Percentile-Based Boundaries)
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("  STEP 4 — RISK CLASSIFICATION")
print("="*60)

p80 = df_p['RRS'].quantile(0.80)
p50 = df_p['RRS'].quantile(0.50)
p20 = df_p['RRS'].quantile(0.20)

print(f"\n  Percentile-based boundaries:")
print(f"    P80 (R1 threshold) : {p80:.4f}")
print(f"    P50 (R2 threshold) : {p50:.4f}")
print(f"    P20 (R4 threshold) : {p20:.4f}")

def classify_risk(rrs):
    if rrs >= p80:   return 'R1'
    elif rrs >= p50: return 'R2'
    elif rrs >= p20: return 'R3'
    else:            return 'R4'

df_p['risk_class'] = df_p['RRS'].apply(classify_risk)

print(f"\n  Classification results:")
risk_dist = df_p['risk_class'].value_counts().reindex(['R1','R2','R3','R4'])
for cls, cnt in risk_dist.items():
    pct = cnt / len(df_p) * 100
    label = {'R1':'Critical','R2':'High','R3':'Moderate','R4':'Low'}[cls]
    print(f"    {cls} ({label:<10}) : {cnt:>4} products  ({pct:.1f}%)")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 5 — ABC vs RISK CLASS COMPARISON (Key Finding)
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("  STEP 5 — ABC vs AI RISK CLASS COMPARISON")
print("="*60)

cross_tab = pd.crosstab(
    df_p['abc_class'],
    df_p['risk_class'],
    margins=True
)
print(f"\n  Cross-tabulation ABC Class vs AI Risk Class:")
print(cross_tab.to_string())

# Key finding
products_ruptured = df_c.groupby('product_id')['rupture_flag'].sum()
ruptured_ids      = products_ruptured[products_ruptured > 0].index
ruptured_abc_dist = df_p[df_p['product_id'].isin(ruptured_ids)]\
    ['abc_class'].value_counts(normalize=True) * 100

print(f"\n  KEY FINDING:")
print(f"  ABC class distribution of products that ruptured:")
for cls, pct in ruptured_abc_dist.items():
    print(f"    Class {cls} : {pct:.1f}%")

pct_C = ruptured_abc_dist.get('C', 0)
print(f"\n  => {pct_C:.1f}% of ruptured products were ABC Class C")
print(f"     (received MINIMAL attention under current system)")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 6 — INVENTORY POLICY PER RISK CLASS
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("  STEP 6 — INVENTORY POLICY CALCULATION")
print("="*60)

# Z factors per risk class
z_factors = {'R1': 3.09, 'R2': 2.05, 'R3': 1.65, 'R4': 1.28}

# Merge with consumption for demand stats
demand_stats = df_c.groupby('product_id').agg(
    mean_demand = ('consumption', 'mean'),
    std_demand  = ('consumption', 'std'),
).reset_index()

df_p = df_p.merge(demand_stats, on='product_id', how='left')

# Calculate Safety Stock and ROP
df_p['Z'] = df_p['risk_class'].map(z_factors)

df_p['safety_stock'] = (
    df_p['Z'] * np.sqrt(
        df_p['avg_lead_time']/7 * df_p['std_demand']**2 +
        df_p['mean_demand']**2  * (df_p['lead_time_std']/7)**2
    )
).round(2)

df_p['reorder_point'] = (
    df_p['mean_demand'] * df_p['avg_lead_time']/7 + df_p['safety_stock']
).round(2)

print(f"\n  Average inventory parameters per risk class:")
policy_summary = df_p.groupby('risk_class').agg(
    Z_factor       = ('Z', 'first'),
    avg_SS         = ('safety_stock', 'mean'),
    avg_ROP        = ('reorder_point', 'mean'),
    nb_products    = ('product_id', 'count')
).reindex(['R1','R2','R3','R4']).round(2)

print(policy_summary.to_string())

# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 1 — RRS DISTRIBUTION WITH CLASS BOUNDARIES
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("  GENERATING CHARTS")
print("="*60)

fig1, ax1 = plt.subplots(figsize=(12, 5))
fig1.patch.set_facecolor(LIGHT_BG)
ax1.set_facecolor('white')

ax1.hist(df_p['RRS'], bins=60, color=ACCENT,
         alpha=0.7, edgecolor='white', linewidth=0.5)

ax1.axvline(p80, color=RED,    linestyle='--', linewidth=2,
            label=f'R1 boundary — P80 ({p80:.3f})')
ax1.axvline(p50, color=ORANGE, linestyle='--', linewidth=2,
            label=f'R2 boundary — P50 ({p50:.3f})')
ax1.axvline(p20, color=GREEN,  linestyle='--', linewidth=2,
            label=f'R4 boundary — P20 ({p20:.3f})')

ymax = ax1.get_ylim()[1]
ax1.fill_betweenx([0, ymax], p80, df_p['RRS'].max(),
                  alpha=0.08, color=RED)
ax1.fill_betweenx([0, ymax], p50, p80,
                  alpha=0.08, color=ORANGE)
ax1.fill_betweenx([0, ymax], p20, p50,
                  alpha=0.08, color=YELLOW)
ax1.fill_betweenx([0, ymax], df_p['RRS'].min(), p20,
                  alpha=0.08, color=GREEN)

ax1.text((p80 + df_p['RRS'].max())/2, ymax*0.85,
         'R1\nCritical', ha='center', fontsize=10,
         fontweight='bold', color=RED)
ax1.text((p50 + p80)/2, ymax*0.85,
         'R2\nHigh', ha='center', fontsize=10,
         fontweight='bold', color=ORANGE)
ax1.text((p20 + p50)/2, ymax*0.85,
         'R3\nModerate', ha='center', fontsize=10,
         fontweight='bold', color=YELLOW)
ax1.text((df_p['RRS'].min() + p20)/2, ymax*0.85,
         'R4\nLow', ha='center', fontsize=10,
         fontweight='bold', color=GREEN)

ax1.set_title('RRS Score Distribution with Risk Class Boundaries\n'
              f'(3,500 products — boundaries at P20={p20:.3f}, '
              f'P50={p50:.3f}, P80={p80:.3f})',
              fontsize=12, fontweight='bold', color=PRIMARY)
ax1.set_xlabel('Rupture Risk Score (RRS)', fontsize=10)
ax1.set_ylabel('Number of Products', fontsize=10)
ax1.legend(fontsize=9)

plt.tight_layout()
plt.savefig('classification_fig1_rrs_distribution.png',
            dpi=150, bbox_inches='tight', facecolor=LIGHT_BG)
plt.close()
print("  Saved classification_fig1_rrs_distribution.png")

# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 2 — ABC vs RISK CLASS HEATMAP
# ══════════════════════════════════════════════════════════════════════════════
fig2, ax2 = plt.subplots(figsize=(8, 5))
fig2.patch.set_facecolor(LIGHT_BG)
ax2.set_facecolor('white')

cross_matrix = pd.crosstab(df_p['abc_class'], df_p['risk_class'])\
    .reindex(columns=['R1','R2','R3','R4'])

sns.heatmap(cross_matrix,
            annot=True, fmt='d', annot_kws={'size': 12, 'weight': 'bold'},
            cmap='YlOrRd', ax=ax2,
            linewidths=1, linecolor='white',
            cbar_kws={'shrink': 0.8})

ax2.set_title('ABC Class vs AI Risk Class — Cross Tabulation\n'
              '(High values in ABC=C / Risk=R1 or R2 prove ABC blindness)',
              fontsize=11, fontweight='bold', color=PRIMARY)
ax2.set_xlabel('AI Risk Class', fontsize=10)
ax2.set_ylabel('ABC Class', fontsize=10)

plt.tight_layout()
plt.savefig('classification_fig2_abc_vs_risk.png',
            dpi=150, bbox_inches='tight', facecolor=LIGHT_BG)
plt.close()
print("  Saved classification_fig2_abc_vs_risk.png")

# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 3 — RISK CLASS DISTRIBUTION BAR CHART
# ══════════════════════════════════════════════════════════════════════════════
fig3, axes3 = plt.subplots(1, 2, figsize=(14, 5))
fig3.patch.set_facecolor(LIGHT_BG)
fig3.suptitle('Classification Results',
              fontsize=13, fontweight='bold', color=PRIMARY)

# Bar chart — count per class
ax = axes3[0]
ax.set_facecolor('white')
risk_counts = df_p['risk_class'].value_counts().reindex(['R1','R2','R3','R4'])
colors      = [RED, ORANGE, YELLOW, GREEN]
bars = ax.bar(['R1\nCritical','R2\nHigh','R3\nModerate','R4\nLow'],
              risk_counts.values,
              color=colors, edgecolor='white', linewidth=1.5)
for bar, val in zip(bars, risk_counts.values):
    ax.text(bar.get_x() + bar.get_width()/2,
            bar.get_height() + 10,
            f'{val:,}', ha='center', va='bottom',
            fontsize=11, fontweight='bold')
ax.set_title('Number of Products per Risk Class',
             fontsize=11, fontweight='bold', color=PRIMARY)
ax.set_ylabel('Number of Products')

# Scatter — RRS vs Lead Time colored by class
ax2 = axes3[1]
ax2.set_facecolor('white')
color_map = {'R1': RED, 'R2': ORANGE, 'R3': YELLOW, 'R4': GREEN}
for cls in ['R4', 'R3', 'R2', 'R1']:
    subset = df_p[df_p['risk_class'] == cls]
    ax2.scatter(subset['avg_lead_time'], subset['RRS'],
                c=color_map[cls], alpha=0.4, s=8,
                label=f'{cls} ({len(subset):,})')
ax2.set_title('RRS Score vs Lead Time\nby Risk Class',
              fontsize=11, fontweight='bold', color=PRIMARY)
ax2.set_xlabel('Average Lead Time (days)')
ax2.set_ylabel('RRS Score')
ax2.legend(fontsize=9, markerscale=3)

plt.tight_layout()
plt.savefig('classification_fig3_results.png',
            dpi=150, bbox_inches='tight', facecolor=LIGHT_BG)
plt.close()
print("  Saved classification_fig3_results.png")

# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 4 — INVENTORY POLICY COMPARISON
# ══════════════════════════════════════════════════════════════════════════════
fig4, axes4 = plt.subplots(1, 2, figsize=(14, 5))
fig4.patch.set_facecolor(LIGHT_BG)
fig4.suptitle('Differentiated Inventory Policy per Risk Class',
              fontsize=13, fontweight='bold', color=PRIMARY)

# Average Safety Stock per class
ax = axes4[0]
ax.set_facecolor('white')
ss_per_class = df_p.groupby('risk_class')['safety_stock']\
    .mean().reindex(['R1','R2','R3','R4'])
bars = ax.bar(['R1','R2','R3','R4'],
              ss_per_class.values,
              color=colors, edgecolor='white', linewidth=1.5)
for bar, val in zip(bars, ss_per_class.values):
    ax.text(bar.get_x() + bar.get_width()/2,
            bar.get_height() + 0.3,
            f'{val:.1f}', ha='center', va='bottom',
            fontsize=11, fontweight='bold')
ax.set_title('Average Safety Stock per Risk Class\n(units)',
             fontsize=11, fontweight='bold', color=PRIMARY)
ax.set_ylabel('Safety Stock (units)')

# Average ROP per class
ax2 = axes4[1]
ax2.set_facecolor('white')
rop_per_class = df_p.groupby('risk_class')['reorder_point']\
    .mean().reindex(['R1','R2','R3','R4'])
bars2 = ax2.bar(['R1','R2','R3','R4'],
                rop_per_class.values,
                color=colors, edgecolor='white', linewidth=1.5)
for bar, val in zip(bars2, rop_per_class.values):
    ax2.text(bar.get_x() + bar.get_width()/2,
             bar.get_height() + 0.3,
             f'{val:.1f}', ha='center', va='bottom',
             fontsize=11, fontweight='bold')
ax2.set_title('Average Reorder Point per Risk Class\n(units)',
              fontsize=11, fontweight='bold', color=PRIMARY)
ax2.set_ylabel('Reorder Point (units)')

plt.tight_layout()
plt.savefig('classification_fig4_policy.png',
            dpi=150, bbox_inches='tight', facecolor=LIGHT_BG)
plt.close()
print("  Saved classification_fig4_policy.png")

# ══════════════════════════════════════════════════════════════════════════════
# EXPORT RESULTS
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("  EXPORTING RESULTS")
print("="*60)

# Final classified products table
output_cols = [
    'product_id', 'archetype', 'abc_class',
    'criticality', 'substitutability', 'avg_lead_time',
    'lead_time_std', 'nb_suppliers', 'demand_variability',
    'stockout_history', 'RRS', 'risk_class',
    'Z', 'safety_stock', 'reorder_point'
]
df_output = df_p[output_cols].copy()

with pd.ExcelWriter('classification_results.xlsx',
                    engine='openpyxl') as writer:

    # Sheet 1 — Full classified products
    df_output.to_excel(writer,
                       sheet_name='Classified Products', index=False)

    # Sheet 2 — R1 products only (most critical)
    df_output[df_output['risk_class'] == 'R1']\
        .sort_values('RRS', ascending=False)\
        .to_excel(writer, sheet_name='R1 Critical Products', index=False)

    # Sheet 3 — Policy summary
    policy_export = pd.DataFrame({
        'Risk Class'      : ['R1', 'R2', 'R3', 'R4'],
        'Label'           : ['Critical', 'High', 'Moderate', 'Low'],
        'Service Level'   : ['99.9%', '98.0%', '95.0%', '90.0%'],
        'Z Factor'        : [3.09, 2.05, 1.65, 1.28],
        'Review Frequency': ['Continuous', 'Weekly', 'Bi-weekly', 'Monthly'],
        'Avg Safety Stock': policy_summary['avg_SS'].values,
        'Avg ROP'         : policy_summary['avg_ROP'].values,
        'Nb Products'     : policy_summary['nb_products'].values,
    })
    policy_export.to_excel(writer,
                           sheet_name='Inventory Policy', index=False)

    # Sheet 4 — ABC vs Risk Cross Tab
    cross_tab.to_excel(writer, sheet_name='ABC vs Risk Class')

print("  Saved classification_results.xlsx")
print("\n" + "="*60)
print("  CLASSIFICATION COMPLETE")
print("="*60)
print(f"\n  Total products classified : {len(df_p):,}")
print(f"  R1 Critical               : {(df_p['risk_class']=='R1').sum():,}")
print(f"  R2 High                   : {(df_p['risk_class']=='R2').sum():,}")
print(f"  R3 Moderate               : {(df_p['risk_class']=='R3').sum():,}")
print(f"  R4 Low                    : {(df_p['risk_class']=='R4').sum():,}")
print(f"\n  Key Finding               : {pct_C:.1f}% of ruptured products = ABC Class C")
print(f"  Output file               : classification_results.xlsx")
print(f"  Charts saved              : 4 PNG files")
