/**
* Register controller
* @namespace thinkster.authentication.controllers
*/
(function () {
  'use strict';



  angular
    .module('trulii.authentication.controllers')
    .controller('RegisterController', RegisterController)
    .directive('formModal',formModal);


  angular
    .module('trulii.authentication.controllers')
    .directive('serverError',serverError);

  angular
    .module('trulii.authentication.controllers')
    

  // angular
  //   .module('trulii.authentication.controllers')
  //   .directive('serverError',serverError);
    
  //   .directive('formModal', ['$http','$compile',function() {
  //   return {
  //     scope: {
  //       formObject: '=',
  //       formErrors: '=',
  //       title: '@',
  //       template: '@',
  //       okButtonText: '@',
  //       formSubmit: '&'
  //     },
  //     compile: function(element, cAtts){
  //       var template,
  //         $element,
  //         loader;

  //       loader = $http.get('partials/form_modal.html')
  //         .success(function(data) {
  //           template = data;
  //         });

  //       //return the Link function
  //       return function(scope, element, lAtts) {
  //         loader.then(function() {
  //           //compile templates/form_modal.html and wrap it in a jQuery object
  //           $element = $( $compile(template)(scope) );
  //         });

  //         //called by form_modal.html cancel button
  //         scope.close = function() {
  //           $element.modal('hide');
  //         };

  //         //called by form_modal.html form ng-submit
  //         scope.submit = function() {
  //           var result = scope.formSubmit();

  //           if (Object.isObject(result)) {
  //             result.success(function() {
  //               $element.modal('hide');
  //             });
  //           } else if (result === false) {
  //             //noop
  //           } else {
  //             $element.modal('hide');
  //           }
  //         };

  //         element.on('click', function(e) {
  //           e.preventDefault();
  //           $element.modal('show');
  //         });
  //       };
  //     }
  //   }
  // }]);

  
  formModal.$inject  = ['$http','$compile','$modal'];

  function formModal($http,$compile,$modal) { 

    //.directive('formModal', ['$http','$compile','$modal',function($http,$compile,$modal) {
      return {
        scope: {
          formObject: '=',
          formErrors: '=',
          title: '@',
          template: '@',
          okButtonText: '@',
          formSubmit: '&formSubmit'
        },
        compile: function(element, cAtts){


          var template,
            $element,
            loader;


          loader = $http.get('/static/partials/form_modal.html')
            .success(function(data) {

              template = data;


            });

          //return the Link function
          return function(scope, element, lAtts) {

            loader.then(function() {
              //compile templates/form_modal.html and wrap it in a jQuery object
              $element = $( $compile(template)(scope) );
            });

            //called by form_modal.html cancel button
            scope.close = function() {
              $element.modal('hide');
            };

            //called by form_modal.html form ng-submit
            scope.submit = function() {
              var result = scope.formSubmit();

              if (angular.isObject(result)) {
                result.success(function() {
                  $element.modal('hide');
                }).error(function(){

                  angular.forEach(scope.formErrors, function(errors, field) {

                    scope.generic_form[field].$setValidity('server', false);


                  });

                }).success(function(data){


                  console.log(data);

                });
              } else if (result === false) {
                //noop
                console.log('show errors');
              } else {
                $element.modal('hide');
              }
            };

            element.on('click', function(e) {

              e.preventDefault();
              $element.modal('show');
            });
          };
        }
      }
  }


  RegisterController.$inject = ['$location', '$scope', 'Authentication','$modal','$http'];

  /**
  * @namespace RegisterController
  */
  function RegisterController($location, $scope, Authentication,$modal,$http) {
    var vm = this;

    
    //vm.user = {};

    $scope.user = {};
    $scope.errors = {};

    $scope.register = register;
    //vm.register = register;



    function _clearErrors(){
      $scope.errors = null;
      $scope.errors = {};
    }



    function _addError(field, message) {

      $scope.errors[field] = message;

    };


        // $scope.form[field].$setValidity('server', false)
        // # keep the error messages from the server
        // $scope.errors[field] = errors.join(', ')


    function _errored(response) {

      if (response['form_errors']) {

        angular.forEach(response['form_errors'], function(errors, field) {

          _addError(field, errors[0]);

        });

      }
    }

    /**
    * @name register
    * @desc Register a new user
    * @memberOf thinkster.authentication.controllers.RegisterController
    */
    function register() {
      _clearErrors();
      return Authentication.register($scope.user.email, $scope.user.password1)
            .error(_errored)
            .success(function(data){

              console.log("success");
              console.log(data);
            });
    }
  }


  //serverError.$inject = [''];

  function serverError(){
    return {
      restrict: 'A',
      require: '?ngModel',
      link: function (scope, element, attrs, ctrl) {

        element.on('change',function(event){

          scope.$apply(function () {
            console.log("control");
            console.log(ctrl);
            ctrl.$setValidity('server', false);

          });

        });
      }
    }

  };

})();