(function () {
  'use strict';

  angular
    .module('trulii.config')
    .config(config);







  config.$inject = ['$locationProvider','$httpProvider'];

  /**
  * @name config
  * @desc Enable HTML5 routing
  */
  function config($locationProvider,$httpProvider) {

    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';

    $locationProvider.html5Mode(true);
    $locationProvider.hashPrefix('!');
    


  }
})();