"""
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