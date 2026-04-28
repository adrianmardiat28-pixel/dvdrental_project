from django.urls import path
from . import views, admin_views # Mengambil dari folder yang sama

urlpatterns = [
    # 1. Navigasi Utama
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('movies/', views.movie_list, name='movie_list'),
    path('movies/<int:film_id>/', views.movie_detail, name='movie_detail'), 
    path('search/', views.search_result, name='search_result'),
    path('analytics/', views.analytic_dashboard, name='analytics'),
    path('api/home-data/', views.api_home_data, name='api_home_data'),

    # 2. Fitur Prediksi Customer
    path('predict-view/', views.customer_prediction_view, name='customer_prediction_view'),
    path('predict-customer/', views.predict_customer, name='predict_customer'),

    # 3. Fitur Prediksi Movie Demand
    path('predict/', views.predict_movie_demand, name='predict_movie_demand'),

    # 4. Fitur Admin (Retrain) 
    path('retrain-model/<int:model_id>/', admin_views.retrain_model_view, name='retrain_model'),
    path('retrain-movie-model/<int:model_id>/', admin_views.retrain_movie_model_view, name='retrain_movie_model'),
    path('load-csv-data/<int:model_id>/', admin_views.load_csv_data_view, name='load_csv_data'),
]