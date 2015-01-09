/**
* Organizers
* @namespace thinkster.authentication.services
*/
(function () {
  'use strict';

  angular
    .module('trulii.organizers.services')
    .factory('OrganizerService', OrganizerService);

  OrganizerService.$inject = ['$cookies', '$http','Authentication'];

  /**
  * @namespace OrganizerService
  * @returns {Factory}
  */
  function OrganizerService($cookies, $http,Authentication) {



    var OrganizerService = {
      update: update,
    };



    return OrganizerService;


    function update(organizer) {

      var request = $http({
        method: 'put',
        url:'/api/organizers/'+organizer.id+'/',
        data: organizer,
        headers: { 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'},
      });

      return request
    }


  }



})();