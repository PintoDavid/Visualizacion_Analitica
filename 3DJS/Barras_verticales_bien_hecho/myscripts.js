var species = ["MAMIFEROS", "AVES", "REPTILES", "ARACNIDOS", "ARTROPODOS", "ANFIBIOS", "MOLUSCOS"];
  var n = species.length;  // Número de especies
  var m = 14; // 14 años (2008-2021)

  // Carga de los datos reales
  var yz = [
    [146, 135, 180, 154, 153, 127, 161, 128, 139, 155, 228, 331, 752, 468], // MAMIFEROS
    [430, 419, 438, 423, 472, 385, 403, 284, 351, 507, 512, 620, 723, 746], // AVES
    [408, 404, 468, 691, 491, 473, 370, 236, 234, 233, 255, 298, 303, 271], // REPTILES
    [1, 2, 5, 4, 3, 6, 3, 2, 0, 0, 0, 0, 1, 0], // ARACNIDOS
    [0, 0, 0, 1, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0], // ARTROPODOS
    [8, 8, 1, 1, 1, 3, 1, 0, 0, 0, 0, 0, 3, 1], // ANFIBIOS
    [1, 0, 4, 7, 4, 33, 2, 0, 0, 0, 0, 150, 3, 0]  // MOLUSCOS
  ];

  var xz = d3.range(2008, 2022);
  var y01z = d3.stack().keys(d3.range(n))(d3.transpose(yz));
  var yMax = d3.max(yz, function(y) { return d3.max(y); });
  var y1Max = d3.max(y01z, function(y) { return d3.max(y, function(d) { return d[1]; }); });

  var svg = d3.select("svg"),
      margin = {top: 80, right: 10, bottom: 20, left: 40},
      width = +svg.attr("width") - margin.left - margin.right,
      height = +svg.attr("height") - margin.top - margin.bottom,
      g = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  var x = d3.scaleBand()
      .domain(xz)
      .rangeRound([0, width])
      .padding(0.08);

  // Ajustar el dominio de la escala Y para que llegue hasta 2000
  var y = d3.scaleLinear()
      .domain([0, 2000])  // Ajustar para que llegue hasta 2000
      .range([height, 0]);

  var color = d3.scaleOrdinal()
      .domain(species)
      .range(["#c6dbef", "#9ecae1", "#6baed6", "#4292c6", "#2171b5", "#08519c", "#08306b"]);

  var series = g.selectAll(".series")
    .data(y01z)
    .enter().append("g")
      .attr("fill", function(d, i) { return color(species[i]); });

  var rect = series.selectAll("rect")
    .data(function(d) { return d; })
    .enter().append("rect")
      .attr("x", function(d, i) { return x(xz[i]); })
      .attr("y", height)
      .attr("width", x.bandwidth())
      .attr("height", 0);

  rect.transition()
      .delay(function(d, i) { return i * 10; })
      .attr("y", function(d) { return y(d[1]); })
      .attr("height", function(d) { return y(d[0]) - y(d[1]); });

  g.append("g")
      .attr("class", "axis axis--x")
      .attr("transform", "translate(0," + height + ")")
      .call(d3.axisBottom(x)
          .tickSize(0)
          .tickPadding(6));

  g.append("g")
      .attr("class", "axis axis--y")
      .call(d3.axisLeft(y)
          .ticks(10)
          .tickSize(0)
          .tickPadding(10));

  d3.selectAll("input")
      .on("change", changed);

  function changed() {
    if (this.value === "grouped") transitionGrouped();
    else transitionStacked();
  }

  function transitionGrouped() {
    y.domain([0, 2000]);  // Mantener el dominio ajustado para agrupado

    rect.transition()
        .duration(500)
        .delay(function(d, i) { return i * 10; })
        .attr("x", function(d, i) { return x(xz[i]) + x.bandwidth() / n * this.parentNode.__data__.key; })
        .attr("width", x.bandwidth() / n)
      .transition()
        .attr("y", function(d) { return y(d[1] - d[0]); })
        .attr("height", function(d) { return y(0) - y(d[1] - d[0]); });
  }

  function transitionStacked() {
    y.domain([0, 2000]);  // Mantener el dominio ajustado para apilado

    rect.transition()
        .duration(500)
        .delay(function(d, i) { return i * 10; })
        .attr("x", function(d, i) { return x(xz[i]); })
        .attr("width", x.bandwidth()) 
        .transition()
        .attr("y", function(d) { return y(d[1]); })
        .attr("height", function(d) { return y(d[0]) - y(d[1]); });
  }