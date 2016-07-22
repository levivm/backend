module.exports = function () {
  var dialog = document.querySelector('dialog');
  dialog.querySelector('.close').addEventListener('click', function() {
    dialog.close();
  });

  function sendAjax(type) {
    var url = window.data.export_url +
      '?start_date=' + window.data.start_date +
      '&end_date=' + window.data.end_date +
      '&type=' + type;

    var xhr = new XMLHttpRequest();
    xhr.open('GET', url);
    xhr.send(null);

    xhr.onreadystatechange = function () {
      var DONE = 4;
      var OK = 200;
      if (xhr.readyState === DONE) {
        var p = dialog.querySelector('p');
        if (xhr.status === OK) {
          p.innerText = 'El archivo será enviado a tu email prontamente.';
        } else {
          p.innerText = 'Hubo un problema. Por favor intenta nuevamente.';
        }
      }
    };
  }

  var studentButton = document.getElementById('export-students');
  studentButton.addEventListener('click', function (event) {
    event.preventDefault();
    sendAjax('students');
    dialog.showModal();
  });

  var organizerButton = document.getElementById('export-organizers');
  organizerButton.addEventListener('click', function (event) {
    event.preventDefault();
    sendAjax('organizers');
    dialog.showModal();
  });
};
