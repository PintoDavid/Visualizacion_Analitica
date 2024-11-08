document.getElementById('file-form').addEventListener('submit', function (event) {
    event.preventDefault();
  });
  
  function processFiles() {
    const folderInput = document.getElementById('folderInput');
    if (!folderInput.files.length) {
      alert('Selecciona una carpeta con archivos');
      return;
    }
  
    const formData = new FormData();
    for (let file of folderInput.files) {
      formData.append('files', file);
    }
  
    fetch('/process_files', {
      method: 'POST',
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      displayClusters(data);
    })
    .catch(error => console.error('Error al procesar archivos:', error));
  }
  
  function displayClusters(data) {
    d3.select("#chart").html("");  // Limpiar el gráfico previo
  
    const width = 800, height = 600;
    const svg = d3.select("#chart")
                  .append("svg")
                  .attr("width", width)
                  .attr("height", height);
  
    const colorScale = d3.scaleOrdinal(d3.schemeCategory10);
    const clusters = {};
  
    data.forEach((d, i) => {
      clusters[d.Cluster] = clusters[d.Cluster] || [];
      clusters[d.Cluster].push(d);
    });
  
    Object.keys(clusters).forEach(cluster => {
      const points = clusters[cluster];
      svg.selectAll(`circle.cluster-${cluster}`)
        .data(points)
        .enter()
        .append("circle")
        .attr("cx", d => d.x)  // Ajustar con el nombre real de las columnas
        .attr("cy", d => d.y)  // Ajustar con el nombre real de las columnas
        .attr("r", 5)
        .attr("fill", colorScale(cluster))
        .attr("opacity", 0.6)
        .attr("class", `cluster-${cluster}`);
    });
  }
  