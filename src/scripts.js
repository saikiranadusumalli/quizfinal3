document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("query-form").addEventListener("submit", function(event) {
        event.preventDefault();
        const formData = new FormData(event.target);
        const data = Object.fromEntries(formData);
        
        fetch('/food', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        }).then(response => response.json()).then(data => {
            if (data.success) {
                alert("Operation successful!");
                location.reload();
            }
        });
    });

    document.getElementById("visualize-form").addEventListener("submit", function(event) {
        event.preventDefault();
        const formData = new FormData(event.target);
        const data = Object.fromEntries(formData);
        
        fetch('/visualize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        }).then(response => response.json()).then(data => {
            if (data.success) {
                if (data.type === "pie") {
                    drawPieChart(data.chartData);
                } else if (data.type === "bar") {
                    drawBarChart(data.chartData);
                } else if (data.type === "scatter") {
                    drawScatterPlot(data.chartData);
                }
            }
        });
    });
});

function drawPieChart(data) {
    // Clear previous chart
    d3.select("#chart").selectAll("*").remove();
    
    const width = 500, height = 500, radius = Math.min(width, height) / 2;
    const color = d3.scaleOrdinal(d3.schemeCategory10);

    const svg = d3.select("#chart").append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", `translate(${width / 2}, ${height / 2})`);

    const pie = d3.pie().value(d => d.quantity);
    const path = d3.arc().outerRadius(radius).innerRadius(0);
    const label = d3.arc().outerRadius(radius).innerRadius(radius - 80);

    const arc = svg.selectAll(".arc")
        .data(pie(data))
        .enter().append("g")
        .attr("class", "arc");

    arc.append("path")
        .attr("d", path)
        .attr("fill", d => color(d.data.name));

    arc.append("text")
        .attr("transform", d => `translate(${label.centroid(d)})`)
        .attr("dy", "0.35em")
        .text(d => `${d.data.name}: ${d.data.quantity}`);
}

function drawBarChart(data) {
    // Clear previous chart
    d3.select("#chart").selectAll("*").remove();

    const margin = {top: 20, right: 30, bottom: 40, left: 90};
    const width = 500 - margin.left - margin.right;
    const height = 500 - margin.top - margin.bottom;

    const svg = d3.select("#chart").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    const x = d3.scaleLinear().range([0, width]);
    const y = d3.scaleBand().range([height, 0]).padding(0.1);

    x.domain([0, d3.max(data, d => d.price)]);
    y.domain(data.map(d => d.name));

    svg.selectAll(".bar")
        .data(data)
        .enter().append("rect")
        .attr("class", "bar")
        .attr("width", d => x(d.price))
        .attr("y", d => y(d.name))
        .attr("height", y.bandwidth())
        .attr("fill", "blue");

    svg.selectAll(".label")
        .data(data)
        .enter().append("text")
        .attr("class", "label")
        .attr("x", d => x(d.price) - 3)
        .attr("y", d => y(d.name) + y.bandwidth() / 2 + 4)
        .attr("text-anchor", "end")
        .text(d => d.price);

    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisBottom(x));

    svg.append("g")
        .attr("class", "y axis")
        .call(d3.axisLeft(y));
}

function drawScatterPlot(data) {
    // Clear previous chart
    d3.select("#chart").selectAll("*").remove();

    const margin = {top: 20, right: 30, bottom: 40, left: 40};
    const width = 500 - margin.left - margin.right;
    const height = 500 - margin.top - margin.bottom;

    const svg = d3.select("#chart").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    const x = d3.scaleLinear().range([0, width]);
    const y = d3.scaleLinear().range([height, 0]);

    x.domain([0, d3.max(data, d => d.index)]);
    y.domain([0, d3.max(data, d => d.price)]);

    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisBottom(x));

    svg.append("g")
        .attr("class", "y axis")
        .call(d3.axisLeft(y));

    svg.selectAll(".dot")
        .data(data)
        .enter().append("circle")
        .attr("class", "dot")
        .attr("cx", d => x(d.index))
        .attr("cy", d => y(d.price))
        .attr("r", 5)
        .style("fill", d => d.quantity < 100 ? "red" : d.quantity <= 1000 ? "blue" : "green");

    svg.selectAll(".label")
        .data(data)
        .enter().append("text")
        .attr("class", "label")
        .attr("x", d => x(d.index))
        .attr("y", d => y(d.price) - 10)
        .attr("text-anchor", "middle")
        .text(d => `${d.name} (${d.price})`);
}
