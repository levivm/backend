-/**
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
    


  
  formModal.$inject  = ['$http','$compile','$modal'];

  function formModal($http,$compile,$modal) { 

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
            console.log("template",element);




          //return the Link function
          return function(scope, element, lAtts) {




            loader.then(function() {
              //compile templates/form_modal.html and wrap it in a jQuery object

              $element = $( $compile(template)(scope) );
              $element.on('hide.bs.modal',function(res){
                scope.formErrors = {};
              });

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

                    if (field!='__all__')
                      scope.generic_form[field].$setValidity('server', false);


                  });
                  

                }).success(function(data){


                  

                });
              } else if (result === false) {
                //noop
                console.log('show errors');
              } else {
                $element.modal('hide');
              }
            };

            element.bind('click', function(e) {

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
    console.log('calling the controller');

    $scope.set_usertype = function function_name(user_type) {
      $scope.user_type = user_type;
    }

    $scope.user = {};
    $scope.errors = {};
    $scope.user.user_type = $scope.user_type;
    
    $scope.$watch("user_type", function(){
      $scope.user.user_type = $scope.user_type;
    });

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
      return Authentication.register($scope.user.email, $scope.user.password1,
                                     $scope.user.first_name, $scope.user.last_name,
                                     $scope.user.user_type)
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
            console.log("aqui");
            ctrl.$setValidity('server', true);

          });

        });
      }
    }

  };

})();