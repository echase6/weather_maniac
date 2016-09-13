'use strict';

var sourceForm = $('form');


function runQuery(event) {
  event.preventDefault();
  var actionURL = sourceForm.attr('action');
  var submitMethod = sourceForm.attr('method');
  var formData = sourceForm.serialize();
  return Promise.resolve($.ajax({
    dataType: 'json',
    url: actionURL,
    method: submitMethod,
    data: formData
  })).then(display_results);
}

function display_results(json) {
    var search_text = [
      'Search: ',
      json.word,
      ', count: ',
      json.word_count,
      ', freq: ',
      json.word_freq * 100,
      '%'
  ].join('')

  var item = $('<li>').text(search_text).on(
    'dblclick',
    function(event) {
      $(event.currentTarget).remove();
    }
  );
  $('ul').append(item);
}


function registerEventHandlers() {
  sourceForm.on('submit', runQuery);
}

$(document).ready(registerEventHandlers);
