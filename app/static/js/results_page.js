function changePage(newPage){
    var $pages = $(".page");

    $pages.each(function(){
        var $page = $(this);

        $page.addClass('is-hidden');
    });

    var $page = $(newPage);
    $page.removeClass('is-hidden')
}

function checkDevice(){
    var isMobile = /iPhone|iPod|Android/i.test(navigator.userAgent);
	var element = document.getElementById('text');
	if (isMobile) {
	    var $pages = $(".page");
	    $pages.each(function(){
	        var $page = $(this);
	        $page.removeClass('is-hidden')
	        $page.addClass('border-bottom')
	    })
	    var $sidenav = $(".sidenav");
	    $sidenav.addClass("is-hidden")
		}
    return isMobile
}

function drawResponseChart() {

    var data = new google.visualization.DataTable();

    data.addColumn('date','Date');
    data.addColumn('number',"Responses");
    response_rate_json.forEach(function(response){
        data.addRow([new Date(response[0].slice(6,10),response[0][4]-1,response[0].slice(0,2)),response[1]]);
    });

    var options = {
        chartArea:{
            width: '90%'
        },
        hAxis: {
            title: 'Day'
        },
        vAxis: {
        title: 'Responses'
        },
        legend:{
        position: "none"
        },
        width: '100%'
    };

    var chart = new google.visualization.LineChart(document.getElementById('chart_div'));
    chart.draw(data, options);

}


function drawResponseTable(){
    var data = new google.visualization.DataTable();
    data.addColumn('date','Date');
    data.addColumn('number','Responses');

    response_rate_json.forEach(function(response){
        data.addRow([new Date(response[0].slice(6,10),response[0][4]-1,response[0].slice(0,2)),response[1]]);
    });
    var options = {
        width:'100%',
        height: '100%'
    }

    var table = new google.visualization.Table(document.getElementById('response_table_div'))
    table.draw(data, options)
}


function drawRadioChart(title, answers, question_index){
    var data = new google.visualization.DataTable();
    data.addColumn('string', 'Answer')
    data.addColumn('number', 'Responses')

    answers.forEach(function (answer){
       data.addRow(answer)

    });

    var options = {
        title: title,
    }
    var table_options = {
        width:"75%",
    }

    var chart = new google.visualization.PieChart(document.getElementById('question-'+question_index))
    var table = new google.visualization.Table(document.getElementById('question_table-'+question_index))
    chart.draw(data, options);
    table.draw(data, table_options);
}

function drawCheckChart(title, answers, question_index){
    var data = new google.visualization.DataTable();
    data.addColumn('string', 'Answer')
    data.addColumn('number', 'Responses')

    answers.forEach(function(answer){
        data.addRow(answer)
    });

    var options = {
        title: title,
        legend:'none'
    }

    var table_options = {
        width:"75%",
    }

    var chart = new google.visualization.ColumnChart(document.getElementById('question-'+question_index))
    chart.draw(data, options)
    var table = new google.visualization.Table(document.getElementById('question_table-'+question_index))
    table.draw(data, table_options);

}

function drawSliderChart(title, answers, question_index){
    var data = new google.visualization.DataTable();

    data.addColumn('number','Value');
    data.addColumn('number',"Responses");
    answers.forEach(function(answer){
        data.addRow([parseInt(answer[0]),answer[1]]);
    });

    var options = {
        title:title,
        hAxis: {
            title: 'Value'
        },
        vAxis: {
            title: 'Responses'
        },
        legend:{
        position: "none"
        },
        width: '100%'
    };
    var table_options = {
        width:"75%",
    }

    var chart = new google.visualization.LineChart(document.getElementById('question-'+question_index));
    chart.draw(data, options);
    var table = new google.visualization.Table(document.getElementById('question_table-'+question_index))
    table.draw(data, table_options);

}

function drawResultCharts(){
    var question_index = 1;
    question_responses_json.forEach(function(question){
        var title = question[0];
        var type = question[1];
        var answers = question.slice(2);

        if (type === "radioField"){
            drawRadioChart(title, answers, question_index);
        }
        else if (type === "checkField"){
            drawCheckChart(title, answers, question_index);
        }
        else if( type === "sliderField"){
            drawSliderChart(title, answers, question_index);
        }
        question_index++;
    });
}


$(document).ready(function() {
    $('#pollHomeLink').on('click', function () {
        changePage('.pollHome');
    });

    $('#responseRateLink').on('click', function () {
        changePage('.responseRate');
    });

    $('#resultsLink').on('click', function () {
        changePage('.results');
    });

    var isMobile = checkDevice()
    console.log(isMobile)
    // Load the Visualization API and the corechart package.
    google.charts.load('current', {'packages': ['corechart', 'table']});
    // Set a callback to run when the Google Visualization API is loaded.
    if (response_rate_json !== "") {
        google.charts.setOnLoadCallback(function () {
            $(".responseRate").removeClass("is-hidden")
            $(".results").removeClass("is-hidden")
            drawResponseChart();
            drawResponseTable();
            drawResultCharts();
            if (isMobile === false) {
                $(".responseRate").addClass("is-hidden")
                $(".results").addClass("is-hidden")
            }
        });
    }
    // Used when page is resized to redraw charts. Have to remove and add classes due to google chart error (won't fill div area when it is hidden)
    $(window).resize(function() {
        if (response_rate_json !== "") {
            var $hidden_areas = $('.is-hidden')
            $hidden_areas.each(function(){
                $(this).removeClass('is-hidden')
            })
            drawResponseChart();
            drawResponseTable();
            drawResultCharts();
            $hidden_areas.each(function(){
                $(this).addClass('is-hidden')
            })

        }
    });

})