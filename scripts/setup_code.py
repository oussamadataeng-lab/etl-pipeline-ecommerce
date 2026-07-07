import os

# Assurez-vous que les dossiers existent
os.makedirs('data/raw', exist_ok=True)
os.makedirs('data/processed', exist_ok=True)
os.makedirs('database', exist_ok=True)
os.makedirs('logs', exist_ok=True)

# Contenu du fichier extract.py
extract_code = '''"""
EXTRACTION - Donnees reelles
"""
import requests
import pandas as pd
from datetime import datetime
import time
import logging
import os

os.makedirs('data/raw', exist_ok=True)
os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/etl.log'),
        logging.StreamHandler()
    ]
)

class DataExtractor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("=" * 70)
        self.logger.info("DEMARRAGE DE L EXTRACTION")
        self.logger.info("=" * 70)
    
    def extract_products(self):
        self.logger.info("Extraction des PRODUITS...")
        try:
            url = "https://fakestoreapi.com/products"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                df = pd.DataFrame(data)
                df['rating_rate'] = df['rating'].apply(lambda x: x.get('rate') if isinstance(x, dict) else None)
                df['rating_count'] = df['rating'].apply(lambda x: x.get('count') if isinstance(x, dict) else None)
                df = df.drop('rating', axis=1)
                filepath = 'data/raw/products.csv'
                df.to_csv(filepath, index=False, encoding='utf-8')
                self.logger.info(f"{len(df)} produits extraits")
                return df
            else:
                self.logger.error(f"Erreur HTTP: {response.status_code}")
                return None
        except Exception as e:
            self.logger.error(f"Erreur: {str(e)}")
            return None
    
    def extract_users(self):
        self.logger.info("Extraction des UTILISATEURS...")
        try:
            url = "https://fakestoreapi.com/users"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                users = []
                for user in data:
                    flat_user = {
                        'user_id': user['id'],
                        'email': user['email'],
                        'username': user['username'],
                        'first_name': user['name']['firstname'],
                        'last_name': user['name']['lastname'],
                        'phone': user['phone'],
                        'city': user['address']['city'],
                        'street': user['address']['street'],
                        'zipcode': user['address']['zipcode']
                    }
                    users.append(flat_user)
                df = pd.DataFrame(users)
                filepath = 'data/raw/users.csv'
                df.to_csv(filepath, index=False, encoding='utf-8')
                self.logger.info(f"{len(df)} utilisateurs extraits")
                return df
            else:
                self.logger.error(f"Erreur HTTP: {response.status_code}")
                return None
        except Exception as e:
            self.logger.error(f"Erreur: {str(e)}")
            return None
    
    def extract_orders(self):
        self.logger.info("Extraction des COMMANDES...")
        try:
            url = "https://fakestoreapi.com/carts"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                order_items = []
                for cart in data:
                    for product in cart['products']:
                        item = {
                            'order_id': cart['id'],
                            'user_id': cart['userId'],
                            'date': cart['date'],
                            'product_id': product['productId'],
                            'quantity': product['quantity']
                        }
                        order_items.append(item)
                df = pd.DataFrame(order_items)
                filepath = 'data/raw/orders.csv'
                df.to_csv(filepath, index=False, encoding='utf-8')
                self.logger.info(f"{len(df)} lignes de commande extraites")
                return df
            else:
                self.logger.error(f"Erreur HTTP: {response.status_code}")
                return None
        except Exception as e:
            self.logger.error(f"Erreur: {str(e)}")
            return None

def main():
    extractor = DataExtractor()
    dataframes = {}
    dataframes['Produits'] = extractor.extract_products()
    time.sleep(1)
    dataframes['Utilisateurs'] = extractor.extract_users()
    time.sleep(1)
    dataframes['Commandes'] = extractor.extract_orders()
    extractor.logger.info("EXTRACTION TERMINEE")
    return dataframes

if __name__ == "__main__":
    main()
'''

# Contenu du fichier transform.py
transform_code = '''"""
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
'''

# Contenu du fichier load.py
load_code = '''"""
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
'''

# Contenu du fichier run_pipeline.py
run_code = '''"""
PIPELINE ETL COMPLET
"""
import logging
from datetime import datetime
import sys
import os

os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/etl.log'),
        logging.StreamHandler()
    ]
)

from extract import main as extract_main
from transform import main as transform_main
from load import main as load_main

def run():
    logger = logging.getLogger(__name__)
    start_time = datetime.now()
    logger.info("=" * 80)
    logger.info("DEMARRAGE DU PIPELINE ETL COMPLET")
    logger.info(f"Debut: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)
    try:
        logger.info("ETAPE 1/3: EXTRACTION")
        extract_main()
        logger.info("ETAPE 2/3: TRANSFORMATION")
        transform_main()
        logger.info("ETAPE 3/3: CHARGEMENT")
        load_main()
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info("=" * 80)
        logger.info("PIPELINE ETL TERMINE AVEC SUCCES !")
        logger.info(f"Duree totale: {duration:.2f} secondes")
        logger.info("=" * 80)
    except Exception as e:
        logger.error("ERREUR DANS LE PIPELINE")
        logger.error(str(e))
        sys.exit(1)

if __name__ == "__main__":
    run()
'''

# Ecrire les fichiers en UTF-8 pur (sans BOM)
files_to_create = {
    'scripts/extract.py': extract_code,
    'scripts/transform.py': transform_code,
    'scripts/load.py': load_code,
    'scripts/run_pipeline.py': run_code
}

for filepath, content in files_to_create.items():
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print(f"Fichier cree proprement : {filepath}")

print("\nTous les fichiers ont ete recrees sans erreurs d'encodage !")
print("Vous pouvez maintenant lancer : python scripts/run_pipeline.py")