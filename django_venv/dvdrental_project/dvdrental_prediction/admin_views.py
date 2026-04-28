import subprocess
import sys
from django.shortcuts import get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .models import ModelInfo, MovieModelInfo

# ==========================================
# 1. VIEW UNTUK CUSTOMER VALUE (RETRAIN)
# ==========================================
@staff_member_required
def retrain_model_view(request, model_id):
    """View untuk menjalankan ulang training Customer Value."""
    try:
        # Menjalankan perintah: python manage.py classify_customer_value
        subprocess.run([sys.executable, 'manage.py', 'classify_customer_value'], check=True)
        
        messages.success(request, "Customer Model retrained and NEW record created successfully!")
    except subprocess.CalledProcessError:
        messages.error(request, "Skrip Error: Cek Terminal VS Code untuk melihat error di 'classify_customer_value.py'")
    except Exception as e:
        messages.error(request, f"Retraining failed: {str(e)}")

    return redirect('/admin/dvdrental_prediction/modelinfo/')


# ==========================================
# 2. VIEW UNTUK MOVIE DEMAND (LOAD CSV / ETL)
# ==========================================
@staff_member_required
def load_csv_data_view(request, model_id):
    """View untuk menjalankan skrip ETL (Sinkronisasi SQL ke CSV)."""
    try:
        # KUNCI: Nama harus 'etl_movie_demand' sesuai file etl_movie_demand.py di folder commands
        subprocess.run([sys.executable, 'manage.py', 'etl_movie_demand'], check=True)
        
        messages.success(request, "Data OLAP berhasil ditarik dari PostgreSQL ke CSV!")
    except subprocess.CalledProcessError:
        messages.error(request, "Skrip ETL Gagal: Periksa terminal untuk detail error SQL.")
    except Exception as e:
        messages.error(request, f"Terjadi kesalahan saat memuat data: {str(e)}")
        
    return redirect('/admin/dvdrental_prediction/moviemodelinfo/')


# ==========================================
# 3. VIEW UNTUK MOVIE DEMAND (RETRAIN)
# ==========================================
@staff_member_required
def retrain_movie_model_view(request, model_id):
    """View untuk menjalankan ulang training Movie Demand."""
    try:
        # Menjalankan perintah: python manage.py train_movie_model
        subprocess.run([sys.executable, 'manage.py', 'train_movie_model'], check=True)
        
        messages.success(request, "Movie Demand Model retrained successfully with full report!")
    except subprocess.CalledProcessError:
        messages.error(request, "Skrip Training Gagal: Cek Terminal VS Code untuk melihat error di 'train_movie_model.py'")
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        
    return redirect('/admin/dvdrental_prediction/moviemodelinfo/')