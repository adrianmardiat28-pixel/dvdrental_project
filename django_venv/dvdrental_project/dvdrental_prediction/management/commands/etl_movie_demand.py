from django.core.management.base import BaseCommand
from django.db import connection
import pandas as pd
import os

class Command(BaseCommand):
    help = "ETL: Extract data from OLAP Table (fact_movie_demand) for Machine Learning"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.HTTP_INFO("--- Memulai Proses ETL dari Tabel OLAP ---"))

        # 1. EXTRACT: Mengambil data langsung dari tabel OLAP
        # Tidak perlu JOIN lagi karena data sudah diringkas di PostgreSQL
        query = """
            SELECT 
                rental_duration, 
                rental_rate, 
                length, 
                replacement_cost, 
                category_name, 
                is_popular 
            FROM fact_movie_demand
        """
        
        try:
            self.stdout.write("Mengekstraksi data dari fact_movie_demand...")
            df = pd.read_sql(query, connection)
            
            if df.empty:
                self.stdout.write(self.style.ERROR("Tabel OLAP kosong! Pastikan sudah menjalankan SQL INSERT di pgAdmin."))
                return

            # 2. TRANSFORM: (Minimalis karena data OLAP biasanya sudah bersih)
            # Pastikan tidak ada nilai null yang tertinggal
            df['category_name'] = df['category_name'].fillna('Unknown')
            df = df.dropna()

            # 3. LOAD: Menyimpan ke CSV untuk dikonsumsi model ML
            csv_filename = 'movie_demand_data.csv'
            df.to_csv(csv_filename, index=False)

            # Output informasi untuk terminal
            self.stdout.write(self.style.SUCCESS(f'SUKSES! {len(df)} baris data OLAP dimuat ke {csv_filename}'))
            self.stdout.write(f"Fitur yang dimuat: {list(df.columns)}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Terjadi kesalahan saat ETL: {str(e)}"))

        self.stdout.write(self.style.HTTP_INFO("--- ETL Selesai ---"))