/**
* Register controller
* @namespace thinkster.authentication.controllers
*/
(function () {
  'use strict';


  angular
    .module('trulii.authentication.controllers')
    .controller('EmailConfirmCtrl', EmailConfirmCtrl);

  EmailConfirmCtrl.$inject = ['$scope', 'Authentication','$modal','$http','$stateParams'];
  /**
  * @namespace RegisterController
  */
  function EmailConfirmCtrl($scope, Authentication,$modal,$http,$stateParams) {

    var error = false;
    Authentication.confirm_email($stateParams.confirmation_key);

    var modalInstance = $modal.open({
      templateUrl: 'static/partials/authentication/email_confirm.html',
      controller: 'ModalInstanceCtrl',
    });

  };

  })();