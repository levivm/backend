/**
* Register controller
* @namespace thinkster.authentication.controllers
*/
(function () {
  'use strict';


  angular
    .module('trulii.authentication.controllers')
    .controller('EmailConfirmCtrl', EmailConfirmCtrl);

  EmailConfirmCtrl.$inject = ['$scope', 'Authentication','$modal','$http','$routeParams'];
  /**
  * @namespace RegisterController
  */
  function EmailConfirmCtrl($scope, Authentication,$modal,$http,$routeParams) {

    var error = false;
    Authentication.confirm_email($routeParams.confirmation_key);

    var modalInstance = $modal.open({
      templateUrl: 'static/partials/authentication/email_confirm.html',
      controller: 'ModalInstanceCtrl',
    });

  };

  })();