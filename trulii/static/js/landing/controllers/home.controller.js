-/**
* Register controller
* @namespace thinkster.authentication.controllers 
*/
(function () {
  'use strict';


  angular
    .module('trulii.landing.controllers')
    .controller('HomeController', HomeController);

  HomeController.$inject = ['$scope','$cookies','cities'];
  /**
  * @namespace RegisterController
  */
  function HomeController($scope,$cookies,cities) {

  	console.log("SSSSSSSSSSSS",cities);
    $scope.cita = "sdasd";
    $scope.cities = cities;

  }
})();