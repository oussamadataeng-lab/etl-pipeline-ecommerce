"""
LOAD - Chargement dans SQLite
"""
import pandas as pd
from sqlalchemy import create_engine, text
import logging
import os

os.makedirs('database', exist_ok=True)
os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/etl.log'),
        logging.StreamHandler()
    ]
)

class DataLoader:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("=" * 70)
        self.logger.info("DEMARRAGE DU CHARGEMENT")
        self.logger.info("=" * 70)
        self.db_path = 'database/ecommerce.db'
        self.engine = create_engine(f'sqlite:///{self.db_path}')
        self.logger.info(f"Connexion prete: {self.db_path}")
    
    def load_table(self, df, table_name):
        try:
            self.logger.info(f"Chargement de {table_name}...")
            df.to_sql(table_name, self.engine, if_exists='replace', index=False)
            self.logger.info(f"{len(df)} lignes chargees dans {table_name}")
        except Exception as e:
            self.logger.error(f"Erreur: {str(e)}")
    
    def create_views(self):
        self.logger.info("Creation des VUES SQL...")
        view_top_products = "CREATE VIEW IF NOT EXISTS v_top_products AS SELECT product_id, times_ordered, total_revenue FROM product_summary ORDER BY total_revenue DESC"
        view_top_customers = "CREATE VIEW IF NOT EXISTS v_top_customers AS SELECT u.full_name, us.total_orders, us.total_spent FROM user_summary us LEFT JOIN users_clean u ON us.user_id = u.user_id ORDER BY us.total_spent DESC"
        
        with self.engine.connect() as conn:
            conn.execute(text(view_top_products))
            conn.execute(text(view_top_customers))
            conn.commit()
            self.logger.info("Vues creees")

    def show_sample_data(self):
        self.logger.info("Exemple de donnees dans la base :")
        with self.engine.connect() as conn:
            self.logger.info("Top 5 Produits (Revenus):")
            result = conn.execute(text("SELECT * FROM v_top_products LIMIT 5"))
            for row in result:
                self.logger.info(f"   Produit {row[0]}: {row[2]}$ de revenus")
            
            self.logger.info("Top 5 Clients (Depenses):")
            result = conn.execute(text("SELECT * FROM v_top_customers LIMIT 5"))
            for row in result:
                self.logger.info(f"   {row[0]}: {row[2]}$ depenses")

def main():
    loader = DataLoader()
    datasets = {
        'products_clean': 'data/processed/products_clean.csv',
        'users_clean': 'data/processed/users_clean.csv',
        'orders_clean': 'data/processed/orders_clean.csv',
        'user_summary': 'data/processed/user_summary.csv',
        'product_summary': 'data/processed/product_summary.csv',
        'monthly_summary': 'data/processed/monthly_summary.csv'
    }
    for table_name, filepath in datasets.items():
        df = pd.read_csv(filepath)
        loader.load_table(df, table_name)
    loader.create_views()
    loader.show_sample_data()
    loader.logger.info("CHARGEMENT TERMINE")

if __name__ == "__main__":
    main()