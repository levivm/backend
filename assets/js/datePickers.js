require('../css/mdDateTimePicker.css');
var mdDateTimePicker = require('md-date-time-picker');

module.exports = function() {
  var dateFormat = 'YYYY-MM-DD';

  var fechaDesde = document.getElementById('fecha_desde');
  var fechaDesdePicker = new mdDateTimePicker.default({
    type: 'date',
    trigger: fechaDesde
  });

  fechaDesde.addEventListener('click', function() {
    fechaDesdePicker.time = moment(fechaDesde.value, dateFormat);
    fechaDesdePicker.toggle();
  });

  fechaDesde.addEventListener('onOk', function() {
    this.value = fechaDesdePicker.time.format(dateFormat);
  });

  var fechaHasta = document.getElementById('fecha_hasta');
  var fechaHastaPicker = new mdDateTimePicker.default({
    type: 'date',
    trigger: fechaHasta
  });

  fechaHasta.addEventListener('click', function() {
    fechaHastaPicker.time = moment(fechaHasta.value, dateFormat);
    fechaHastaPicker.toggle();
  });

  fechaHasta.addEventListener('onOk', function() {
    this.value = fechaHastaPicker.time.format(dateFormat);
  });

  var filterDate = document.getElementById('filter_date');
  filterDate.addEventListener('click', function () {
    document.getElementById('filter_date_form').submit();
  });
};
