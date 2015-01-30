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
      
      function LocationManager(locationsData) {
          if (locationsData) {
              this.setData(locationsData);
          }

      };

      LocationManager.prototype = {
          setData: function(locationsData) {
              angular.extend(this, locationsData);
          },
          create: function(){
            return $http.post('/api/activities/',this);
          },
          getAvailableCities: function() {
              var scope = this;

              return $http.get('/api/locations/cities/').then(function(response){                
                scope.setData({'availableCities': response.data});
                return response.data
              });



          },
      };
      return LocationManager;
  };



})();