(function () {
  'use strict';



	angular
	.module('trulii', [
	  'ui.bootstrap',
	  'trulii.config',
	  'trulii.routes',
	  'trulii.authentication'

	]);


	angular
  	.module('trulii.config',[]);

	angular
	.module('trulii.routes',['ngRoute']);



	angular.module('trulii').controller('ModalInstanceCtrl', function ($scope, $modalInstance) {

	  // $scope.items = items;
	  // $scope.selected = {
	  //   item: $scope.items[0]
	  // };

	  $scope.ok = function () {
	    $modalInstance.close("1");
	  };

	  $scope.cancel = function () {
	    $modalInstance.dismiss('cancel');
	  };
	});


    angular.module('trulii').directive('formModal', ['$http','$compile','$modal',function($http,$compile,$modal) {
    return {
      scope: {
        formObject: '=',
        formErrors: '=',
        title: '@',
        template: '@',
        okButtonText: '@',
        formSubmit: '&'
      },
      compile: function(element, cAtts){






        var template,
          $element,
          loader;



        loader = $http.get('/static/partials/form_modal.html')
          .success(function(data) {
          	console.log("data");
          	console.log(data);
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

            if (Object.isObject(result)) {
              result.success(function() {
                $element.modal('hide');
              });
            } else if (result === false) {
              //noop
            } else {
              $element.modal('hide');
            }
          };

          element.on('click', function(e) {
          	console.log('hiceeeeeee clickkkkkkkkk');
          	console.log($element);
            e.preventDefault();
			// $modal.open({
		 //      templateUrl: '/static/partials/form_modal.html',
		 //      controller: 'ModalInstanceCtrl',
		 //      //size: size,
		 //      //resolve: {
		 //      //  items: function () {
		 //      //    return $scope.items;
		 //     //   }
		 //      });
            $element.modal('show');
            console.log($element);
          });
        };
      }
    }
  }]);






	angular
	  .module('trulii')
	  .run(run);







	run.$inject = ['$http','$cookies'];








	/**
	* @name run
	* @desc Update xsrf $http headers to align with Django's defaults
	*/
	function run($http,$cookies) {

		//$http.defaults.headers.post['X-CSRFToken'] = $cookies['csrftoken'];
	  $http.defaults.xsrfHeaderName = 'X-CSRFToken';
	  $http.defaults.xsrfCookieName = 'csrftoken';
	}

})();



