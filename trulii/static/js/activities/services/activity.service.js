/**
* activities
* @namespace thinkster.authentication.services
*/
(function () {
  'use strict';

  // angular
  //   .module('trulii.activities.services')
  //   .factory('activitieService', activitieService);

  // activitieService.$inject = ['$cookies', '$http','Authentication'];

  // /**
  // * @namespace activitieService
  // * @returns {Factory}
  // */
  // function activitieService($cookies, $http,Authentication) {



  //   var activitieService = {
  //     update: update,
  //   };



  //   return activitieService;


  //   function update(activitie) {

  //     var request = $http({
  //       method: 'put',
  //       url:'/api/activities/'+activitie.id+'/',
  //       data: activitie,
  //       headers: { 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'},
  //     });

  //     return request
  //   }


  // }

  angular
    .module('trulii.activities.services')
    .factory('Activity', Activity);

  Activity.$inject = ['$http'];

  function Activity($http) {  
      
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
              return $http.get('/api/activities/info/');
          },
          load: function(id){
            var scope = this;
            return $http.get('/api/activities/'+id)
              .then(function(response) {
                scope.setData(response.data);
              });
          },
          update: function() {
            return $http({
              method: 'put',
              url:'/api/activities/' + this.id,
              data: this,
              headers: { 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'},
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