function adjustIndices(removedIndex) {
    var $forms = $('.subform');

    $forms.each(function(i) {
        var $form = $(this);
        var index = parseInt($form.data('index'));
        var newIndex = index - 1;

        if (index < removedIndex) {
            // Skip
            return true;
        }

        // Change ID in form itself
        $form.attr('id', $form.attr('id').replace(index, newIndex));
        $form.data('index', newIndex);
        $form.attr('data-index', $form.attr('data-index').replace(index, newIndex));

        // Change IDs in form inputs
        $form.find('input').each(function(j) {
            var $item = $(this);
            $item.attr('id', $item.attr('id').replace(index, newIndex));
            $item.attr('name', $item.attr('name').replace(index, newIndex));
        });

        $form.find('label').each(function(idx){
            var $item = $(this);
            $item.attr('for', $item.attr('for').replace(index,newIndex))
        });
        $form.find('div').each(function(idx){
            var $item = $(this);
            if ($item.hasClass('question-title-div') == false){
                $item.attr('id', $item.attr('id').replace(index, newIndex));
                $item.attr("data-index",$item.attr('data-index').replace(index, newIndex));
                $item.data('index', $item.data('index').replace(index,newIndex));
            }
        });

    });
}

function removeForm() {
    var forms = $('.subform');
    var $removedForm = $(this).closest('.subform');
    var removedIndex = parseInt($removedForm.data('index'));

    $removedForm.hide('slow', function(){
        $removedForm.remove();
    });

    // Update indices
    adjustIndices(removedIndex);
}


function addForm(questionType) {
    var $templateForm = $('#question-_-form');

    if (!$templateForm) {
        console.log('[ERROR] Cannot find template');
        return;
    }

    // Get Last index
    var $lastForm = $('.subform').last();

    var newIndex = 0;

    if ($lastForm.length > 0) {
        newIndex = parseInt($lastForm.data('index')) + 1;
    }

    // Add elements
    var $newForm = $templateForm.clone();

    $newForm.attr('id', $newForm.attr('id').replace('_', newIndex));
    $newForm.data('index', newIndex);
    $newForm.attr('data-index', $newForm.attr('data-index').replace('_', newIndex));

    $newForm.find('input').each(function(idx) {
        var $item = $(this);
        $item.attr('value', $item.attr('value').replace("_", questionType))
        $item.attr('id', $item.attr('id').replace('_', newIndex));
        $item.attr('name', $item.attr('name').replace('_', newIndex));
    });

    $newForm.find('label').each(function(idx){
        var $item = $(this);

         $item.attr('for', $item.attr('for').replace("_", newIndex));
    });

    $newForm.find('div').each(function(idx){
        var $item = $(this);
        if ($item.hasClass('question-title-div') === false){
            $item.attr('id', $item.attr('id').replace("_", newIndex));
            $item.attr("data-index",$item.attr('data-index').replace('_', newIndex))
            $item.addClass('subsubform');
        }
    });

    if (questionType === "checkField"){
        $newForm.find(".question-type-label").each(function(){
            var text = $(this).text();
            $(this).text(text.replace("Single-choice Question", "Multi-choice Question"));
        });
    }

    // Append
    $('#subforms-container').append($newForm);
    $newForm.addClass('subform');
    $newForm.removeClass('is-hidden');

    $newForm.find('.remove').click(removeForm);
    $('body, html').animate({ scrollTop: $newForm.offset().top}, 1000)

}
function deleteErrorMessages(){
    $("#error-container").find(".error-type").each(function(){
        var $error = $(this);
        $error.remove();
    });
}

function nextForm(){
    if ($("#title").val().trim() === ""){
        $( "#error-container" ).append( "<p class='error-type'>You must give your survey a title</p>" );
        $('#errorModal').modal('show');
        return false;
    }

    var $firstForm = $('#firstForm');
    $firstForm.addClass('is-hidden');

    var $nextForm = $('#nextForm');
    $nextForm.removeClass('is-hidden');

}

function backForm(){
    var $currentForm = $('#nextForm');
    $currentForm.addClass('is-hidden');

    var $firstForm = $('#firstForm');
    $firstForm.removeClass('is-hidden');

}

