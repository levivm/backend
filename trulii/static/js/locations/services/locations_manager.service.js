/**
* activities
* @namespace thinkster.authentication.services
*/
(function () {
  'use strict';

 
  angular
    .module('trulii.locations.services')
    .factory('LocationManager', LocationManager);

  LocationManager.$inject = ['$http','$q'];

  function LocationManager($http,$q) {  
      
      this.availableCities;
      var LocationManager = {
        getAvailableCities :_getAvailableCities
      }

      function _getAvailableCities(){

         var deferred = $q.defer();

        if(this.availableCities){
          deferred.resolve(this.availableCities);
          return deferred.promise
        }
        else{
          var scope = this;
          return $http.get('/api/locations/cities/').then(function(response){    
            scope.availableCities = response.data           
            return response.data
          });

        }

      }

      // function LocationManager(locationsData) {
      //     if (locationsData) {
      //         this.setData(locationsData);
      //     }

      //     this.cache = ['1'];
      //     this.availableCities = this.getAvailableCities();
      //     console.log("sadasdasd",this.getAvailableCities());

      //     // if (!(this.availableCities)){
      //     //   console.log('availableCities',availableCities);
      //     //   this.availableCities = this.getAvailableCities();

      //     // }
      // };

      // LocationManager.prototype = {
      //     setData: function(locationsData) {
      //         angular.extend(this, locationsData);
      //     },
      //     create: function(){
      //       return $http.post('/api/activities/',this);
      //     },
      //     getAvailableCities: function() {
      //         var scope = this;

      //         return $http.get('/api/locations/cities/').then(function(response){                
      //           scope.setData({'availableCities': response.data});
      //           return response.data
      //         });



      //     },
      // };
      return LocationManager;
  };



})();