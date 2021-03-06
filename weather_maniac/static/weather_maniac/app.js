'use strict';


/**
 * Add clip path, x, y axes, and legend.
 * @param {[type]} svg         [description]
 * @param {[type]} xAxis       [description]
 * @param {[type]} yAxis       [description]
 * @param {[type]} margin      [description]
 * @param {[type]} chartWidth  [description]
 * @param {[type]} chartHeight [description]
 */
function addAxesAndLegend(svg, xAxis, yAxis, margin, chartWidth, chartHeight) {
  var legendWidth  = 100,
    legendHeight = 240,
    radius = 16;

  var axes = svg.append('g').
    attr('clip-path', 'url(#axes-clip)');

  axes.append('g').
    attr('class', 'x axis').
    attr('transform', 'translate(0,' + chartHeight + ')').
    call(xAxis);

  axes.append('g').
    attr('class', 'y axis').
    call(yAxis).
    append('text').
      attr('transform', 'rotate(-90)').
      attr('y', 6).
      attr('dy', '.71em').
      style('text-anchor', 'end').
      text('Degrees (F)');

  var legend = svg.append('g').
    attr('class', 'legend').
    attr('transform', 'translate(' + (chartWidth + 40) + ', 100)');

  legend.append('rect').
    attr('class', 'legend-bg').
    attr('width',  legendWidth).
    attr('height', legendHeight);

  legend.append('text').
    attr('x', 15).
    attr('y', 25).
    text('Forecast');

  legend.append('circle').
    attr('class', 'marker-bg').
    attr('cx', 50).
    attr('cy', 53).
    attr('r', radius);

  legend.append('text').
    attr('x', 50).
    attr('y', 57).
    attr('text-anchor', 'middle').
    text('##');

  legend.append('rect').
    attr('class', 'outer').
    attr('width',  80).
    attr('height', 20).
    attr('x', 10).
    attr('y', 120);

  legend.append('text').
    attr('x', 50).
    attr('y', 105).
    attr('text-anchor', 'middle').
    text('90% Confid.');

  legend.append('rect').
    attr('class', 'inner').
    attr('width',  80).
    attr('height', 20).
    attr('x', 10).
    attr('y', 200);

  legend.append('text').
    attr('x', 50).
    attr('y', 185).
    attr('text-anchor', 'middle').
    text('50% Confid.');
}

/**
 * Append the outer, inner and edian paths to the svg.
 * @param  {[type]} svg  [description]
 * @param  {[type]} data [description]
 * @param  {[type]} x    [description]
 * @param  {[type]} y    [description]
 */
function drawPaths(svg, data, x, y) {
  var upperOuterArea = d3.svg.area().
    interpolate('basis').
    x(function(d) { return x(d.date) || 1; }).
    y0(function(d) { return y(d.pct95); }).
    y1(function(d) { return y(d.pct75); });

  var innerArea = d3.svg.area().
    interpolate('basis').
    x(function(d) { return x(d.date) || 1; }).
    y0(function(d) { return y(d.pct75); }).
    y1(function(d) { return y(d.pct25); });

  var lowerOuterArea = d3.svg.area().
    interpolate('basis').
    x(function(d) { return x(d.date) || 1; }).
    y0(function(d) { return y(d.pct25); }).
    y1(function(d) { return y(d.pct05); });

  svg.datum(data);

  svg.append('path').
    attr('class', 'area upper outer').
    attr('d', upperOuterArea).
    attr('clip-path', 'url(#rect-clip)');

  svg.append('path').
    attr('class', 'area lower outer').
    attr('d', lowerOuterArea).
    attr('clip-path', 'url(#rect-clip)');

  svg.append('path').
    attr('class', 'area upper inner').
    attr('d', innerArea).
    attr('clip-path', 'url(#rect-clip)');
}

/**
 * Add an individual marker.
 * @param {[type]} marker      [description]
 * @param {[type]} svg         [description]
 * @param {[type]} chartHeight [description]
 * @param {[type]} x           [description]
 * @param {[type]} y           [description]
 */
