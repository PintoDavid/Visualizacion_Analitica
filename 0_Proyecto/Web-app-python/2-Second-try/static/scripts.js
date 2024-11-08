async function enviarArchivos() {
    const jsonFile = document.getElementById('jsonFile').files[0];
    const binFile = document.getElementById('binFile').files[0];

    if (!jsonFile || !binFile) {
        alert("Por favor, seleccione ambos archivos.");
        return;
    }

    const formData = new FormData();
    formData.append('json_file', jsonFile);
    formData.append('bin_file', binFile);

    try {
        const response = await fetch('/procesar_archivos', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            graficarDatos(data);
        } else {
            const error = await response.json();
            alert(`Error: ${error.error}`);
        }
    } catch (error) {
        console.error("Error al enviar los archivos:", error);
    }
}

function graficarDatos(data) {
    const svg = d3.select("#chart").html('').append("svg")
        .attr("width", 800)
        .attr("height", 600);

    const color = d3.scaleOrdinal(d3.schemeCategory10);

    // Escalas
    const xScale = d3.scaleLinear()
        .domain(d3.extent(data, d => d.x))
        .range([50, 750]);

    const yScale = d3.scaleLinear()
        .domain(d3.extent(data, d => d.y))
        .range([550, 50]);

    // Dibujar puntos
    svg.selectAll("circle")
        .data(data)
        .enter()
        .append("circle")
        .attr("cx", d => xScale(d.x))
        .attr("cy", d => yScale(d.y))
        .attr("r", 5)
        .attr("fill", d => color(d.cluster));
    
    // Opcional: etiquetas de centroides
    svg.selectAll("text")
        .data(data)
        .enter()
        .append("text")
        .attr("x", d => xScale(d.x))
        .attr("y", d => yScale(d.y))
        .attr("dy", -10)
        .attr("text-anchor", "middle")
        .style("fill", d => color(d.cluster))
        .text(d => d.cluster);
}
