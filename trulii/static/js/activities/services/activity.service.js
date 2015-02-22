/**
* activities
* @namespace thinkster.authentication.services
*/
(function () {
  'use strict';

 
  angular
    .module('trulii.activities.services')
    .factory('Activity', Activity);

  Activity.$inject = ['$http','$q'];

  function Activity($http,$q) {  
      
      function Activity(activitieData) {
          if (activitieData) {
              this.setData(activitieData);
          }
          this.tags = [];

          // Some other initializations related to book
      };

      Activity.prototype = {
          setData: function(activitieData) {
              angular.extend(this, activitieData);
          },
          create: function(){
            return $http.post('/api/activities/',this);
          },
          generalInfo: function() {
              var scope = this;
              
              var deferred = $q.defer();

              if (scope.presave_info){ 
               
                deferred.resolve(scope.presave_info);                
                return deferred.promise
              }
              else{

                return $http.get('/api/activities/info/').then(function(response){
                  scope.presave_info = response.data;
                  deferred.resolve(scope.presave_info);
                  return deferred.promise
                });

              }

              //return deferred.promise;

          },
          load: function(id){
            var scope = this;

            return $http.get('/api/activities/'+id)
              .then(function(response) {
                scope.setData(response.data);
                return scope
              });
          },
          update: function() {
            return $http({
              method: 'put',
              url:'/api/activities/' + this.id,
              data: this,
              //headers: { 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'},
            });
          }
          //   //$http.put('/api/activities/' + this.id, this);
          // },
          // change_email: function() {
          //   return $http({
          //     method: 'post',
          //     url:'users/email/',
          //     data: {
          //       'email':this.user.email,
          //       'action_add':true,
          //     },
          //   });

          //   //$http.put('/api/activities/' + this.id, this);
          // },
          // change_password: function(password_data) {
          //   console.log(password_data);
          //   console.log('--------');
          //   return $http({
          //     method: 'post',
          //     url:'/users/password/change/',
          //     data: password_data,
          //   });

          //   //$http.put('/api/activities/' + this.id, this);
          // },
      };
      return Activity;
  };



})();