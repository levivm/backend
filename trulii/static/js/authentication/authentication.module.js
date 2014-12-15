(function () {
  'use strict';

  angular
    .module('trulii.authentication', [
      'trulii.authentication.controllers',
      'trulii.authentication.services'
    ]);

  angular
    .module('trulii.authentication.controllers', []);

  angular
    .module('trulii.authentication.services', ['ngCookies']);
})();