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



    var vm = this;

    vm.cities = cities;

    vm.activity = angular.copy(activity);



    initialize();

    vm.save_activity  = _updateActivity;

    vm.setOverElement = _setOverElement;

    vm.showTooltip    = _showTooltip;



    
    //vm.map = { center: { latitude: 45, longitude: -73 }, zoom: 8 };
    
    // console.log("maps",vm);
    // uiGmapGoogleMapApi.then(function(maps) {


    // });


    // uiGmapIsReady.promise().then(function(instances) { 
    //   vm.map_instance = instances.pop().map;
      
    // });



    /******************ACTIONS**************/


    
    function _updateActivity() {
        _clearErrors();
        _setActivityPos();
        //var city_object = {};
        //angular.extend(city_object,vm.activity.location.city);
        //var city_object = vm.activity.location.city.copy();
        //vm.activity.location.city = vm.activity.location.city.id;
        console.log("BEFORE UPDATE",vm.activity.location);
        vm.activity.update()
            .success(function(response){
                vm.isCollapsed = false;
                angular.extend(vm.activity,activity);

            })
            .error(_errored);
    }

    function _showTooltip(element){

        if (vm.currentOverElement==element)
            return true
        return false
    }


    function _setOverElement(element){

        vm.currentOverElement = element;
    }



    /*****************SETTERS********************/

    function _setActivityPos(){
      vm.activity.location.point = [];
      vm.activity.location.point[0] = vm.marker.coords.latitude;
      vm.activity.location.point[1] = vm.marker.coords.longitude;
      //vm.activity.location.point = vm.marker.coords;
    }




    /*********RESPONSE HANDLERS***************/





    function _clearErrors(){

        vm.activity_location_form.$setPristine();
        vm.errors = {};
    }



    function _addError(field, message) {
      vm.errors[field] = message;
      vm.activity_location_form[field].$setValidity(message, false);
      console.log("FORMMMM",vm.activity_location_form[field]);

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

        vm.errors = {};
        vm.isCollapsed = true;
        console.log("INIIIIT",vm.activity);
        var city_id;
        //console.log("-----------------------------------");
        var city  = vm.activity.location ? vm.activity.location.city : null;
        //console.log("ACTIVITY",vm.activity);
        //console.log("ACTIVITY CITY",vm.activity.location);

        //console.log("ACTIVITY CITY 2",vm.activity.location.city);
        //console.log("ACTIVITY CITY 3",vm.activity.location);
        
        //console.log("city",vm.activity.location );
        if (city){
          city_id = typeof city == 'number' ? city:city.id;
          //console.log("1",city_id);
          //console.log();
        }
        else{
          //console.log("asda",LocationManager.getCurrentCity());
          city_id = LocationManager.getCurrentCity().id;
          //vm.activity.location = {};
          console.log("2",city_id);

        }
        vm.activity.location.city = filterFilter(vm.cities,{id:city_id})[0];
        console.log(vm.activity.location,vm.cities,city_id);
          



        // if (!(vm.activity.location.city)){
        //   var current_city =  LocationManager.getCurrentCity();
        //   //console.log("SDDD",filterFilter(vm.cities,{id:current_city.id}));
        //   vm.activity.location.city =filterFilter(vm.cities,{id:current_city.id})[0];
        // }
        // else{
        //   var city_id = vm.activity.location.city;
        //   vm.activity.location.city =filterFilter(vm.cities,{id:city_id})[0];
        // }
        
        _initialize_map();
        _setMarker(); 




        //vm.map.control.allowedBounds = _objectToBounds(LocationManager.getAllowedBounds());



    }

    function _initialize_map(){

        //var city =  vm.activity.location.city;
        var latitude;
        var longitude;
        var location = {};

        //location = vm.activity.location.city ? 
        if (vm.activity.location.point)
          location = angular.copy(vm.activity.location);
          //location = vm.activity.location;
        else
          location = angular.copy(vm.activity.location.city);
          //location = vm.activity.location.city;

        latitude  = location.point[0];
        longitude = location.point[1];


        vm.map = {
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

                vm.map.control.valid_center = map.getCenter();
                return
              };

              map.panTo(vm.map.control.valid_center);

            }

          },
          control : {
            allowedBounds : LocationManager.getAllowedBounds()

          }

        };

    }

    function _setMarker(){

      //faltar chequear cuando la activdad no tengo locacion al principio
      var latitude = vm.activity.location.point ? 
                     vm.activity.location.point[0] : vm.activity.location.city.point[0];
      var longitude = vm.activity.location.point ? 
                     vm.activity.location.point[1] : vm.activity.location.city.point[1];

      vm.marker = {
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

            vm.marker.options = {
              draggable: true,
              labelContent: "lat: " + vm.marker.coords.latitude + ' ' + 'lon: ' + vm.marker.coords.longitude,
              labelAnchor: "100 0",
              labelClass: "marker-labels"
            };
          }
        }
      };


    }
       

  };

  })();