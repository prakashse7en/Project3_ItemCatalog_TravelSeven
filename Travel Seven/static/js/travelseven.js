$(document).ready(function(){
	$('#submit').click(function(){
		if(!($('#name').val().length > 0)){
			alert("City name is empty.");
			return false;
			}
		else if(!($('#description').val().length > 0)){
			alert("Description is empty.")
			return false;
		}
		else if(!($('#bestseason').val().length) >0 ){
			alert("Best Season is empty.")
			return false;
		}
		else{
			return true;
		}
	});
});