from django.shortcuts import render, get_object_or_404
from django.conf import settings
import joblib
import os
import pandas as pd
import json
import numpy as np
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .forms import MovieDemandForm
from django.db.models import Avg, Count
from django.core.management import call_command
from django.contrib import messages
from django.shortcuts import redirect

from .models import Movie, MovieModelInfo ,Category, FactMovieDemand
from .forms import CustomerPredictionForm, MovieSearchForm, MovieDemandForm

def home(request):
    return render(request, 'dvdrental_prediction/home.html')

def about(request):
    return render(request, 'dvdrental_prediction/about.html')

def movie_list(request):
    # gunakan select_related agar query lebih efisien saat ambil language
    movies = Movie.objects.select_related('language').all()
    return render(request, 'dvdrental_prediction/movie_list.html', {'movies': movies})

def movie_detail(request, film_id):
    # gunakan get_object_or_404 agar tidak error jika film_id tidak ditemukan
    movie = get_object_or_404(Movie, pk=film_id)
    # ambil aktor lewat relasi ManyToMany
    actors = movie.actors.all()
    return render(request, 'dvdrental_prediction/movie_detail.html', {
        'movie': movie,
        'actors': actors
    })

def search_result(request):
    form = MovieSearchForm(request.GET)
    movies = Movie.objects.select_related('language').all()

    if form.is_valid():
        actor = form.cleaned_data.get('actor')
        category = form.cleaned_data.get('category')
        language = form.cleaned_data.get('language')

        if actor:
            movies = movies.filter(actors=actor)
        if category:
            movies = movies.filter(filmcategory__category=category)
        if language:
            movies = movies.filter(language=language)

    return render(request, 'dvdrental_prediction/movie_search.html', {
        'form': form,
        'movies': movies
    })

# --- PREDIKSI MOVIE DEMAND ---
def predict_movie_demand(request):
    prediction = None
    probability = None
    all_categories = Category.objects.all().order_by('name')

    if request.method == 'POST':
        form = MovieDemandForm(request.POST)
        selected_genre = request.POST.get('category_name')

        if form.is_valid():
            try:
                # Load Model & List Fitur
                model = joblib.load(os.path.join(settings.BASE_DIR, 'movie_demand_model.pkl'))
                features = joblib.load(os.path.join(settings.BASE_DIR, 'model_features.pkl'))

                # Buat DataFrame input dengan kolom yang sama persis saat training
                input_df = pd.DataFrame(0, index=[0], columns=features)
                
                # Isi data numerik
                input_df['rental_duration'] = form.cleaned_data['rental_duration']
                input_df['rental_rate'] = form.cleaned_data['rental_rate']
                input_df['length'] = form.cleaned_data['length']
                input_df['replacement_cost'] = form.cleaned_data['replacement_cost']

                # One-Hot Encoding Manual untuk Genre
                genre_col = f"genre_{selected_genre}"
                if genre_col in input_df.columns:
                    input_df[genre_col] = 1

                # Jalankan Prediksi
                hasil = model.predict(input_df)[0]
                proba = model.predict_proba(input_df)[0]

                if hasil == 1:
                    prediction = "LARIS MANIS"
                    probability = round(proba[1] * 100, 1)
                else:
                    prediction = "SEPI PEMINAT"
                    probability = round(proba[0] * 100, 1)

            except Exception as e:
                print(f"Error: {e}")
                prediction = "Model Error"
    else:
        form = MovieDemandForm()

    return render(request, 'dvdrental_prediction/movie_prediction.html', {
        'form': form, 'categories': all_categories, 
        'prediction': prediction, 'probability': probability
    })

# Customer Prediction 
def customer_prediction_view(request):
    form = CustomerPredictionForm()
    return render(request, 'dvdrental_prediction/dashboard.html', {'form': form})

# Load model di luar fungsi agar hanya ter-load sekali saat server jalan
model_path = os.path.join(settings.BASE_DIR, 'customer_value_model.pkl')
model = joblib.load(model_path)

