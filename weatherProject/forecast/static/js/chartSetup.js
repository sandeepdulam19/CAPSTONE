const { plugin } = require("mongoose");

document.addEventListener('DOMContentLoaded', () => {
    const forecastItems = document.querySelectorAll('.forecast-item');

    const temps = [];
    const times = [];

    forecastItems.forEach(item => {
        const time = item.querySelector('.forecast-time').textContent;
        const temp = item.querySelector('.forecast-temperatureValue').textContent;
        const hum = item.querySelector('.forecast-humidityValue').textContent;

        if(time && temp && hum){
            times.push(time);
            temps.push(temp);
        }

    });
    if (temps.length === 0 || times){
        console.error('Temp or time values are missing');
        return;
    }

    new Chart(Ctx,{
        type : 'line',
        data: {
            labels: times,
            datasets:[
                {
                    label: 'celsius Degrees',
                    data: temps,
                    borderColor: gradient,
                    borderWidth: 2,
                    tension: 0.4,
                    pointRadius: 2,

                },
            ],
        },
        options: {
            plugins: {
                legend: {
                    display: false,
                },
            },
            scales: {
                x: {
                    display: false,
                    grid: {
                        drawOnChartArea: false,
                    },
                },
                y: {
                    display: false,
                    grid: {
                        drawOnChartArea: false,
                    },
                },
            },
            animation:{
                duration: 750,
            },
        },
    });
});