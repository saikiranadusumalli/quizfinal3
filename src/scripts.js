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
                let type = data.type;
                document.getElementById("chart-image").src = `static/${type}_chart.png`;
                // D3.js Visualization
                visualizeWithD3(data.type, data.chartData);
            }
        });
    });
});

function visualizeWithD3(type, data) {
    // Clear any previous SVGs
    d3.select("svg").remove();
    
    if (type === 'pie') {
        // Create a pie chart using D3.js
        const width = 500, height = 500, radius = Math.min(width, height) / 2;
        const color = d3.scaleOrdinal(d3.schemeCategory10);

        const svg = d3.select("#chart").append("svg")
            .attr("width", width)
            .attr("height", height)
            .append("g")
            .attr("transform", `translate(${width / 2}, ${height / 2})`);

        const pie = d3.pie().value(d => d.quantity);
        const path = d3.arc().outerRadius(radius - 10).innerRadius(0);
        const label = d3.arc().outerRadius(radius - 40).innerRadius(radius - 40);

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
    } else if (type === 'bar') {
        // Create a bar chart using D3.js
        const width = 500, height = 300;
        const svg = d3.select("#chart").append("svg")
            .attr("width", width)
            .attr("height", height);

        const x = d3.scaleBand().range([0, width]).padding(0.1);
        const y = d3.scaleLinear().range([height, 0]);

        x.domain(data.map(d => d.name));
        y.domain([0, d3.max(data, d => d.price)]);

        svg.selectAll(".bar")
            .data(data)
            .enter().append("rect")
            .attr("class", "bar")
            .attr("x", d => x(d.name))
            .attr("width", x.bandwidth())
            .attr("y", d => y(d.price))
            .attr("height", d => height - y(d.price))
            .attr("fill", "blue");

        svg.append("g")
            .attr("transform", `translate(0,${height})`)
            .call(d3.axisBottom(x));

        svg.append("g")
            .call(d3.axisLeft(y));
    } else if (type === 'scatter') {
        // Create a scatter plot using D3.js
        const width = 500, height = 300;
        const svg = d3.select("#chart").append("svg")
            .attr("width", width)
            .attr("height", height);

        const x = d3.scaleLinear().range([0, width]);
        const y = d3.scaleLinear().range([height, 0]);

        x.domain([0, d3.max(data, d => d.index)]);
        y.domain([0, d3.max(data, d => d.price)]);

        svg.selectAll(".dot")
            .data(data)
            .enter().append("circle")
            .attr("class", "dot")
            .attr("cx", d => x(d.index))
            .attr("cy", d => y(d.price))
            .attr("r", 5)
            .attr("fill", d => d.quantity < 100 ? 'red' : d.quantity <= 1000 ? 'blue
