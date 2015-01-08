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
    /**
    * @name UploadFile
    * @desc The Factory to be returned
    */


    var OrganizerService = {
      update: update,
    };



    return OrganizerService;

    ////////////////////

    /**
    * @name update
    * @desc Try to update a new user
    * @param {string} username The username entered by the user
    * @param {string} password The password entered by the user
    * @param {string} email The email entered by the user
    * @returns {Promise}
    * @memberOf thinkster.authentication.services.Authentication
    */
    function update(organizer) {
      //var organizer    = Authentication.getAuthenticatedAccount();
      //console.log('rr',{'name':'levis'});
      //var organizer_id = organizer.id;

      //console.log('/api/organizers/'+organizer_id);
      return $http.post('/api/organizers/'+organizer.id+'/', organizer)
    }


  }



})();