function addMarker(marker, svg, chartHeight, x, y) {
  var radius = 16,
    xPos = x(marker.date) - radius - 3,
    yPos = y(marker.value) - radius - 3;

  var markerG = svg.append('g').
    attr('class', 'marker').
    attr('text-anchor', 'middle').
    attr('transform', 'translate(' + xPos + ', ' + yPos + ')').
    attr('opacity', 0);

  markerG.transition().
    duration(1000).
    attr('transform', 'translate(' + xPos + ', ' + yPos + ')').
    attr('opacity', 1);

  markerG.append('circle').
    attr('class', 'marker-bg').
    attr('cx', radius).
    attr('cy', radius).
    attr('r', radius);

  markerG.append('text').
    attr('x', radius).
    attr('y', 21).
    text(marker.value);
}

/**
 * Stars animation of the graph first, then the markers
 * @param  {[type]} svg         [description]
 * @param  {[type]} chartWidth  [description]
 * @param  {[type]} chartHeight [description]
 * @param  {[type]} rectClip    [description]
 * @param  {[type]} markers     [description]
 * @param  {[type]} x           [description]
 * @param  {[type]} y           [description]
 */
function startTransitions(svg, chartWidth, chartHeight,
                          rectClip, markers, x, y) {
  markers.forEach(function(marker, i) {
    setTimeout(function() {
      addMarker(marker, svg, chartHeight, x, y);
    }, 100 + 100 * i);
  });

  rectClip.transition().
    duration(1000).
    delay(200 + 100 * markers.length).
    attr('width', chartWidth);
}

/**
 * The function to create the chart
 * @param  {[type]} data    JSON object holding the data
 * @param  {[type]} markers JSON object holding the markers (unused)
 */
function makeChart(data, markers) {
  var svgWidth  = 960,
    svgHeight = 500,
    margin = {top: 20, right: 140, bottom: 40, left: 40},
    chartWidth  = svgWidth  - margin.left - margin.right,
    chartHeight = svgHeight - margin.top  - margin.bottom;

  var yMin = d3.min(data, function(d) { return d.pct05; }),
    yMax = d3.max(data, function(d) { return d.pct95; });

  var yCent = (yMin + yMax) / 2;
  yMin = yCent - 2 * (yCent - yMin);
  yMax = yCent + 2 * (yMax - yCent);

  var x = d3.time.scale().range([0, chartWidth]).
            domain(d3.extent(data, function(d) { return d.date; })),
    y = d3.scale.linear().range([chartHeight, 0]).
            domain([yMin, yMax]);

  var xAxis = d3.svg.axis().scale(x).orient('bottom').
                innerTickSize(-chartHeight).
                outerTickSize(0).
                tickPadding(10).
                ticks(d3.time.days, 1).
                tickFormat(d3.time.format('%a %e')),
    yAxis = d3.svg.axis().scale(y).orient('left').
                innerTickSize(-chartWidth).
                outerTickSize(0).
                tickPadding(10);

  if ($('svg').length) { $('svg').remove();}

  var svg = d3.select('#graph').append('svg').
    attr('width',  svgWidth).
    attr('height', svgHeight).
    append('g').
      attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

  // clipping to start chart hidden and slide it in later
  var rectClip = svg.append('clipPath').
    attr('id', 'rect-clip').
    append('rect').
      attr('width', 0).
      attr('height', chartHeight);

  addAxesAndLegend(svg, xAxis, yAxis, margin, chartWidth, chartHeight);
  drawPaths(svg, data, x, y);
  startTransitions(svg, chartWidth, chartHeight, rectClip, markers, x, y);
}

var parseDate  = d3.time.format('%Y-%m-%d').parse;

/**
 * The Main function to display the graph, using the provided JSON data.
 * @param  {[type]} dataJson [description]
 */
function displayGraph(dataJson) {
  $('html,body').css('cursor', 'default');
  $('#crazy').remove();

  var data = dataJson.map(function(d) {
    return {
      date: parseDate(d.date),
      pct05: d.pct05,
      pct25: d.pct25,
      pct50: d.pct50,
      pct75: d.pct75,
      pct95: d.pct95
    };
  });

  var markers = dataJson.map(function(marker) {
    return {
      date: parseDate(marker.date),
      value: marker.source_raw
    };
  });

  makeChart(data, markers);
}
