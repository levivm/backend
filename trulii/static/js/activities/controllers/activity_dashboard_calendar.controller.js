/**
* Register controller
* @namespace thinkster.organizers.controllers
*/
(function () {
  'use strict';


  angular
    .module('trulii.activities.controllers')
    .controller('ActivityCalendarController', ActivityCalendarController);

  ActivityCalendarController.$inject = ['$scope','$timeout','activity'];
  /**
  * @namespace ActivityCalendarController
  */
  function ActivityCalendarController($scope,$timeout,activity) {


    $scope.numb_objects = 0;
    $scope.objects = [];
    $scope.input_price = 0;

    $scope.alerts = [];
    $scope.dates_alerts = [];

    $scope.closeAlert = function(key, index) {
      $scope.objects[key].alerts.splice(index, 1);
    };
    $scope.today = function() {
      $scope.dt = new Date();
    };
    $scope.today();

    $scope.clear = function () {
      $scope.dt = null;
    };

  $scope.test = {};
  $scope.middleOpened = false;
    $scope.toggleMin = function() {
      $scope.minDate = $scope.minDate ? null : new Date();
    };
    $scope.toggleMin();

    $scope.dateOptions = {
      formatYear: 'yy',
      startingDay: 1
    };

    $scope.formats = ['dd-MMMM-yyyy', 'yyyy/MM/dd', 'dd.MM.yyyy', 'shortDate'];
    $scope.format = $scope.formats[0];



     $scope.checkValue = function () {
          if ($scope.value > 100) {
              $scope.value = 100;
          }
          valueProgress($scope.value);
      }
      
      $scope.$watch('startdt', function(newval, oldval){
          if($scope.enddt < $scope.startdt) {
              $scope.enddt = '';
          };
      });
      
      $scope.$watch('enddt', function(newval, oldval){
          if($scope.enddt < $scope.startdt) {
              $scope.enddt = '';
          };
      });

    var date = new Date();
    $scope.start = new Date();
    $scope.middle = new Date();
    //$scope.end = new Date(date.getFullYear(), date.getMonth() + 1, 0); Last day of the month
    $scope.end = new Date(new Date().getFullYear(), 11, 31); //last day of the year

    $scope.minStartDate = 0; //fixed date
    $scope.maxStartDate = new Date(); //init value
    $scope.minEndDate = $scope.end; //init value
    $scope.maxEndDate = $scope.end; //fixed date same as $scope.maxStartDate init value
    $scope.middleEndDate = $scope.end;
    //$scope.minMiddleDate = 112;
    $scope.minMiddleDate = $scope.end; //fixed date

    $scope.$watch('start', function(v,c){

      //alert("inside");
      if($scope.start > $scope.end){
        $scope.dates_alerts = [];
        $scope.dates_alerts.push({msg: 'Tu fecha inicial debe ser menor a tu fecha de cierre, introduzca una fecha de cierre mayor o acorde.'});
        //alert("Tu fecha inicial debe ser menor a tu fecha de cierre, introduzca una fecha de cierre mayor o acorde.");
        $scope.start = $scope.end;
        $scope.middle = $scope.start;

      };
      for(var index in $scope.objects){
        //alert("inside objects");
        //alert();
        if($scope.objects[index].date < $scope.start){
          $scope.objects[index].date = $scope.start;
          $scope.objects[index].alerts = [];
          $scope.objects[index].alerts.push({msg: 'Tu fecha de sesión debe ser mayor a tu fecha de inicio, tu fecha de sesión fue modificada.'});
        
          //alert("Tu fecha de sesión debe ser mayor a tu fecha de inicio, tu fecha de sesión fue modificada.");
        };
          
        
      };
      //if($scope.start > $scope.middle){
      //  alert("Tu fecha inicial debe ser menor a tu fecha de sesión, tu fecha de sesión fue modificada.");
        //$scope.start = $scope.end;
       // $scope.middle = $scope.start;
      //}

      $scope.minEndDate = $scope.start;
      $scope.minMiddleDate = v;
      $scope.test = v;
      //console.log("v: "+ v );
      //console.log("c: "+ c );
    });

    $scope.$watch('test', function(v){

        //console.log("watch test: "+v);
    });


    $scope.$watch('end', function(v){
      //console.log("2: "+ $scope.minMiddleDate);
      $scope.maxStartDate = v;
      $scope.middle = $scope.start;


    });

    $scope.checkPrice = function(v){
      alert(v);

    }

    $scope.add_object = function() {
          
          var date_new_object = new Date();
      

           if($scope.numb_objects == 0){
              
              $scope.objects.push({
                date: $scope.start,
                start: new Date($scope.start.getFullYear(), 
                              $scope.start.getMonth(), 
                              $scope.start.getDate(),
                              8,
                              0,
                              0),
                end: new Date($scope.start.getFullYear(), 
                              $scope.start.getMonth(), 
                              $scope.start.getDate(),
                              18,
                              0,
                              0),
                innit: false,
                alerts: $scope.alerts,
              }); 
              $scope.numb_objects = $scope.numb_objects + 1;
           }
           else{

                var today = new Date();
                var new_date = new Date($scope.start.getFullYear(), $scope.start.getMonth(), $scope.start.getDate());
                var new_start = new Date($scope.start.getFullYear(), 
                                  $scope.start.getMonth(), 
                                  $scope.start.getDate(),
                                  8,
                                  0,
                                  0);

                var new_end = new Date($scope.start.getFullYear(), 
                                  $scope.start.getMonth(), 
                                  $scope.start.getDate(),
                                  18,
                                  0,
                                  0);

                if(today.getDate() == new_start.getDate()){
                   //console.log("s the same day");
                    $scope.objects.push({
                      date:today,
                      start: new_start,
                      end: new_end,
                      innit: false,
                      alerts: $scope.alerts,
                    }); 
                    $scope.numb_objects = $scope.numb_objects + 1;

                }else{
                   //console.log("another day, so midnight has passed");
                   //console.log(today); 
                   new_start = new Date(
                      today.getFullYear(),
                      today.getMonth(), 
                      today.getDate()+1
                    );
                   today = new_start;

                      $scope.objects.push({
                      date:today,
                      start: new_start,
                      end: new_end,
                      innit: false,
                      alerts: $scope.alerts,
                    }); 
                    $scope.numb_objects = $scope.numb_objects + 1;
                }
           }
            
        };

    $scope.checkSessionDate = function(key){

      for (var i in $scope.objects){
        if(i!=key){        
          if($scope.objects[key].date.getFullYear() ===  $scope.objects[i].date.getFullYear()
            && $scope.objects[key].date.getMonth() === $scope.objects[i].date.getMonth()
            && $scope.objects[key].date.getDay() === $scope.objects[i].date.getDay()){
   
            $scope.objects[key].date = new Date(
              $scope.start.getFullYear(),
              $scope.start.getMonth(),
              $scope.start.getDate()
              );
            if($scope.objects[key].date.getFullYear() ===  $scope.start.getFullYear()
                && $scope.objects[key].date.getMonth() === $scope.start.getMonth()
                && $scope.objects[key].date.getDay() === $scope.start.getDay()){
                $scope.objects[key].alerts = [];
                $scope.objects[key].alerts.push({msg: 'La fecha de sesión es erronea, su fecha de sesión fue modificada a la fecha de inicio.'});

              //alert("Hay dos fechas de sesión empezando el mismo día que la fecha de inicio.");
                $scope.objects[key].date = $scope.start;
          }
        }

        };
      };
    };

    $scope.delete_object = function() {
      $scope.numb_objects = $scope.numb_objects - 1;
      $scope.objects.pop();  
    };
    $scope.delete_all = function(){
      $scope.numb_objects = 0;
      $scope.objects = [];
    };

   $scope.openStart = function() {
      //alert();
      //$scope.minMiddleDate = $scope.minEndDate;
      $timeout(function() {
        $scope.startOpened = true;
      });
    };

    $scope.openEnd = function() {

      $timeout(function() {
        $scope.endOpened = true;
      });
    };

    $scope.openMiddle = function(key) {

      //alert(key);
      //$scope.objects[key].innit = false;
      //alert($scope.objects[key].innit);
      //$scope.middleOpened = false;
            $timeout(function() {
        //      $scope.middleOpened = true;
              $scope.objects[key].innit = true;
            });

        };

    $scope.dateOptions = {
      'year-format': "'yy'",
      'starting-day': 1
    };




    // time picker controller
        $scope.mytime = new Date();  

        $scope.mytime2 = new Date();
        
        $scope.hstep = 1;
        $scope.mstep = 1;

        $scope.options = {
          hstep: [1, 2, 3],
          mstep: [1, 5, 10, 15, 25, 30]
        };

        $scope.ismeridian = true;
        $scope.toggleMode = function() {
          $scope.ismeridian = ! $scope.ismeridian;
        };

        $scope.update = function() {
          var d = new Date();
          d.setHours( 14 );
          d.setMinutes( 0 );
          $scope.mytime = d;
        };

        $scope.changed = function (key) {

          for (var i in $scope.objects){
            /*console.log("key: "+key);
            console.log($scope.objects[key] === $scope.objects[i]);
            console.log($scope.objects[key].start.getHours());
            console.log($scope.objects[key].start.getMinutes());
            console.log($scope.objects[key].start.getSeconds());
            console.log(" ");
            console.log($scope.objects[i].start.getHours());
            console.log($scope.objects[i].start.getMinutes());
            console.log($scope.objects[i].start.getSeconds());*/
            //console.log($scope.objects[key]);
            //console.log($scope.objects[key]);

            //console.log($scope.objects[i]);
            //console.log($scope.objects[i]);
             if(i!=key){  // we are not checking the object with itself       
                //console.log("inside");
                //console.log($scope.objects[key].start.getFullYear());
                /*console.log($scope.objects[key].date.getFullYear());
                console.log($scope.objects[i].date.getFullYear());
                console.log($scope.objects[key].date.getMonth());
                console.log($scope.objects[i].date.getMonth());
                console.log($scope.objects[key].date.getDate());
                console.log($scope.objects[i].date.getDate());
                */
              if($scope.objects[key].date.getFullYear() == $scope.objects[i].date.getFullYear()
                 && $scope.objects[key].date.getMonth() == $scope.objects[i].date.getMonth()
                 && $scope.objects[key].date.getDate() == $scope.objects[i].date.getDate()
                 ){
                  if($scope.objects[key].start.getHours() === $scope.objects[i].start.getHours()
                    && $scope.objects[key].start.getMinutes() === $scope.objects[i].start.getMinutes()){
                    //console.log("Hay dos fechas de sesión a la misma hora y el mismo día");
                    $scope.objects.pop(key);
                    $scope.objects[key].alerts = [];
                    $scope.objects[key].alerts.push({msg: 'Hay dos fechas de sesión a la misma hora y el mismo día'});

                    //alert("Hay dos fechas de sesión a la misma hora y el mismo día");

                  }
                }
              };
          };
          
          if($scope.objects[key].start > $scope.objects[key].end){
              $scope.objects[key].start  = $scope.objects[key].end;
              $scope.objects[key].alerts = [];
              $scope.objects[key].alerts.push({msg: 'Tu hora de inicio de sesión debe ser menor a tu hora de fin de sesión.'});

              //alert('Tu hora de inicio de sesión debe ser menor a tu hora de fin de sesión.');
          };

        };


        $scope.changed2 = function(key){
          if($scope.objects[key].start > $scope.objects[key].end){
            $scope.objects[key].start  = $scope.objects[key].end;
            $scope.objects[key].alerts = [];
            $scope.objects[key].alerts.push({msg: 'Tu hora de inicio de sesión debe ser menor a tu hora de fin de sesión.'});

            //alert('Tu hora de inicio de sesión debe ser menor a tu hora de fin de sesión.');
          };
        };
        $scope.clear = function() {
          $scope.mytime = null;
        };

       
        /*$scope.$watch('mytime', function(value){
          if($scope.mytime > $scope.mytime2) 
            alert("!");
        });*/
        $scope.$watch('mytime', function(value){
        //  if($scope.mytime > $scope.mytime2) 
            //alert("!");

        });

  };

  })();