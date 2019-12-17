angular.module('satellite_input', [])
.controller('MainCtrl', [
  '$scope','$http',
  function($scope,$http){
    $scope.eci = 'F4K53U92YdiuT3Wqe8pNsm';
    $scope.profile = {'sat_name': "", 'address': "",'email': ""};
  
    var sky_cloud = function(){
    return 'http://localhost:8080/sky/cloud/'+$scope.eci;
  };

      var sky_event = function(){
    return 'http://localhost:8080/sky/event/'+$scope.eci;
  };


    var aURL = sky_event()+'/1231/satellite/track_request';
    $scope.post_profile = function() {
      var bURL = aURL + "?sat_name=" + $scope.sat_name + "&address=" + $scope.address + "&email=" + $scope.email;
      return $http.post(bURL).success(function(data){
        $scope.sat_name='';
        $scope.address='';
        $scope.email='';
        $scope.get_profile_array();
      });
    };

  var eURL = sky_cloud()+'/satellite/tracking';
  $scope.get_profile_array = function() {
    return $http.get(eURL).success(function(data){
      angular.copy(data, $scope.profile);
    });
  };
  $scope.get_profile_array();


   }
]);