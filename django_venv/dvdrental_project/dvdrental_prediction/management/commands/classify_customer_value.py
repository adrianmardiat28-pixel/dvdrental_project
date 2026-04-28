import pandas as pd
import joblib
from django.core.management.base import BaseCommand
from sklearn.ensemble import RandomForestClassifier 
from sklearn.model_selection import train_test_split    
from sklearn.metrics import classification_report

from dvdrental_prediction.models import ModelInfo

class Command(BaseCommand):
    help = 'train the model classify customer value and save it'

    def handle(self, *args, **kwargs):
        # 1. Baca dataset dari CSV
        df = pd.read_csv('customer_payment_dataset.csv')

        # 2. Create target label
        df['value_label'] = (df['total_payment'] > 100 ).astype(int) # 1 untuk high value, 0 untuk low value

        # 3. create  features dan label
        features = ['store_id','total_payment','active', 'payment_count', 'average_payment']
        X = df[features]
        y = df['value_label']

        # 4. Split data untuk training dan testing
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # 5. Train model Random Forest
        model = RandomForestClassifier()
        model.fit(X_train, y_train)

        # 6. Predict and evaluate model
        predictions = model.predict(X_test)
        report = classification_report(y_test, predictions)
        self.stdout.write(self.style.SUCCESS('Classification Report:\n' + report))

        # 7. save model to file
        model_filename = 'customer_value_model.pkl'
        joblib.dump(model, model_filename)
        self.stdout.write(self.style.SUCCESS(f'Model saved as {model_filename}'))

        # 8. Simpan informasi model ke database (opsional, bisa diabaikan jika tidak ada tabel ModelInfo)
        model_info = ModelInfo.objects.create(
            model_name='RandomForestCustomerModel',
            model_file=model_filename,
            training_data='customer_payment_dataset.csv',
            training_date=pd.Timestamp.now(),
            model_summary=report      
        )
        self.stdout.write(self.style.SUCCESS(f'Model information saved to database {model_info.id}'))

