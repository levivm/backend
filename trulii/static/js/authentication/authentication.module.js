(function () {
  'use strict';

  angular
    .module('trulii.authentication', [
      'trulii.authentication.controllers',
      'trulii.authentication.services',
      //'trulii.authentication.directives'
    ]);



  angular
    .module('trulii.authentication.controllers',[]);

  angular
    .module('trulii.authentication.services', ['ngCookies']);

  // angular
  //  .module('trulii.authentication.directives',[]);

})();