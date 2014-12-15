(function () {
  //'use strict';

  // angular.module('trulii.authentication.directives').directive('formModal', ['$http','$compile',function() {
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

  //       console.log("COMPILE");
  //       var template,
  //         $element,
  //         loader;

  //       loader = $http.get('/static/template/form_modal.html')
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

})

