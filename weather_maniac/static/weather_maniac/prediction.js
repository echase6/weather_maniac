'use strict';

var sourceForm = $('form');

/**
 * Query the server for the graph data, using an AJAX request.
 */
function runQuery(event) {
  event.preventDefault();
  $('html,body').css('cursor', 'wait');
  if ($('svg').length) { $('svg').remove();}
  $('#graph').prepend($('<img>',{id:'crazy',src:'/static/weather_maniac/crazy.gif', style:"width:300px;height:300px;"}));
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
  sourceForm.on('submit', runQuery);
}

$(document).ready(registerEventHandlers);
