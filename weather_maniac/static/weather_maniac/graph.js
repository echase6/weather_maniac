'use strict';

var sourceForm = $('form');


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
    legendHeight = 240;

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
    text('Service A');

  legend.append('path').
    attr('class', 'median-line').
    attr('d', 'M10,80L85,80');

  legend.append('text').
    attr('x', 50).
    attr('y', 105).
    attr('text-anchor', 'middle').
    text('Service B');

  legend.append('text').
    attr('x', 50).
    attr('y', 185).
    attr('text-anchor', 'middle').
    text('Service C');
}

/**
 * Append the outer, inner and edian paths to the svg.
 * @param  {[type]} svg  [description]
 * @param  {[type]} data [description]
 * @param  {[type]} x    [description]
 * @param  {[type]} y    [description]
 */
function drawPaths(svg, data, x, y) {

  var lineA = d3.svg.line().
  // .interpolate('basis')
  x(function(d) { return x(d.date); }).
  y(function(d) { return y(d.sourceA); });

  var lineB = d3.svg.line().
  // .interpolate('basis')
  x(function(d) { return x(d.date); }).
  y(function(d) { return y(d.sourceB); });

  var lineC = d3.svg.line().
  // .interpolate('basis')
  x(function(d) { return x(d.date); }).
  y(function(d) { return y(d.sourceC); });

  svg.datum(data);

  svg.append('path').
    attr('class', 'median-line').
    attr('d', lineA).
    attr('clip-path', 'url(#rect-clip)');

  svg.append('path').
    attr('class', 'median-line').
    attr('d', lineB).
    attr('clip-path', 'url(#rect-clip)');

  svg.append('path').
    attr('class', 'median-line').
    attr('d', lineC).
    attr('clip-path', 'url(#rect-clip)');
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
function startTransitions(svg, chartWidth, chartHeight, rectClip, x, y) {

  rectClip.transition().
    duration(1000).
    // delay(200 + 100 * markers.length).
    attr('width', chartWidth);
}

/**
 * The function to create the chart
 * @param  {[type]} data    JSON object holding the data
 * @param  {[type]} markers JSON object holding the markers (unused)
 */
function makeChart(data) {
  var svgWidth  = 960,
    svgHeight = 500,
    margin = {top: 20, right: 140, bottom: 40, left: 40},
    chartWidth  = svgWidth  - margin.left - margin.right,
    chartHeight = svgHeight - margin.top  - margin.bottom;

  var yMin = d3.min(data, function(d) { return d.sourceA; }),
    yMax = d3.max(data, function(d) { return d.sourceA; });

    yMin = 40;
    yMax = 70;

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
  startTransitions(svg, chartWidth, chartHeight, rectClip, x, y);
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
      sourceA: d.Service_A,
      sourceB: d.Service_B,
      sourceC: d.Service_C
    };
  });

  makeChart(data);
}

/**
 * [runGraph description]
 * @return {[type]} [description]
 */
function runGraph() {
  event.preventDefault();
  $('html,body').css('cursor', 'wait');
  if ($('svg').length) { $('svg').remove();}
  $('#graph').prepend($('<img>',{id: 'crazy',
    src: '/static/weather_maniac/crazy.gif',
    style: 'width:300px;height:300px;'}));
  var actionURL = sourceForm.attr('action');
  var submitMethod = sourceForm.attr('method');
  var formData = sourceForm.serialize();
  return Promise.resolve($.ajax({
    dataType: 'json',
    url: actionURL,
    method: submitMethod,
    data: formData
  })).then(displayGraph);
}

/**
 * When the document is ready, bid runQuery to the submit button.
 * @return {[type]} [description]
 */
function registerEventHandlers() {
  sourceForm.on('submit', runGraph);
}

$(document).ready(runGraph);
