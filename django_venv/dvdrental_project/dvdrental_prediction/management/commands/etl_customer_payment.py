import pandas as pd
from django.core.management.base import BaseCommand
from django.db.models import Sum
# Ganti 'your_app' dengan nama folder aplikasi Django kamu
from dvdrental_prediction.models import Customer, Payment 

class Command(BaseCommand):
    help = 'Perform ETL to create the customer payment dataset'

    def handle(self, *args, **kwargs):
        data = []

        # Loop untuk mengambil semua data Customer dan Payment
        for customer in Customer.objects.all():
            payments = Payment.objects.filter(customer=customer)

            # Transformasi data untuk tujuan ML
            total_payment = payments.aggregate(total=Sum('amount'))['total'] or 0
            payment_count = payments.count()
            average_payment = total_payment / payment_count if payment_count > 0 else 0

            # Menambahkan setiap loop ke dalam list data
            data.append({
                'customer_id': customer.customer_id,
                'store_id': customer.store_id,
                'active': customer.active,
                'create_date': customer.create_date,
                'total_payment': total_payment,
                'payment_count': payment_count,
                'average_payment': round(average_payment, 2),
            }) # end of loop

        # Membuat dataframe dan menyimpannya sebagai CSV
        df = pd.DataFrame(data)
        df.to_csv('customer_payment_dataset.csv', index=False)

        # Output sukses ke terminal
        self.stdout.write(self.style.SUCCESS('Customer payment dataset saved to CSV.'))