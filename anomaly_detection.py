import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# ══════════════════════════════════════════════════════════════════════════════
# STEP 1 — LOAD DATA
# ══════════════════════════════════════════════════════════════════════════════
print("="*60)
print("  STEP 1 — LOADING DATA")
print("="*60)

# Load classification results
try:
    df_classified = pd.read_excel('classification_results.xlsx',
                                  sheet_name='Classified Products')
    print("  Loaded classification_results.xlsx")
except:
    df_classified = pd.read_csv('classification_results.csv')
    print("  Loaded classification_results.csv")

# Load consumption
try:
    df_c = pd.read_excel('consumption_clean.xlsx')
    print("  Loaded consumption_clean.xlsx")
except:
    df_c = pd.read_csv('consumption_clean.csv')
    print("  Loaded consumption_clean.csv")

print(f"\n  Classified products : {len(df_classified):,} rows")
print(f"  Consumption records : {len(df_c):,} rows")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 2 — FILTER R1 AND R2 PRODUCTS ONLY
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("  STEP 2 — FILTERING R1 AND R2 PRODUCTS")
print("="*60)

r1r2_products = df_classified[
    df_classified['risk_class'].isin(['R1', 'R2'])
][['product_id', 'risk_class', 'RRS']].copy()

print(f"\n  R1 products : {(r1r2_products['risk_class']=='R1').sum():,}")
print(f"  R2 products : {(r1r2_products['risk_class']=='R2').sum():,}")
print(f"  Total       : {len(r1r2_products):,} products to monitor")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 3 — MERGE CLASSIFICATION WITH CONSUMPTION
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("  STEP 3 — MERGING TABLES")
print("="*60)

df_merged = df_c.merge(r1r2_products, on='product_id', how='inner')
df_merged = df_merged.sort_values(['product_id', 'week']).reset_index(drop=True)

print(f"\n  Merged table rows   : {len(df_merged):,}")
print(f"  Merged table cols   : {list(df_merged.columns)}")
print(f"  Products covered    : {df_merged['product_id'].nunique():,}")
print(f"  Weeks covered       : {df_merged['week'].min()} to {df_merged['week'].max()}")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 4 — FEATURE ENGINEERING
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("  STEP 4 — FEATURE ENGINEERING")
print("="*60)

# For each product compute rolling features that help Isolation Forest
# detect anomalies more accurately
df_merged = df_merged.sort_values(['product_id', 'week'])

# Rolling mean and std over last 4 weeks
df_merged['rolling_mean_4w'] = df_merged.groupby('product_id')['consumption']\
    .transform(lambda x: x.rolling(4, min_periods=1).mean())

df_merged['rolling_std_4w'] = df_merged.groupby('product_id')['consumption']\
    .transform(lambda x: x.rolling(4, min_periods=1).std().fillna(0))

# Deviation from rolling mean
df_merged['deviation'] = df_merged['consumption'] - df_merged['rolling_mean_4w']

# Week over week change
df_merged['wow_change'] = df_merged.groupby('product_id')['consumption']\
    .transform(lambda x: x.pct_change().fillna(0))

# Stock level ratio (how full is the stock relative to recent consumption)
df_merged['stock_consumption_ratio'] = (
    df_merged['stock_level'] /
    df_merged['rolling_mean_4w'].replace(0, np.nan)
).fillna(0)

print(f"\n  Features created:")
features = ['consumption', 'rolling_mean_4w', 'rolling_std_4w',
            'deviation', 'wow_change', 'stock_consumption_ratio']
for f in features:
    print(f"    {f}")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 5 — ISOLATION FOREST ANOMALY DETECTION
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("  STEP 5 — ISOLATION FOREST MODEL")
print("="*60)

# Features for the model
X = df_merged[features].copy()

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train Isolation Forest
model = IsolationForest(
    contamination=0.05,   # expect 5% of weeks to be anomalous
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)

print("\n  Training Isolation Forest...")
print(f"    contamination : 5% (expected anomaly rate)")
print(f"    n_estimators  : 100 trees")
print(f"    input shape   : {X_scaled.shape}")

model.fit(X_scaled)

# Predict: -1 = anomaly, 1 = normal
df_merged['anomaly_prediction'] = model.predict(X_scaled)
df_merged['anomaly_score']      = model.decision_function(X_scaled)

# Convert: 1 = anomaly (easier to read), 0 = normal
df_merged['is_anomaly'] = (df_merged['anomaly_prediction'] == -1).astype(int)

print(f"\n  Model trained successfully")
print(f"  Total weeks analyzed    : {len(df_merged):,}")
print(f"  Anomalies detected      : {df_merged['is_anomaly'].sum():,}")
print(f"  Anomaly rate            : {df_merged['is_anomaly'].mean()*100:.1f}%")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 6 — ALERT CLASSIFICATION (3 RULES)
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("  STEP 6 — ALERT CLASSIFICATION")
print("="*60)

def classify_alert(row):
    if row['is_anomaly'] == 0:
        return 'GREEN'
    # Red — spike: consumption more than 2x rolling mean
    if row['consumption'] > 2 * row['rolling_mean_4w']:
        return 'RED'
    # Orange — strong upward change week over week
    if row['wow_change'] > 0.5:
        return 'ORANGE'
    # Yellow — moderate anomaly
    return 'YELLOW'

df_merged['alert_level'] = df_merged.apply(classify_alert, axis=1)

