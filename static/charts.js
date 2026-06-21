const labels = [];
const values = [];

testResults.forEach(item => {

    labels.push(item.test);

    values.push(item.value);

});

const ctx =
document.getElementById("healthChart");

new Chart(ctx, {

    type: "bar",

    data: {

        labels: labels,

        datasets: [

        {
            label: "Patient Values",

            data: values,

            borderWidth: 2
        }

        ]
    },

    options: {

        responsive: true,

        scales: {

            y: {
                beginAtZero: true
            }
        }
    }

});