@csrf_exempt
def predict_customer(request):
    print (f"Request method: {request.method}")
    if request.method == "POST":
        # Parse incoming JSON data
        data = json.loads(request.body)
        print (f"Received data: {data}")

        # Prepare feature array (ensure correct feature order)
        features = np.array([
            data["store_id"],
            data["active"],
            data["total_payment"],
            data["payment_count"],
            data["average_payment"]
        ]).reshape(1, -1)

        # Melakukan prediksi
        prediction = model.predict(features)[0]
        # Jika model mendukung probability (optional tapi bagus untuk chart)
        probability = model.predict_proba(features)[0].tolist() 

        return JsonResponse({
            'prediction': int(prediction),
            'probability': probability
        })
    
# --- TAMBAHAN BARU UNTUK DASHBOARD ANALYTIC ---
def analytic_dashboard(request):
    """
    Dashboard Analitik menggunakan data dari Tabel OLAP (Fact Table)
    agar performa lebih cepat dan data selalu akurat.
    """
    
    # 1. Menghitung Metrik Ringkasan (Summary Cards) dari Tabel OLAP
    total_movies = FactMovieDemand.objects.count()
    
    # Ambil rata-rata
    metrics = FactMovieDemand.objects.aggregate(
        avg_rate=Avg('rental_rate'),
        avg_len=Avg('length')
    )
    
    avg_rental_rate = round(metrics['avg_rate'] or 0, 2)
    avg_duration = round(metrics['avg_len'] or 0, 1)
    
    # Menghitung film High Demand (is_popular = 1)
    popular_movies_count = FactMovieDemand.objects.filter(is_popular=1).count()
    low_demand_count = total_movies - popular_movies_count

    # 2. Menyiapkan Data untuk Bar Chart (Distribusi Rating)
    # Kita grouping berdasarkan rating
    rating_query = FactMovieDemand.objects.values('rating').annotate(count=Count('film_id')).order_by('-count')
    
    rating_labels = [item['rating'] for item in rating_query]
    rating_counts = [item['count'] for item in rating_query]

    # 3. Menyiapkan Context & Mengubahnya ke JSON untuk Chart.js
    context = {
        'total_movies': total_movies,
        'avg_rental_rate': avg_rental_rate,
        'avg_duration': avg_duration,
        'popular_movies_count': popular_movies_count,
        
        # Data untuk JavaScript (Chart.js)
        'rating_labels': json.dumps(rating_labels),
        'rating_counts': json.dumps(rating_counts),
        'demand_dist': json.dumps([popular_movies_count, low_demand_count]),
    }
    
    return render(request, 'dvdrental_prediction/analytic.html', context)

# --- API UNTUK HOME DASHBOARD ---
def api_home_data(request):
    try:
        # 1. Total Movies dari Tabel OLAP (Lebih Cepat)
        total_movies = FactMovieDemand.objects.count()
        
        # 2. Rata-rata Harga Sewa dari OLAP
        avg_res = FactMovieDemand.objects.aggregate(Avg('rental_rate'))
        avg_rate = avg_res['rental_rate__avg'] or 0
        avg_rate_formatted = f"${round(avg_rate, 2)}"

        # 3. Akurasi Model Terbaru
        latest_model = MovieModelInfo.objects.order_by('-id').first()
        accuracy_display = f"{round(latest_model.accuracy * 100, 1)}%" if latest_model and latest_model.accuracy else "Pending"

        # 4. Distribusi Demand (Berdasarkan Kolom is_popular di OLAP)
        high_demand = FactMovieDemand.objects.filter(is_popular=1).count()
        low_demand = total_movies - high_demand

        return JsonResponse({
            'total_movies': f"{total_movies:,}",
            'avg_rental_rate': avg_rate_formatted,
            'model_accuracy': accuracy_display,
            'chart_data': [high_demand, low_demand]
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def load_csv_data_view(request, model_id):
    try:
        # Memanggil command ETL (pastikan nama command sesuai dengan file di management/commands/)
        call_command('etl_movie_data') 
        
        messages.success(request, "Data OLAP berhasil ditarik ke CSV (Angka 10 Berhasil Diterapkan!)")
    except Exception as e:
        messages.error(request, f"Gagal memuat data: {str(e)}")
    
    # Kembali ke halaman admin sebelumnya
    return redirect(f'/admin/dvdrental_prediction/moviemodelinfo/')