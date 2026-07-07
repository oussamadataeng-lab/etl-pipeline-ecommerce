"""
TRANSFORMATION - Nettoyage
"""
import pandas as pd
from datetime import datetime
import logging
import os

os.makedirs('data/processed', exist_ok=True)
os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/etl.log'),
        logging.StreamHandler()
    ]
)

class DataTransformer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("=" * 70)
        self.logger.info("DEMARRAGE DE LA TRANSFORMATION")
        self.logger.info("=" * 70)
    
    def transform_products(self, df):
        self.logger.info("Transformation des PRODUITS...")
        df_clean = df.copy()
        df_clean = df_clean.rename(columns={'id': 'product_id'})
        df_clean['price_category'] = pd.cut(
            df_clean['price'],
            bins=[0, 50, 100, 500, float('inf')],
            labels=['Budget', 'Mid-range', 'Premium', 'Luxury']
        )
        self.logger.info(f"{len(df_clean)} produits transformes")
        return df_clean
    
    def transform_users(self, df):
        self.logger.info("Transformation des UTILISATEURS...")
        df_clean = df.copy()
        df_clean['full_name'] = df_clean['first_name'] + ' ' + df_clean['last_name']
        df_clean['email'] = df_clean['email'].str.lower()
        self.logger.info(f"{len(df_clean)} utilisateurs transformes")
        return df_clean
    
    def transform_orders(self, df, products_df):
        self.logger.info("Transformation des COMMANDES...")
        df_clean = df.copy()
        df_clean['date'] = pd.to_datetime(df_clean['date'])
        df_clean['year'] = df_clean['date'].dt.year
        df_clean['month'] = df_clean['date'].dt.month
        products_simple = products_df[['product_id', 'price', 'category', 'title']].copy()
        df_enriched = df_clean.merge(products_simple, on='product_id', how='left')
        df_enriched['line_total'] = df_enriched['quantity'] * df_enriched['price']
        df_enriched = df_enriched.rename(columns={'title': 'product_name', 'category': 'product_category'})
        self.logger.info(f"{len(df_enriched)} commandes transformees")
        return df_enriched
    
    def create_aggregations(self, orders_df):
        self.logger.info("Creation des AGREGATIONS...")
        user_summary = orders_df.groupby('user_id').agg({
            'order_id': 'count',
            'line_total': 'sum',
            'quantity': 'sum'
        }).reset_index()
        user_summary.columns = ['user_id', 'total_orders', 'total_spent', 'total_items']
        
        product_summary = orders_df.groupby('product_id').agg({
            'order_id': 'count',
            'quantity': 'sum',
            'line_total': 'sum'
        }).reset_index()
        product_summary.columns = ['product_id', 'times_ordered', 'total_quantity_sold', 'total_revenue']
        
        monthly_summary = orders_df.groupby(['year', 'month']).agg({
            'line_total': 'sum',
            'quantity': 'sum'
        }).reset_index()
        monthly_summary.columns = ['year', 'month', 'total_revenue', 'total_items']
        
        self.logger.info("Agregations creees")
        return user_summary, product_summary, monthly_summary

def main():
    transformer = DataTransformer()
    transformer.logger.info("Chargement des donnees brutes...")
    products_raw = pd.read_csv('data/raw/products.csv')
    users_raw = pd.read_csv('data/raw/users.csv')
    orders_raw = pd.read_csv('data/raw/orders.csv')
    
    products_clean = transformer.transform_products(products_raw)
    users_clean = transformer.transform_users(users_raw)
    orders_clean = transformer.transform_orders(orders_raw, products_clean)
    user_summary, product_summary, monthly_summary = transformer.create_aggregations(orders_clean)
    
    dataframes = {
        'products_clean': products_clean,
        'users_clean': users_clean,
        'orders_clean': orders_clean,
        'user_summary': user_summary,
        'product_summary': product_summary,
        'monthly_summary': monthly_summary
    }
    
    for name, df in dataframes.items():
        filepath = f'data/processed/{name}.csv'
        df.to_csv(filepath, index=False, encoding='utf-8')
        transformer.logger.info(f"{name} sauvegarde")
    
    transformer.logger.info("TRANSFORMATION TERMINEE")
    return dataframes

if __name__ == "__main__":
    main()