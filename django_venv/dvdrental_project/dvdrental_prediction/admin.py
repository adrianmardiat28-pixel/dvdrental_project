from django.contrib import admin
from .models import ModelInfo, MovieModelInfo
from django.utils.html import format_html
from django.utils.timezone import now

# ==========================================
# 1. ADMIN UNTUK CUSTOMER (ModelInfo)
# ==========================================
@admin.register(ModelInfo)
class ModelInfoAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'training_date', 'training_data', 'short_summary', 'retrain_button')
    search_fields = ('model_name', 'training_data')
    
    def short_summary(self, obj):
        return (obj.model_summary[:75] + '...') if obj.model_summary else "-"
    short_summary.short_description = "Summary"

    def retrain_button(self, obj):
        return format_html('<a class="button" href="/admin/dvdrental_prediction/retrain-model/{}/">Retrain</a>', obj.id)
    retrain_button.short_description = "Retrain"


# ==========================================
# 2. ADMIN UNTUK MOVIE (MovieModelInfo)
# ==========================================
@admin.register(MovieModelInfo)
class MovieModelInfoAdmin(admin.ModelAdmin):
    # Update list_display untuk memunculkan tombol Load CSV di tabel utama
    list_display = ('model_name', 'training_date', 'training_data', 'short_summary', 'load_csv_button', 'retrain_button')
    search_fields = ('model_name', 'training_data')
    
    # Susunan field di halaman detail
    fields = ('model_name', 'model_file', 'training_data', 'training_date', 'model_summary')

    def short_summary(self, obj):
        return (obj.model_summary[:75] + '...') if obj.model_summary else "-"
    short_summary.short_description = "Summary"

    # TOMBOL BARU: Load CSV (ETL) - Warna Biru
    def load_csv_button(self, obj):
        return format_html(
            '<a class="button" style="background-color: #007bff; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none; margin-right: 5px;" '
            'href="/admin/dvdrental_prediction/load-csv-data/{}/">Load CSV (ETL)</a>', obj.id
        )
    load_csv_button.short_description = "Update Data"

    # TOMBOL: Retrain Movie - Warna Hijau
    def retrain_button(self, obj):
        return format_html(
            '<a class="button" style="background-color: #28a745; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none;" '
            'href="/admin/dvdrental_prediction/retrain-movie-model/{}/">Retrain Movie</a>', obj.id
        )
    retrain_button.short_description = "Retrain AI"