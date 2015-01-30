/**
* Register controller
* @namespace thinkster.organizers.controllers
*/
(function () {
  'use strict';


  angular
    .module('trulii.activities.controllers')
    .controller('ActivityDBLocationController', ActivityDBLocationController);

  ActivityDBLocationController.$inject = ['$scope','$log','uiGmapGoogleMapApi','filterFilter','activity','cities'];
  /**
  * @namespace ActivityDBLocationController
  */
  function ActivityDBLocationController($scope,$log,uiGmapGoogleMapApi,filterFilter,activity,cities) {




    

    $scope.cities = cities;

    $scope.activity = activity;

    initialize();

    $scope.save_activity = _updateActivity;

    $scope.setOverElement = _setOverElement;

    $scope.showTooltip = _showTooltip;



    
    //$scope.map = { center: { latitude: 45, longitude: -73 }, zoom: 8 };
    

    uiGmapGoogleMapApi.then(function(maps) {

        _setMarker(); 

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

      //faltar chequear cuando la activdad no tengo locacion al principio
      $scope.marker = {
        id: 0,
        coords: {
          latitude: $scope.activity.location.point[1],
          longitude: $scope.activity.location.point[0]
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
        var city   = filterFilter($scope.cities,{id:$scope.activity.city}).pop();
        var latitude  =  city.point[0];
        var longitude = city.point[1];
        $scope.map = {center: {latitude: latitude, longitude: longitude }, zoom: 4 };

        


    }

  };

  })();