document.addEventListener("DOMContentLoaded", function () {
    const statusBox = document.getElementById("statusBox");
    const predictionChart = document.getElementById("predictionChart");

    // 1. Example input data (nanti bisa diambil dari form)
    const inputData = {
        store_id: 1,
        active: 1,
        total_payment: 150,
        payment_count: 3,
        average_payment: 50
    };

    // 2. Send the data to the backend
    fetch('/predict-customer/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken') // Penting untuk Django POST request
        },
        body: JSON.stringify(inputData)
    })
    .then(response => response.json())
    .then(data => {
        // 3. Once the response is received, update the chart
        if (data.prediction !== undefined) {
            statusBox.textContent = `Prediction: ${data.prediction}`;

            // 4. Create the chart using Chart.js
            new Chart(predictionChart, {
                type: 'bar', // Bisa diganti 'line', 'pie', dll.
                data: {
                    labels: ['Class 0', 'Class 1'], // Sesuaikan dengan kelas modelmu
                    datasets: [{
                        label: 'Prediction Probability',
                        data: data.probability, // Array probabilitas dari backend
                        backgroundColor: ['rgba(255, 99, 132, 0.2)', 'rgba(54, 162, 235, 0.2)'],
                        borderColor: ['rgba(255, 99, 132, 1)', 'rgba(54, 162, 235, 1)'],
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        } else {
            statusBox.textContent = 'Error: Could not fetch prediction.';
        }
    })
    .catch(error => {
        statusBox.textContent = 'Error: ' + error.message;
    });
});

// Fungsi tambahan untuk mengambil CSRF Token (agar tidak error 403)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}