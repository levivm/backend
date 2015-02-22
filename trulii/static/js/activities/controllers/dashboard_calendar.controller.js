/**
* Register controller
* @namespace thinkster.organizers.controllers
*/
(function () {
  'use strict';


  angular
    .module('trulii.activities.controllers')
    .controller('ActivityCalendarController', ActivityCalendarController);

  ActivityCalendarController.$inject = ['$scope','$timeout','activity','datepickerPopupConfig','calendar'];
  /**
  * @namespace ActivityCalendarController
  */
  function ActivityCalendarController($scope,$timeout,activity,datepickerPopupConfig,calendar) {



  console.log("calendariooooooooooo",calendar);
  //$scope.startOpened = false;
  var vm = this;
  //vm.start_date = "asdasd";
  

  };

  })();