'use strict';

var sourceForm = $('form');

/**
 * Query the server for the graph data, using an AJAX request.
 */
function runQuery(event) {
  event.preventDefault();
  $('html,body').css('cursor', 'wait');
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
