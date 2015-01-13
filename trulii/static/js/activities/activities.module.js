(function () {
  'use strict';

  angular
    .module('trulii.activities', [
      'trulii.activities.controllers',
      'trulii.activities.services',
    ]);

  angular
    .module('trulii.activities.controllers',[])
    .controller('CreateActivitiesController', function(){


        alert('ejecut');

    });

    console.log(angular.module('trulii.activities.controllers'));

  angular
    .module('trulii.activities.services', ['ngCookies']);

})();