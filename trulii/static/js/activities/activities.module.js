(function () {
  'use strict';

  angular
    .module('trulii.activities', [
      'trulii.activities.controllers',
      'trulii.activities.services',
    ]);

  angular
    .module('trulii.activities.controllers',['ngTagsInput'])



  angular
    .module('trulii.activities.services', ['ngCookies']);

})();