/**
* Register controller
* @namespace thinkster.organizers.controllers
*/
(function () {
  'use strict';


  angular
    .module('trulii.activities.controllers')
    .controller('ActivityDBLocationController', ActivityDBLocationController);

  ActivityDBLocationController.$inject = ['$scope','$log','uiGmapGoogleMapApi','uiGmapIsReady','filterFilter','activity','cities','LocationManager'];
  /**
  * @namespace ActivityDBLocationController
  */
  function ActivityDBLocationController($scope,$log,uiGmapGoogleMapApi,uiGmapIsReady,filterFilter,activity,cities,LocationManager) {





    $scope.cities = cities;

    $scope.activity = activity;

    initialize();

    $scope.save_activity  = _updateActivity;

    $scope.setOverElement = _setOverElement;

    $scope.showTooltip    = _showTooltip;



    
    //$scope.map = { center: { latitude: 45, longitude: -73 }, zoom: 8 };
    
    // console.log("maps",$scope);
    // uiGmapGoogleMapApi.then(function(maps) {


    // });


    // uiGmapIsReady.promise().then(function(instances) { 
    //   $scope.map_instance = instances.pop().map;
      
    // });



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
      $scope.activity.location.point = [];
      $scope.activity.location.point[0] = $scope.marker.coords.latitude;
      $scope.activity.location.point[1] = $scope.marker.coords.longitude;
      //$scope.activity.location.point = $scope.marker.coords;
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
        //console.log("FFFF",$scope.activity);
        var city_id;
        var city  = $scope.activity.location ? $scope.activity.location.city : null;
        
        console.log("city",city)
        if (city){
          city_id = city.id;
        }
        else{
          console.log("asda",LocationManager.getCurrentCity());
          city_id = LocationManager.getCurrentCity().id;
          $scope.activity.location = {};
        }
        $scope.activity.location.city =filterFilter($scope.cities,{id:city_id})[0];
          



        // if (!($scope.activity.location.city)){
        //   var current_city =  LocationManager.getCurrentCity();
        //   //console.log("SDDD",filterFilter($scope.cities,{id:current_city.id}));
        //   $scope.activity.location.city =filterFilter($scope.cities,{id:current_city.id})[0];
        // }
        // else{
        //   var city_id = $scope.activity.location.city;
        //   $scope.activity.location.city =filterFilter($scope.cities,{id:city_id})[0];
        // }
        _initialize_map();
        _setMarker(); 




        //$scope.map.control.allowedBounds = _objectToBounds(LocationManager.getAllowedBounds());



    }

    function _initialize_map(){

        //var city =  $scope.activity.location.city;
        var latitude;
        var longitude;
        var location;

        //location = $scope.activity.location.city ? 
        if ($scope.activity.location.point)
          location = $scope.activity.location;
        else
          location = $scope.activity.location.city;

        latitude  = location.point[0];
        longitude = location.point[1];

        console.log("LOCATION",location);

        $scope.map = {
          center: {latitude: latitude, longitude: longitude }, 
          zoom: 8, 
          bounds: LocationManager.getAllowedBounds() ,

          events: {

            bounds_changed : function(map, eventName, args) {

              var _allowedBounds = LocationManager.getAllowedBounds();

              var _northeast = _allowedBounds.northeast;
              var _southwest = _allowedBounds.southwest;
              var  northeast = new google.maps.LatLng(_northeast.latitude,_northeast.longitude);
              var  southwest = new google.maps.LatLng(_southwest.latitude,_southwest.longitude);

              var allowedBounds = new google.maps.LatLngBounds(southwest,northeast);
              


              if (allowedBounds.contains(map.getCenter())) {

                $scope.map.control.valid_center = map.getCenter();
                return
              };

              map.panTo($scope.map.control.valid_center);

            }

          },
          control : {
            allowedBounds : LocationManager.getAllowedBounds()

          }

        };

    }

    function _setMarker(){

      //faltar chequear cuando la activdad no tengo locacion al principio
      var latitude = $scope.activity.location.point ? 
                     $scope.activity.location.point[0] : $scope.activity.location.city.point[0];
      var longitude = $scope.activity.location.point ? 
                     $scope.activity.location.point[1] : $scope.activity.location.city.point[1];

      $scope.marker = {
        id: 0,
        coords: {
          latitude: latitude,
          longitude: longitude
        },
        options: { draggable: true },
        events: {
          dragend: function (marker, eventName, args) {
            $log.log('marker dragend',args.map);
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
       

  };

  })();