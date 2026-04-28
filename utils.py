import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler, MinMaxScaler

def run_classification_logic(df_p, df_c):
    risk_variables = ['criticality', 'substitutability', 'avg_lead_time', 'lead_time_std', 'nb_suppliers', 'demand_variability', 'stockout_history']
    vars_to_invert = ['substitutability', 'nb_suppliers']
    
    scaler = MinMaxScaler()
    df_norm = df_p[risk_variables].copy()
    df_norm_scaled = pd.DataFrame(scaler.fit_transform(df_norm), columns=[f'{col}_norm' for col in risk_variables])
    
    for col in vars_to_invert:
        df_norm_scaled[f'{col}_norm'] = 1 - df_norm_scaled[f'{col}_norm']
    
    df_p = pd.concat([df_p.reset_index(drop=True), df_norm_scaled], axis=1)
    
    weights = {'criticality': 0.25, 'substitutability': 0.20, 'avg_lead_time': 0.15, 'lead_time_std': 0.15, 'nb_suppliers': 0.10, 'demand_variability': 0.10, 'stockout_history': 0.05}
    df_p['RRS'] = sum(weights[col] * df_p[f'{col}_norm'] for col in weights.keys())
    
    p80, p50, p20 = df_p['RRS'].quantile([0.8, 0.5, 0.2])
    def classify_risk(rrs):
        if rrs >= p80: return 'R1'
        elif rrs >= p50: return 'R2'
        elif rrs >= p20: return 'R3'
        else: return 'R4'
    
    df_p['risk_class'] = df_p['RRS'].apply(classify_risk)
    
    z_factors = {'R1': 3.09, 'R2': 2.05, 'R3': 1.65, 'R4': 1.28}
    demand_stats = df_c.groupby('product_id').agg(mean_demand=('consumption', 'mean'), std_demand=('consumption', 'std')).reset_index()
    df_p = df_p.merge(demand_stats, on='product_id', how='left')
    df_p['Z'] = df_p['risk_class'].map(z_factors)
    
    # Formule de Safety Stock Robuste
    df_p['safety_stock'] = (df_p['Z'] * np.sqrt(df_p['avg_lead_time']/7 * df_p['std_demand']**2 + df_p['mean_demand']**2 * (df_p['lead_time_std']/7)**2)).round(2)
    df_p['reorder_point'] = (df_p['mean_demand'] * df_p['avg_lead_time']/7 + df_p['safety_stock']).round(2)
    
    return df_p

def run_anomaly_logic(df_p_classified, df_c):
    r1r2_products = df_p_classified[df_p_classified['risk_class'].isin(['R1', 'R2'])][['product_id', 'risk_class', 'RRS']]
    df_merged = df_c.merge(r1r2_products, on='product_id', how='inner')
    df_merged = df_merged.sort_values(['product_id', 'week'])
    
    df_merged['rolling_mean_4w'] = df_merged.groupby('product_id')['consumption'].transform(lambda x: x.rolling(4, min_periods=1).mean())
    df_merged['rolling_std_4w'] = df_merged.groupby('product_id')['consumption'].transform(lambda x: x.rolling(4, min_periods=1).std().fillna(0))
    df_merged['wow_change'] = df_merged.groupby('product_id')['consumption'].transform(lambda x: x.pct_change())
    df_merged['stock_consumption_ratio'] = (df_merged['stock_level'] / df_merged['rolling_mean_4w'].replace(0, np.nan))
    df_merged['deviation'] = df_merged['consumption'] - df_merged['rolling_mean_4w']
    
    features = ['consumption', 'rolling_mean_4w', 'rolling_std_4w', 'deviation', 'wow_change', 'stock_consumption_ratio']
    X = df_merged[features].copy()
    X = X.replace([np.inf, -np.inf], np.nan).fillna(0) # Correction de l'erreur Infinity
    
    X_scaled = StandardScaler().fit_transform(X)
    model = IsolationForest(contamination=0.05, n_estimators=100, random_state=42)
    df_merged['is_anomaly'] = (model.fit_predict(X_scaled) == -1).astype(int)
    
    def classify_alert(row):
        if row['is_anomaly'] == 0: return 'GREEN'
        if row['consumption'] > 2 * row['rolling_mean_4w']: return 'RED'
        if row['wow_change'] > 0.5: return 'ORANGE'
        return 'YELLOW'
    
    df_merged['alert_level'] = df_merged.apply(classify_alert, axis=1)
    return df_merged