function updateAnswerIndices(removedIndex){
    var $answers = $('.subsubform');
    removedIndex[1] = parseInt(removedIndex[1]);

    $answers.each(function(i){

        var $answer = $(this);
        var index = $answer.data("index").split("/");
        var newIndex = index.slice();
        newIndex[1] = newIndex[1]-1;


        if (newIndex[0] == removedIndex[0]){
            if (newIndex[1] < removedIndex[1]){
                return true;
            }
            $answer.attr('id', $answer.attr('id').replace("question-"+index[0]+"-form-"+index[1], "question-"+newIndex[0]+"-form-"+newIndex[1]));


            $answer.find('input').each(function(j) {
                var $item = $(this);
                $item.attr('id', $item.attr('id').replace("questionList-"+index[0]+"-answerList-"+index[1]+"-answer", "questionList-"+newIndex[0]+"-answerList-"+newIndex[1]+"-answer"));
                $item.attr('name', $item.attr('name').replace("questionList-"+index[0]+"-answerList-"+index[1]+"-answer", "questionList-"+newIndex[0]+"-answerList-"+newIndex[1]+"-answer"));
            });

            $answer.find('label').each(function(idx){
                var $item = $(this);
                $item.attr('for', $item.attr('for').replace("questionList-"+index[0]+"-answerList-"+index[1]+"-answer", "questionList-"+newIndex[0]+"-answerList-"+newIndex[1]+"-answer"))
            });

            newIndex = newIndex.join("/");
            index = index.join("/")
            $answer.data('index', newIndex);
            $answer.attr('data-index', $answer.attr('data-index').replace(index, newIndex));
        }
    });
}

function checkDevice(){
    var isMobile = /iPhone|iPod|Android/i.test(navigator.userAgent);
	var element = document.getElementById('text');
	if (isMobile) {
	    var $form = $("label");
	    $form.each(function(){
	        var $field = $(this);
	        $field.removeClass('text-right')
	        $field.addClass('text-left')
	    });
	}
}

function addTextForm(){
    var $templateForm = $('#question-_-form-text');

    if (!$templateForm) {
        console.log('[ERROR] Cannot find template');
        return;
    }

    // Get Last index
    var $lastForm = $('.subform').last();

    var newIndex = 0;

    if ($lastForm.length > 0) {
        newIndex = parseInt($lastForm.data('index')) + 1;
    }

    // Add elements
    var $newForm = $templateForm.clone();

    $newForm.attr('id', $newForm.attr('id').replace('question-_-form-text','question-'+newIndex+"-form"));
    $newForm.data('index', newIndex);
    $newForm.attr('data-index', $newForm.attr('data-index').replace('_', newIndex));

    $newForm.find('input').each(function(idx) {
        var $item = $(this);
        $item.attr('id', $item.attr('id').replace('__', newIndex));
        $item.attr('name', $item.attr('name').replace('_', newIndex));
    });

    // Append
    $('#subforms-container').append($newForm);
    $newForm.addClass('subform');
    $newForm.removeClass('is-hidden');

    $newForm.find('.remove').click(removeForm);
    $('body, html').animate({ scrollTop: $newForm.offset().top}, 1000)

}


function addSliderForm(){
    var $templateForm = $('#question-_-form-slider');

    if (!$templateForm) {
        console.log('[ERROR] Cannot find template');
        return;
    }

    // Get Last index
    var $lastForm = $('.subform').last();

    var newIndex = 0;

    if ($lastForm.length > 0) {
        newIndex = parseInt($lastForm.data('index')) + 1;
    }

    // Add elements
    var $newForm = $templateForm.clone();

    $newForm.attr('id', $newForm.attr('id').replace('question-_-form-slider','question-'+newIndex+"-form"));
    $newForm.data('index', newIndex);
    $newForm.attr('data-index', $newForm.attr('data-index').replace('_', newIndex));

    $newForm.find('input').each(function(idx) {
        var $item = $(this);
        $item.attr('id', $item.attr('id').replace('___', newIndex));
        $item.attr('name', $item.attr('name').replace('_', newIndex));
    });

    $newForm.find('div').each(function(idx){
        var $item = $(this);
        if ($item.hasClass('question-title-div') == false){
            $item.attr('id', $item.attr('id').replace("___", newIndex));
            $item.attr("data-index",$item.attr('data-index').replace('_', newIndex))
            $item.addClass('subsubform');
        }
    });
    // Append
    $('#subforms-container').append($newForm);
    $newForm.addClass('subform');
    $newForm.removeClass('is-hidden');

    $newForm.find('.remove').click(removeForm);
    $('body, html').animate({ scrollTop: $newForm.offset().top}, 1000)
}

