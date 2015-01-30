/**
* Register controller
* @namespace thinkster.organizers.controllers
*/
(function () {
  'use strict';


  angular
    .module('trulii.activities.controllers')
    .controller('ActivityDBLocationController', ActivityDBLocationController);

  ActivityDBLocationController.$inject = ['$scope','$log','uiGmapGoogleMapApi','activity','cities'];
  /**
  * @namespace ActivityDBLocationController
  */
  function ActivityDBLocationController($scope,$log,uiGmapGoogleMapApi,activity,cities) {




    console.log('Ciudades',cities);

    initialize();

    $scope.cities = cities;

    $scope.activity = activity;

    $scope.save_activity = _updateActivity;

    $scope.setOverElement = _setOverElement;

    $scope.showTooltip = _showTooltip;

    

    
    //$scope.map = { center: { latitude: 45, longitude: -73 }, zoom: 8 };
    $scope.map = {center: {latitude: 40.1451, longitude: -99.6680 }, zoom: 4 };

    uiGmapGoogleMapApi.then(function(maps) {

    });


    /******************ACTIONS**************/


    
    function _updateActivity() {
        console.log("actividad");
        _setActivityPos();
        console.log($scope.activity);
        $scope.activity.update()
            .success(function(response){
                $scope.isCollapsed = false;
            })
            .error(_errored);
    }

    function _showTooltip(element){

        if ($scope.currentOverElement==element)
            return true
        return false
    }


    function _setOverElement(element){

        $scope.currentOverElement = element;
    }



    /*****************SETTERS********************/

    function _setActivityPos(){
      console.log($scope.marker);
      //var location = {
        //'city':$scope.city.id

      ///}
      $scope.activity.location.point = $scope.marker.coords;
      //$scope.marker.coords;
      //$scope.activity.setData({'location':$scope.marker.coords});
      //$scope.activity.location = 
      //$scope.activity.location = 1;
      console.log($scope.activity,"bbbbbbbbb");
    }

    function _setMarker(){


      $scope.marker = {
        id: 0,
        coords: {
          latitude: 40.1451,
          longitude: -99.6680
        },
        options: { draggable: true },
        events: {
          dragend: function (marker, eventName, args) {
            $log.log('marker dragend');
            var lat = marker.getPosition().lat();
            var lon = marker.getPosition().lng();
            $log.log(lat);
            $log.log(lon);

            $scope.marker.options = {
              draggable: true,
              labelContent: "lat: " + $scope.marker.coords.latitude + ' ' + 'lon: ' + $scope.marker.coords.longitude,
              labelAnchor: "100 0",
              labelClass: "marker-labels"
            };
          }
        }
      };


  }


    /*********RESPONSE HANDLERS***************/





    function _clearErrors(){
        $scope.activity_location_form.$setPristine();
        $scope.errors = null;
        $scope.errors = {};
    }



    function _addError(field, message) {
      $scope.errors[field] = message;
      console.log('fiellld',field);
      $scope.activity_location_form[field].$setValidity(message, false);

    };

    function _errored(errors) {
        angular.forEach(errors, function(message,field) {


          _addError(field,message[0]);   

        });

    }


    function activate() {
      // If the user is authenticated, they should not be here.

    }

    function initialize(){

        $scope.errors = {};
        $scope.isCollapsed = true;
        _setMarker();


    }

  };

  })();