alert_summary = df_merged['alert_level'].value_counts()
print(f"\n  Alert distribution:")
for level in ['RED', 'ORANGE', 'YELLOW', 'GREEN']:
    cnt = alert_summary.get(level, 0)
    pct = cnt / len(df_merged) * 100
    print(f"    {level:<8} : {cnt:>6,} weeks  ({pct:.1f}%)")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 7 — RESULTS ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("  STEP 7 — RESULTS ANALYSIS")
print("="*60)

# Anomalies by risk class
print("\n  Anomalies by risk class:")
anomaly_by_class = df_merged[df_merged['is_anomaly']==1]\
    .groupby('risk_class')['is_anomaly'].count()
for cls, cnt in anomaly_by_class.items():
    total = (df_merged['risk_class']==cls).sum()
    pct   = cnt / total * 100
    print(f"    {cls} : {cnt:,} anomalous weeks out of {total:,} ({pct:.1f}%)")

# Products with most anomalies
print("\n  Top 10 products with most anomaly weeks:")
top_anomalies = df_merged[df_merged['is_anomaly']==1]\
    .groupby(['product_id','risk_class'])['is_anomaly']\
    .sum().sort_values(ascending=False).head(10)
for (pid, cls), cnt in top_anomalies.items():
    print(f"    {pid}  {cls}  {cnt} anomalous weeks")

# Anomaly weeks that coincide with actual ruptures
anomaly_with_rupture = df_merged[
    (df_merged['is_anomaly']==1) &
    (df_merged['rupture_flag']==1)
]
print(f"\n  Anomaly weeks that led to rupture  : {len(anomaly_with_rupture):,}")
print(f"  Total rupture events in R1/R2      : {df_merged['rupture_flag'].sum():,}")
if df_merged['rupture_flag'].sum() > 0:
    detection_rate = len(anomaly_with_rupture) / df_merged['rupture_flag'].sum() * 100
    print(f"  Rupture detection rate             : {detection_rate:.1f}%")

# Last week status (week 104) — current alert status
print("\n  Current alert status (last week — week 104):")
last_week = df_merged[df_merged['week'] == df_merged['week'].max()]
last_alerts = last_week['alert_level'].value_counts()
for level in ['RED', 'ORANGE', 'YELLOW', 'GREEN']:
    cnt = last_alerts.get(level, 0)
    print(f"    {level:<8} : {cnt:>4} products")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 8 — EXPORT RESULTS
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("  STEP 8 — EXPORTING RESULTS")
print("="*60)

# Full anomaly results
anomaly_output = df_merged[[
    'product_id', 'risk_class', 'RRS', 'week',
    'consumption', 'rolling_mean_4w', 'deviation',
    'stock_level', 'rupture_flag',
    'anomaly_score', 'is_anomaly', 'alert_level'
]].copy()

# Products currently in alert (last week)
products_in_alert = last_week[last_week['alert_level'] != 'GREEN'][[
    'product_id', 'risk_class', 'RRS',
    'consumption', 'stock_level', 'alert_level', 'anomaly_score'
]].sort_values(['alert_level', 'RRS'], ascending=[True, False])

# Summary per product
product_summary = df_merged.groupby(['product_id', 'risk_class']).agg(
    RRS              = ('RRS', 'first'),
    total_weeks      = ('week', 'count'),
    anomaly_weeks    = ('is_anomaly', 'sum'),
    rupture_weeks    = ('rupture_flag', 'sum'),
    red_alerts       = ('alert_level', lambda x: (x=='RED').sum()),
    orange_alerts    = ('alert_level', lambda x: (x=='ORANGE').sum()),
    yellow_alerts    = ('alert_level', lambda x: (x=='YELLOW').sum()),
    avg_consumption  = ('consumption', 'mean'),
    max_consumption  = ('consumption', 'max'),
).reset_index().sort_values('anomaly_weeks', ascending=False)

with pd.ExcelWriter('anomaly_detection_results.xlsx',
                    engine='openpyxl') as writer:

    anomaly_output.to_excel(
        writer, sheet_name='Full Anomaly Results', index=False)

    product_summary.to_excel(
        writer, sheet_name='Product Summary', index=False)

    products_in_alert.to_excel(
        writer, sheet_name='Current Alerts Week 104', index=False)

    # Alert summary sheet
    alert_df = pd.DataFrame({
        'Alert Level' : ['RED', 'ORANGE', 'YELLOW', 'GREEN'],
        'Meaning'     : ['Consumption spike > 2x mean',
                         'Strong week-over-week increase > 50%',
                         'Moderate anomaly detected by AI',
                         'Normal consumption'],
        'Total Weeks' : [alert_summary.get(l, 0)
                         for l in ['RED','ORANGE','YELLOW','GREEN']],
        'Action'      : ['Immediate emergency reorder',
                         'Check stock vs reorder point',
                         'Monitor closely next week',
                         'No action required'],
    })
    alert_df.to_excel(writer, sheet_name='Alert Legend', index=False)

print("  Saved anomaly_detection_results.xlsx")
print("\n" + "="*60)
print("  ANOMALY DETECTION COMPLETE")
print("="*60)
print(f"\n  Products monitored    : {df_merged['product_id'].nunique():,}")
print(f"  Total weeks analyzed  : {len(df_merged):,}")
print(f"  Anomalies detected    : {df_merged['is_anomaly'].sum():,}")
print(f"  RED alerts            : {(df_merged['alert_level']=='RED').sum():,}")
print(f"  ORANGE alerts         : {(df_merged['alert_level']=='ORANGE').sum():,}")
print(f"  YELLOW alerts         : {(df_merged['alert_level']=='YELLOW').sum():,}")
print(f"  Output file           : anomaly_detection_results.xlsx")
