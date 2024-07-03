document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("add-food").addEventListener("click", addFood);
    document.getElementById("modify-food").addEventListener("click", modifyFood);
    document.getElementById("delete-food").addEventListener("click", deleteFood);

    document.getElementById("pie-chart-btn").addEventListener("click", () => showVisualization('pie'));
    document.getElementById("bar-chart-btn").addEventListener("click", () => showVisualization('bar'));
    document.getElementById("scatter-plot-btn").addEventListener("click", () => showVisualization('scatter'));

    function addFood() {
        const name = prompt("Enter food name:");
        const price = parseFloat(prompt("Enter food price:"));
        const quantity = parseInt(prompt("Enter food quantity:"));

        fetch('/food', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ command: 'add', name, price, quantity }),
        }).then(response => response.json()).then(data => {
            if (data.success) {
                alert("Food added successfully!");
            }
        });
    }

    function modifyFood() {
        const id = parseInt(prompt("Enter food ID to modify:"));
        const name = prompt("Enter new food name:");
        const price = parseFloat(prompt("Enter new food price:"));
        const quantity = parseInt(prompt("Enter new food quantity:"));

        fetch('/food', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ command: 'modify', id, name, price, quantity }),
        }).then(response => response.json()).then(data => {
            if (data.success) {
                alert("Food modified successfully!");
            }
        });
    }

    function deleteFood() {
        const id = parseInt(prompt("Enter food ID to delete:"));

        fetch('/food', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ command: 'delete', id }),
        }).then(response => response.json()).then(data => {
            if (data.success) {
                alert("Food deleted successfully!");
            }
        });
    }

    function showVisualization(type) {
        const N = document.getElementById("N").value;

        fetch('/visualize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ type, N }),
        }).then(response => response.json()).then(data => {
            if (data.success) {
                if (type === 'pie') {
                    drawPieChart();
                } else if (type === 'bar') {
                    drawBarChart();
                } else if (type === 'scatter') {
                    drawScatterPlot();
                }
            }
        });
    }

    function drawPieChart() {
        d3.select("#chart-container").html('<img src="/static/pie_chart.png" alt="Pie Chart">');
    }

    function drawBarChart() {
        d3.select("#chart-container").html('<img src="/static/bar_chart.png" alt="Bar Chart">');
    }

    function drawScatterPlot() {
        d3.select("#chart-container").html('<img src="/static/scatter_plot.png" alt="Scatter Plot">');
    }
});
