"""
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