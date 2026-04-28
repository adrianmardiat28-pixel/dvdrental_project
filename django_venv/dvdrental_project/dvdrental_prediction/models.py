from django.db import models

# 1. Class Language
class Language(models.Model):
    language_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=20)

    class Meta:
        db_table = 'language'
        managed = False

    def __str__(self):
        return self.name


# 2. Class Actor
class Actor(models.Model):
    actor_id = models.IntegerField(primary_key=True)
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)

    class Meta:
        db_table = 'actor'
        managed = False

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# 3. Class Movie
class Movie(models.Model):
    film_id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    release_year = models.IntegerField()
    rating = models.CharField(max_length=5)
    
    # --- ATRIBUT UNTUK ML ---
    rental_duration = models.IntegerField(null=True, blank=True)
    rental_rate = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    length = models.IntegerField(null=True, blank=True)
    replacement_cost = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    # -----------------------

    language = models.ForeignKey(Language, on_delete=models.DO_NOTHING, db_column='language_id')
    actors = models.ManyToManyField('Actor', through='FilmActor')
    categories = models.ManyToManyField('Category', through='FilmCategory')

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'film'
        managed = False


# 4. Class Category
class Category(models.Model):
    category_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=25)

    class Meta:
        db_table = 'category'
        managed = False

    def __str__(self):
        return self.name


# 5. Class FilmCategory
class FilmCategory(models.Model):
    film = models.ForeignKey('Movie', on_delete=models.CASCADE, db_column='film_id')
    category = models.ForeignKey('Category', on_delete=models.CASCADE, db_column='category_id')

    class Meta:
        db_table = 'film_category'
        unique_together = ('film', 'category')
        managed = False


# 6. Class FilmActor
class FilmActor(models.Model):
    actor = models.ForeignKey('Actor', on_delete=models.CASCADE, db_column='actor_id')
    film = models.ForeignKey('Movie', on_delete=models.CASCADE, db_column='film_id')

    class Meta:
        db_table = 'film_actor'
        unique_together = ('film', 'actor')
        managed = False


# 7. Class Customer
class Customer(models.Model):
    customer_id = models.IntegerField(primary_key=True)
    store_id = models.IntegerField()
    address_id = models.IntegerField()
    active = models.BooleanField()
    create_date = models.DateTimeField()

    class Meta:
        db_table = 'customer'
        managed = False


# 8. Class Payment
class Payment(models.Model):
    payment_id = models.IntegerField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING, db_column='customer_id')
    amount = models.DecimalField(max_digits=5, decimal_places=2)
    payment_date = models.DateTimeField()

    class Meta:
        db_table = 'payment'
        managed = False


# 9. Class Customer Model Info (Updated with Accuracy Field)
class ModelInfo(models.Model):
    model_name = models.CharField(max_length=100)
    model_file = models.CharField(max_length=255)
    training_data = models.CharField(max_length=255)
    training_date = models.DateTimeField()
    accuracy = models.FloatField(null=True, blank=True) # <-- TAMBAHAN: Untuk simpan angka akurasi
    model_summary = models.TextField(blank=True)

    def __str__(self):
        return f"{self.model_name} - {self.training_date.strftime('%Y-%m-%d %H:%M:%S')}"


# 10. Class Movie Model Info (Pusat Data Hasil Training)
class MovieModelInfo(models.Model):
    model_name = models.CharField(max_length=100, default="Movie Demand Prediction")
    model_file = models.CharField(max_length=255, default="movie_demand_model.pkl")
    training_data = models.CharField(max_length=255, default="movie_demand_data.csv")
    training_date = models.DateTimeField() 
    # Field accuracy untuk menyimpan hasil score (0.0 - 1.0)
    accuracy = models.FloatField(null=True, blank=True) 
    # Field untuk menyimpan Classification Report (Precision, Recall, F1)
    model_summary = models.TextField(blank=True)

    class Meta:
        verbose_name = "Movie AI Model Info"
        verbose_name_plural = "Movie AI Model Infos"
        # Menambahkan ordering agar secara default ID terbaru di atas
        ordering = ['-id']

    def __str__(self):
        # Menampilkan persentase di admin panel (misal: 0.72 -> 72.0%)
        acc_percent = f"{round(self.accuracy * 100, 1)}%" if self.accuracy else "N/A"
        return f"{self.model_name} - {acc_percent} ({self.training_date.strftime('%Y-%m-%d')})"
    
# 11. Class OLAP Table (Fact Table)
class FactMovieDemand(models.Model):
    fact_id = models.AutoField(primary_key=True)
    film_id = models.IntegerField()
    title = models.CharField(max_length=255)
    category_name = models.CharField(max_length=50)
    rental_duration = models.IntegerField()
    rental_rate = models.DecimalField(max_digits=4, decimal_places=2)
    length = models.IntegerField()
    replacement_cost = models.DecimalField(max_digits=5, decimal_places=2)
    rating = models.CharField(max_length=10)
    total_rentals = models.IntegerField()
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2)
    is_popular = models.IntegerField()

    class Meta:
        db_table = 'fact_movie_demand' # Harus sama persis dengan nama tabel di Postgres
        managed = False # Karena kita buat tabelnya manual di pgAdmin

    def __str__(self):
        return f"{self.title} ({self.category_name})"