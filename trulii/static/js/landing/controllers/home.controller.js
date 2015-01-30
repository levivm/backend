-/**
* Register controller
* @namespace thinkster.authentication.controllers 
*/
(function () {
  'use strict';


  angular
    .module('trulii.landing.controllers')
    .controller('HomeController', HomeController);

  HomeController.$inject = ['$scope','$modal','$http','cities'];
  /**
  * @namespace RegisterController
  */
  function HomeController($scope,$modal,$http,cities) {

  	console.log("conadasd2",cities);

  }
})();