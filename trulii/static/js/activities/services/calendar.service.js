/**
* activities
* @namespace thinkster.authentication.services
*/
(function () {
  'use strict';

 
  angular
    .module('trulii.activities.services')
    .factory('Calendar', Calendar);

  Calendar.$inject = ['$http','$q'];

  function Calendar($http,$q) {  
      
      function Calendar(calendarData) {
          if (calendarData) {
              this.setData(calendarData);

          }else{


            var today = new Date();
            //console.log()
            var tomorrow = new Date(new Date().getTime() + 24 * 60 * 60 * 1000);
            this.initial_date = today;
            this.closing_sale = tomorrow;
            this.capacity = 1;




            this.sessions = [];
            this.number_of_sessions = 0;
            this.last_sn = 0;


            //this.toggleMode = function() {
            //  this.ismeridian = ! $scope.ismeridian;
            //};


          }




          //this.tags = [];

          // Some other initializations related to book
      };

      Calendar.prototype = {
          setData: function(calendarData) {

              angular.extend(this, calendarData);
              angular.forEach(this.sessions,function(session){

                session.date = new Date(session.date);
                session.end_time   = new Date(session.end_time);
                session.start_time = new Date(session.start_time);

              });
              this.last_sn = this.number_of_sessions;
              this.sessions.reverse();    


          },
          load: function(activity_id){

            var that = this;
                that.activity = activity_id;

            console.log("activity_id",activity_id);
            return $http.get('/api/activities/'+activity_id+'/calendar/')
                        .then(function(response){
                          
                          that.setData(response.data);
                          //that.sessions.reverse();
                          //that.last_sn = response.data.
                          console.log("BUENAAAA",that);
                          return that

                        },function(response){

                          return that
                        });


          },
          create: function(){
            var activity_id = this.activity;


            var _initial_date = this.initial_date;

            var _closing_sale = this.closing_sale;

            this.initial_date = this.initial_date.valueOf();
            this.closing_sale = this.closing_sale.valueOf();
            angular.forEach(this.sessions,function(session){

              session.date = session.date.valueOf();
              session.end_time = session.end_time.valueOf();
              session.start_time = session.start_time.valueOf();

            });
            console.log(this);
            var that = this;
            return $http.post('/api/activities/'+activity_id+'/calendar/',this)
                        .then(function(response){
                          console.log("responseEEEE",response.data);
                          that.setData(response.data);
                          return response.data
                        },function(response){

                          //that.setData(response.data);
                          console.log("ES EROOORR",response.data);
                          // that.initial_date = new Date(that.initial_date);
                          // that.closing_sale = new Date(that.closing_sale);

                          // angular.forEach(that.sessions,function(session){

                          //   session.date = new Date(session.date);
                          //   session.end_time   = new Date(session.end_time);
                          //   session.start_time = new Date(session.start_time);

                          // });

                          return $q.reject(response.data);
                        });

          },
          update : function(){

            var activity_id = this.activity;
            this.setToSave();
            console.log("updatinggggggggg",activity_id);
            var that = this;
            return $http.put('/api/activities/'+activity_id+'/calendar/',this)
                        .then(function(response){
                          that.setData(response.data);
                          return response.data
                        },
                        function(response){
                          return $q.reject(response.data);
                        });

          },
          setToSave: function(){

            var _initial_date = this.initial_date;

            var _closing_sale = this.closing_sale;

            this.initial_date = this.initial_date.valueOf();
            this.closing_sale = this.closing_sale.valueOf();
            angular.forEach(this.sessions,function(session){

              session.date = session.date.valueOf();
              session.end_time = session.end_time.valueOf();
              session.start_time = session.start_time.valueOf();

            });


          },
          changeStartDate: function(){

            var initial_date  = this.initial_date;
                //this.initial_date = initial_date.valueOf ? initial_date.valueOf() : initial_date;
                //this.initial_date = this.initial_date;

            if(this.initial_date>this.closing_sale)
              this.closing_sale = this.initial_date;



          },
          changeCloseDate: function(){

            var closing_sale = this.closing_sale;
                //this.closing_sale = closing_sale.valueOf ? closing_sale.valueOf() : closing_sale;

            if(this.initial_date>this.closing_sale)
              this.closing_sale = this.initial_date;
          },
          openCloseDate: function($event){
            $event.preventDefault();
            $event.stopPropagation();
            this.endOpened = true;
          },
          openStartDate: function($event){
            $event.preventDefault();
            $event.stopPropagation();
            this.startOpened = true;

          },
          openSessionDate: function($event,session){
            $event.preventDefault();
            $event.stopPropagation();
            session.openDate= true;             
          },
          changeSessionsN: function(){

            
            if (this.number_of_sessions>10)
              return;


            var difference = this.number_of_sessions - this.last_sn;
            var abs_difference = Math.abs(difference);

            console.log("difference",abs_difference);
            for (var i=0; i<abs_difference; i++){

                if (difference>0){

                  var index = this.number_of_sessions - 1
                  var date = index ? this.sessions[index-1].date : this.initial_date;

                  var start_time = new Date();
                      start_time.setHours( 6 );
                      start_time.setMinutes( 0 );
                  var end_time = new Date();
                      end_time.setHours( 12 );
                      end_time.setMinutes( 0 );

                  var session = {
                    openDate:false,
                    date:date,
                    minDate:date,
                    start_time:start_time,
                    end_time:end_time,
                  };
                  this.sessions.push(session);
                }
                else{
                  this.sessions.pop();
                }
            }

            this.last_sn = this.number_of_sessions;
            //return this.number_of_sessions

          },
          changeSessionDate: function($index,session){

            var size = this.sessions.length;
            var rest_sessions     = this.sessions.slice($index+1, $index+size);
            var previous_sessions = this.sessions.slice(0,$index);
            rest_sessions.map(function(value){

              value.date    = value.date<=session.date ? session.date : value.date;
              value.minDate  = session.date;


            });


            previous_sessions.map(function(value){


              value.maxDate = session.date;

            });

          },
          changeStartTime: function(session){



            var start_time = session.start_time.getHours();
            var end_time   = session.end_time.getHours();


            if(start_time > end_time){
              var new_end_time = new Date();
                  new_end_time.setHours(start_time+1);
              session.end_time = new_end_time;
            }

          },
          changeEndTime: function(session){

            var start_time = session.start_time.getHours();
            var end_time   = session.end_time.getHours();

            if(start_time > end_time){
              var new_start_time = new Date();
                  new_start_time.setHours(end_time-1);
              session.start_time = new_start_time;
            }

          }





          // create: function(){
          //   return $http.post('/api/activities/',this);
          // },
          // generalInfo: function() {
          //     var scope = this;
              
          //     var deferred = $q.defer();

          //     if (scope.presave_info){ 
               
          //       deferred.resolve(scope.presave_info);                
          //       return deferred.promise
          //     }
          //     else{

          //       return $http.get('/api/activities/info/').then(function(response){
          //         scope.presave_info = response.data;
          //         deferred.resolve(scope.presave_info);
          //         return deferred.promise
          //       });

          //     }

          //     //return deferred.promise;

          // },
          // load: function(id){
          //   var scope = this;

          //   return $http.get('/api/activities/'+id)
          //     .then(function(response) {
          //       scope.setData(response.data);
          //       return scope
          //     });
          // },
          // update: function() {
          //   return $http({
          //     method: 'put',
          //     url:'/api/activities/' + this.id,
          //     data: this,
          //     headers: { 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'},
          //   });
          // }
          //   //$http.put('/api/activities/' + this.id, this);
          // },
          // change_email: function() {
          //   return $http({
          //     method: 'post',
          //     url:'users/email/',
          //     data: {
          //       'email':this.user.email,
          //       'action_add':true,
          //     },
          //   });

          //   //$http.put('/api/activities/' + this.id, this);
          // },
          // change_password: function(password_data) {
          //   console.log(password_data);
          //   console.log('--------');
          //   return $http({
          //     method: 'post',
          //     url:'/users/password/change/',
          //     data: password_data,
          //   });

          //   //$http.put('/api/activities/' + this.id, this);
          // },
      };
      return Calendar;
  };



})();