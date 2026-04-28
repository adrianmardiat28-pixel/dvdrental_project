document.addEventListener("DOMContentLoaded", function() {
    // 1. Ambil elemen-elemen di HTML yang mau diubah
    const elTotalMovies = document.getElementById('stat-total-movies');
    const elAvgRate = document.getElementById('stat-avg-rate');
    const elAccuracy = document.getElementById('stat-accuracy');
    const ctxChart = document.getElementById('demandChart').getContext('2d');

    // 2. Fetch Data dari API Django
    fetch(apiHomeDataUrl)
        .then(response => response.json())
        .then(data => {
            // 3. Tulis angka asli dari Database ke dalam Kotak/Card HTML
            elTotalMovies.innerText = data.total_movies;
            elAvgRate.innerText = data.avg_rental_rate;
            elAccuracy.innerText = data.model_accuracy;

            // 4. Gambar Chart.js menggunakan data asli
            new Chart(ctxChart, {
                type: 'doughnut',
                data: {
                    labels: ['High Demand', 'Low Demand'],
                    datasets: [{
                        data: data.chart_data, // Data disuntikkan dari API
                        backgroundColor: ['#10b981', '#f43f5e'],
                        borderColor: '#ffffff',
                        borderWidth: 3,
                        hoverOffset: 5
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '75%',
                    plugins: { 
                        legend: { position: 'bottom' } 
                    },
                    animation: {
                        animateScale: true,
                        animateRotate: true
                    }
                }
            });
        })
        .catch(error => {
            console.error("Gagal mengambil data dari API:", error);
            elTotalMovies.innerText = "Error";
            elAvgRate.innerText = "Error";
            elAccuracy.innerText = "Error";
        });
});