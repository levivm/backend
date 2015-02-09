-/**
* Register controller
* @namespace thinkster.authentication.controllers 
*/
(function () {
  'use strict';


  angular
    .module('trulii.landing.controllers')
    .controller('HomeController', HomeController);

  HomeController.$inject = ['$scope','$cookies','LocationManager','cities'];
  /**
  * @namespace RegisterController
  */
  function HomeController($scope,$cookies,LocationManager,cities) {


    //console.log('CITIES',LocationManager.availableCities);
    $scope.cities = cities;

    activate();

    $scope.setCurrentCity = _setCurrentCity; 

    



    function _setCurrentCity(city){

      LocationManager.setCurrentCity(city);
      console.log("cityyyyyyyyyyyyy",city);

    }

    function activate(){


      $scope.current_city = LocationManager.getCurrentCity();
      console.log("ZZZZZ",$scope.current_city);

    }



  }
})();