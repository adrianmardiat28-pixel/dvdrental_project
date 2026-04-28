import pandas as pd
import joblib
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.timezone import now
from sklearn.ensemble import RandomForestClassifier 
from sklearn.model_selection import train_test_split 
from sklearn.metrics import classification_report

# Import model database hasil migrasi terbaru
from dvdrental_prediction.models import MovieModelInfo

class Command(BaseCommand):
    help = 'Train Random Forest model and bundle with Features into one file'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.HTTP_INFO("--- Memulai Training Model Bundle (OLAP + Genre) ---"))
        
        # 1. BACA DATA
        csv_path = os.path.join(settings.BASE_DIR, 'movie_demand_data.csv')
        try:
            df = pd.read_csv(csv_path)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File {csv_path} tidak ditemukan! Jalankan ETL dulu.'))
            return

        # 2. FEATURE ENGINEERING (ONE-HOT ENCODING GENRE)
        if 'category_name' in df.columns:
            self.stdout.write("Mentransformasi Genre menjadi fitur numerik...")
            genre_dummies = pd.get_dummies(df['category_name'], prefix='genre')
            df = pd.concat([df, genre_dummies], axis=1)
            
            genre_cols = genre_dummies.columns.tolist()
            features = ['rental_duration', 'rental_rate', 'length', 'replacement_cost'] + genre_cols
        else:
            features = ['rental_duration', 'rental_rate', 'length', 'replacement_cost']

        X = df[features]
        y = df['is_popular']

        # 3. SPLIT DATA
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # 4. TRAINING
        self.stdout.write(f"Melatih model dengan {len(features)} variabel input...")
        model = RandomForestClassifier(
            n_estimators=300,
            max_depth=15,
            min_samples_leaf=2,
            class_weight='balanced',
            random_state=42
        )
        model.fit(X_train, y_train)

        # 5. EVALUASI
        akurasi = model.score(X_test, y_test)
        report = classification_report(y_test, model.predict(X_test))
        
        self.stdout.write(self.style.SUCCESS(f'Akurasi Terbaru: {akurasi * 100:.2f}%'))

        # 6. SIMPAN DALAM SATU PAKET (BUNDLE)
        # Kita satukan model dan daftar fitur ke dalam dictionary agar tidak pusing
        model_bundle = {
            'model': model,
            'features': features
        }
        
        # Nama file baru agar tidak tertukar dengan yang lama
        bundle_path = os.path.join(settings.BASE_DIR, 'movie_demand_bundle.pkl')
        joblib.dump(model_bundle, bundle_path)

        # 7. UPDATE DATABASE
        model_info = MovieModelInfo.objects.create(
            model_name='Random Forest Bundle (Model + Features)',
            model_file='movie_demand_bundle.pkl', # Simpan nama file bundle
            training_data='movie_demand_data.csv',
            training_date=now(),
            accuracy=akurasi,
            model_summary=report
        )

        self.stdout.write(self.style.SUCCESS(f"Sukses! Bundle ID {model_info.id} disimpan sebagai 'movie_demand_bundle.pkl'"))