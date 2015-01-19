(function () {
  'use strict';

  angular
    .module('trulii.activities', [
      'trulii.activities.controllers',
      'trulii.activities.services',
      'trulii.activities.directives',
    ]);

  angular
    .module('trulii.activities.controllers',['ngTagsInput'])



  angular
    .module('trulii.activities.services', ['ngCookies']);


  angular
    .module('trulii.activities.directives', []);
})();