function validateData(){
    var validated = true
    var $lastForm = $('.subform').last();
    if ($lastForm.length == 0){
        $( "#error-container" ).append( "<p class='error-type'>You must provide at least one question</p>" );
        validated = false;
    }
    var $questions = $('.subform');
    $questions.each(function(){
        var $form = $(this);
        $form.find('input').each(function(j) {
            if ($(this).val().trim()=== "" && $(this).hasClass('label-input') == false){
                $( "#error-container" ).append( "<p class='error-type'>You must complete all inputs</p>" );
                validated = false;
                return false;
            }
        });
        if(validated == false){
            return false;
        }
    });


    return validated;
}



$(document).ready(function() {
    checkDevice();

    $('#addRadio').click(function(){
        addForm("radioField");
        $('#questionModal').modal('hide');
    });
    $('#addCheck').click(function(){
        addForm("checkField");
        $('#questionModal').modal('hide');
    });
    $('#addText').click(function(){
        $("#questionModal").modal('hide');
        addTextForm();
    });
    $('#addSlider').click(function(){
        $('#questionModal').modal('hide');
        addSliderForm();

    });

    $('#validateButton').click(function(){
        deleteErrorMessages()
        var validateResult = validateData()
        if (validateResult == true){
            $('#confirmModal').modal('show');
        }
        else{
            $('#errorModal').modal('show');
        }
    });


    $('.remove').click(removeForm);
    $('#next').click(function(){
        deleteErrorMessages()
        nextForm()
    });
    $('#back').click(backForm);

    $("body").on("click",".removeAnswer",function(){

        var $answers = $(this).closest('.subform');
        var id = $answers.children().last().prev().data('index').split('/');
        if (id[1] == 1){
            return true;
        }

        var $removedAnswer = $(this).closest('.subsubform');
        var removedIndex = $removedAnswer.attr('data-index').split("/");

        $removedAnswer.hide('slow', function(){
            $removedAnswer.remove();
        });

        // Update indices
        updateAnswerIndices(removedIndex);
    });

    $("body").on("click",".addAnswer", function(){
        var $templateForm = $('#question-_-form-_');
        if (!$templateForm) {
            console.log('[ERROR] Cannot find template');
            return;
        }

        var $answers = $(this).closest('.subform');
        var lastId = $answers.children().last().prev().data('index').split('/');
        var newId = lastId.slice();
        newId[1] = parseInt(newId[1]) + 1;


        var $newForm = $templateForm.clone();

        $newForm.attr('id', $newForm.attr('id').replace('question-_-form-_', 'question-'+newId[0]+'-form-'+newId[1]));

        $newForm.find('input').each(function(idx) {
            var $item = $(this);

            $item.attr('id', $item.attr('id').replace('questionList-_-answerList-_-answer','questionList-'+newId[0]+'-answerList-'+newId[1]+'-answer'));
            $item.attr('name', $item.attr('name').replace('questionList-_-answerList-_-answer', 'questionList-'+newId[0]+'-answerList-'+newId[1]+'-answer'));
        });

        $newForm.find('label').each(function(idx){
            var $item = $(this);

             $item.attr('for', $item.attr('for').replace("questionList-_-answerList-_-answer", 'questionList-'+newId[0]+'-answerList-'+newId[1]+'-answer'));
        });

        newId = newId.join("/");
        $newForm.data('index', newId);
        $newForm.attr('data-index', $newForm.attr('data-index').replace('_/_', newId));


        // Append
        $newForm.removeClass('is-hidden')
        $newForm.addClass('subsubform');
        $newForm.insertAfter('#question-'+lastId[0]+'-form-'+lastId[1]);
    });
});