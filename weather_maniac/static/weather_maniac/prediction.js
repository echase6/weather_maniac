'use strict';

var sourceForm = $('form');


function runQuery(event) {
  event.preventDefault();
  $('html,body').css( 'cursor', 'wait' );
  var actionURL = sourceForm.attr('action');
  var submitMethod = sourceForm.attr('method');
  var formData = sourceForm.serialize();
  return Promise.resolve($.ajax({
    dataType: 'json',
    url: actionURL,
    method: submitMethod,
    data: formData
  })).then(display_graph);
}


function registerEventHandlers() {
  sourceForm.on('submit', runQuery);
}

$(document).ready(registerEventHandlers);
