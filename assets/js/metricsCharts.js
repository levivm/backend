google.charts.load('current', {'packages': ['corechart']});

module.exports = function() {

  google.charts.setOnLoadCallback(drawStudentsRangeDonutChart);
  google.charts.setOnLoadCallback(drawOrganizersRangeDonutChart);
  google.charts.setOnLoadCallback(drawCategoriesRangeBar);

  function drawStudentsRangeDonutChart() {
    var data = new google.visualization.DataTable();
    data.addColumn('string', 'type');
    data.addColumn('number', 'number');
    data.addRows(window.data.general.range.students);

    var options = {
      'pieHole': 0.4,
      'pieSliceText': 'value',
      'width': '100%',
      'height': 350,
      'colors': ['#1565C0', '#2196F3', '#90CAF9']
    };

    var chart = new google.visualization.PieChart(document.getElementById('students_div'));
    chart.draw(data, options);
  }

  function drawOrganizersRangeDonutChart() {
    var data = new google.visualization.DataTable();
    data.addColumn('string', 'type');
    data.addColumn('number', 'number');
    data.addRows(window.data.general.range.organizers);

    var options = {
      'pieHole': 0.4,
      'pieSliceText': 'value',
      'width': '100%',
      'height': 350,
      'colors': ['#558B2F', '#8BC34A', '#C5E1A5']
    };

    var chart = new google.visualization.PieChart(document.getElementById('organizers_div'));
    chart.draw(data, options);
  }

  function drawCategoriesRangeBar() {
    var data = new google.visualization.DataTable();
    data.addColumn('string', 'category');
    data.addColumn('number', 'students');
    data.addColumn('number', 'organizers');
    data.addRows(window.data.general.range.categories);

    var options = {
      'height': 500
    };

    var chart = new google.visualization.BarChart(document.getElementById('categories_by_range'));
    chart.draw(data, options);
  }

};
