// 1. Deklarasikan variabel global dengan nama yang berbeda dari ID HTML
let myChartInstance = null;

document.getElementById('predictionForm').addEventListener('submit', function(e) {
    e.preventDefault();

    // Ambil data dari input form
    const data = {
        store_id: parseInt(document.getElementById('id_store_id').value),
        active: parseInt(document.getElementById('id_active').value),
        total_payment: parseFloat(document.getElementById('id_total_payment').value),
        payment_count: parseInt(document.getElementById('id_payment_count').value),
        average_payment: parseFloat(document.getElementById('id_average_payment').value)
    };

    // Kirim data ke backend
    fetch('/predict-customer/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        console.log("Prediction result:", result);
        
        // Update teks status
        const statusBox = document.getElementById('statusBox');
        statusBox.innerText = `Prediction: ${result.prediction}, Probabilities: ${result.probability.map(p => p.toFixed(2)).join(', ')}`;
        
        // Panggil fungsi update grafik
        updateChart(result.probability);
    })
    .catch(err => {
        console.error('Prediction error:', err);
        document.getElementById('statusBox').innerText = 'Error making prediction.';
    });
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function updateChart(probabilities) {
    const canvas = document.getElementById('predictionChart');
    const ctx = canvas.getContext('2d');

    // 2. Jika sudah ada grafik sebelumnya, hancurkan dulu agar tidak error/tumpang tindih
    if (myChartInstance) {
        myChartInstance.destroy();
    }

    const labels = probabilities.map((_, index) => `Class ${index}`);
    
    // 3. Buat instance chart baru ke variabel global
    myChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Probability',
                data: probabilities,
                backgroundColor: ['rgba(54, 162, 235, 0.7)', 'rgba(255, 99, 132, 0.7)'],
                borderColor: ['rgba(54, 162, 235, 1)', 'rgba(255, 99, 132, 1)'],
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: { beginAtZero: true, max: 1 }
            }
        }
    });
}