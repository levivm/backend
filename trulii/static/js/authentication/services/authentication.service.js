/**
* Authentication
* @namespace thinkster.authentication.services
*/
(function () {
  'use strict';

  angular
    .module('trulii.authentication.services')
    .factory('Authentication', Authentication);

  Authentication.$inject = ['$cookies', '$http'];

  /**
  * @namespace Authentication
  * @returns {Factory}
  */
  function Authentication($cookies, $http) {
    /**
    * @name Authentication
    * @desc The Factory to be returned
    */


    var Authentication = {
      register: register
    };

    return Authentication;

    ////////////////////

    /**
    * @name register
    * @desc Try to register a new user
    * @param {string} username The username entered by the user
    * @param {string} password The password entered by the user
    * @param {string} email The email entered by the user
    * @returns {Promise}
    * @memberOf thinkster.authentication.services.Authentication
    */
    function register(email, password,first_name,last_name,user_type) {


      return $http.post('/users/signup/', {
        //username: username,
        password1: password,
        email: email,
        first_name: first_name,
        last_name: last_name,
        user_type: user_type
      });
     // .success(function(data, status, headers, config) {
     //               //console.log(data);
     //               //console.log(data.form_errors);
     //               //return data
     //  }).error(function(data, status, headers, config) {
     //                console.log("mirame");
     //                console.log(data["form_errors"]);
                    
     //  });

    }

    /**
     * @name login
     * @desc Try to log in with email `email` and password `password`
     * @param {string} email The email entered by the user
     * @param {string} password The password entered by the user
     * @returns {Promise}
     * @memberOf thinkster.authentication.services.Authentication
     */
    function login(email, password) {
      return $http.post('/users/login/', {
        email: email, password: password
      });
    }

  }



})();