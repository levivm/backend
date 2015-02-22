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
      register: register,
      confirm_email:confirm_email,
      getAuthenticatedAccount: getAuthenticatedAccount,
      isAuthenticated: isAuthenticated,
      login: login,
      logout:logout,
      reset_password:reset_password,
      updateAuthenticatedAccount: updateAuthenticatedAccount,
      unauthenticate: unauthenticate,
      getCurrentUser:getCurrentUser

    };



    return Authentication;

    ////////////////////


    function _parseParam(obj) {
      var query = '', name, value, fullSubName, subName, subValue, innerObj, i;
        
      for(name in obj) {
        value = obj[name];
          
        if(value instanceof Array) {
          for(i=0; i<value.length; ++i) {
            subValue = value[i];
            fullSubName = name + '[]';
            innerObj = {};
            innerObj[fullSubName] = subValue;
            query += param(innerObj) + '&';
          }
        }
        else if(value instanceof Object) {
          for(subName in value) {
            subValue = value[subName];
            fullSubName = name + '[' + subName + ']';
            innerObj = {};
            innerObj[fullSubName] = subValue;
            query += param(innerObj) + '&';
          }
        }
        else if(value !== undefined && value !== null)
          query += encodeURIComponent(name) + '=' + encodeURIComponent(value) + '&';
      }
        
      return query.length ? query.substr(0, query.length - 1) : query;
    };

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


      // return $http.post('/users/signup/', {
      //   //username: username,
      //   password1: password,
      //   email: email,
      //   first_name: first_name,
      //   last_name: last_name,
      //   user_type: user_type
      // });

      var request = $http({
        method: 'post',
        url: '/users/signup/',
        data:_parseParam({
          password1: password,
          email: email,
          first_name: first_name,
          last_name: last_name,
          user_type: user_type
        }),
        headers: { 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'},

      });

      return request

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

      var request = $http({
        method: 'post',
        url: '/users/login/',
        data:_parseParam({
          login:email,
          password:password
        }),
        headers: { 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'},
        //headers: { 'Content-Type': 'application/json'},
      })
      return request
      // return $http.post('/users/login/', {
      //   login: email, password: password
      // },
      
      // );
    }

    function logout() {

      var request = $http({
        method: 'post',
        url: '/users/logout/',
      }).success(unauthenticate);

      return request
    }




    /**
     * @name login
     * @desc Try to log in with email `email` and password `password`
     * @param {string} email The email entered by the user
     * @param {string} password The password entered by the user
     * @returns {Promise}
     * @memberOf thinkster.authentication.services.Authentication
     */
    function confirm_email(confirmation_key) {
      return $http.post('/users/confirm-email/'+confirmation_key, {})
    }

    function reset_password(email) { 


      var request = $http({
        data:_parseParam({'email':email}),
        headers: { 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'},
      });

      return request
      // return $http.post('/password/reset/',


      //   ).success( function(response) {
      //   console.log('password reset');
      //   console.log(response);

      // });
    }

    function getCurrentUser(){

      return $http.get('api/users/current/');
      

    }


    /**
     * @name getAuthenticatedAccount
     * @desc Return the currently authenticated account
     * @returns {object|undefined} Account if authenticated, else `undefined`
     * @memberOf thinkster.authentication.services.Authentication
     */
    function getAuthenticatedAccount() {
      if (!$cookies.authenticatedAccount) {
        return;
      }

      return JSON.parse($cookies.authenticatedAccount);
    }

    /**
     * @name isAuthenticated
     * @desc Check if the current user is authenticated
     * @returns {boolean} True is user is authenticated, else false.
     * @memberOf thinkster.authentication.services.Authentication
     */
    function isAuthenticated() {
      return !!$cookies.authenticatedAccount;
    }


    /**
     * @name updateAuthenticatedAccount
     * @desc Stringify the account object and store it in a cookie
     * @param {Object} user The account object to be stored
     * @returns {undefined}
     * @memberOf thinkster.authentication.services.Authentication
     */
    function updateAuthenticatedAccount() {

      getCurrentUser().success(function(response){

          console.log('loggeddddddd',response);
         $cookies.authenticatedAccount = JSON.stringify(response);

      });
      
    }


    /**
     * @name unauthenticate
     * @desc Delete the cookie where the user object is stored
     * @returns {undefined}
     * @memberOf thinkster.authentication.services.Authentication
     */
    function unauthenticate() {
      console.log('loggout');
      delete $cookies.authenticatedAccount;
    }


  }



})();