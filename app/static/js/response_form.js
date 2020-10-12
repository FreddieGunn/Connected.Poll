function validate(){
    var $questions = $('input').filter('[required]:visible');
    var checked_radio = 0
    var validated = true;

    $questions.each(function(){
        var $question = $(this);
        if($question.attr('type') === "text" && $question.val().trim() === "") {
            if (validated === true) {
                $("#error-container").append("<p class='error-type'>All text inputs must be complete</p>");
            }
            validated = false;
        }
        else if($question.attr('type') === "radio" && $question.is(':checked')){
               checked_radio++
        }
    });
    var $radios = $('.radio-group');
    var groups = $radios.length
    if (groups !== checked_radio){
        $("#error-container").append("<p class='error-type'>All radio fields must be complete</p>");
        validated = false;
    }
    return validated;
}

function deleteErrorMessages(){
    $("#error-container").find(".error-type").each(function(){
        var $error = $(this);
        $error.remove();
    });
}









$(document).ready(function() {

    $("#validateButton").click(function(){
        deleteErrorMessages();
        var valid_data = validate();
        if (valid_data){
            $('#confirmModal').modal('show');
        }
        else{
            $('#errorModal').modal('show');
        }
    });
});