/**
* Organizers
* @namespace thinkster.authentication.services
*/
(function () {
  'use strict';

  // angular
  //   .module('trulii.organizers.services')
  //   .factory('OrganizerService', OrganizerService);

  // OrganizerService.$inject = ['$cookies', '$http','Authentication'];

  // /**
  // * @namespace OrganizerService
  // * @returns {Factory}
  // */
  // function OrganizerService($cookies, $http,Authentication) {



  //   var OrganizerService = {
  //     update: update,
  //   };



  //   return OrganizerService;


  //   function update(organizer) {

  //     var request = $http({
  //       method: 'put',
  //       url:'/api/organizers/'+organizer.id+'/',
  //       data: organizer,
  //       headers: { 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'},
  //     });

  //     return request
  //   }


  // }

  angular
    .module('trulii.organizers.services')
    .factory('Organizer', Organizer);

  Organizer.$inject = ['$http'];

  function Organizer($http) {  
      
      function Organizer(organizerData) {
          if (organizerData) {
              this.setData(organizerData);
          }
          // Some other initializations related to book
      };

      Organizer.prototype = {
          setData: function(organizerData) {
              angular.extend(this, organizerData);
          },
          load: function(id) {
              var scope = this;
              $http.get('/api/organizers/' + id).success(function(organizerData) {
                  console.log('response');
                  console.log(organizerData);
                  scope.setData(organizerData);
              });
          },
          update: function() {
            return $http({
              method: 'put',
              url:'/api/organizers/' + this.id,
              data: this,
              headers: { 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'},
            });

            //$http.put('/api/organizers/' + this.id, this);
          },
          change_email: function() {
            return $http({
              method: 'post',
              url:'users/email/',
              data: {
                'email':this.user.email,
                'action_add':true,
              },
            });

            //$http.put('/api/organizers/' + this.id, this);
          },
          change_password: function(password_data) {
            console.log(password_data);
            console.log('--------');
            return $http({
              method: 'post',
              url:'/users/password/change/',
              data: password_data,
            });

            //$http.put('/api/organizers/' + this.id, this);
          },
      };
      return Organizer;
  };



})();