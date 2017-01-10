google.load("visualization", "1", {packages:["corechart"], 'language': 'en'});
(function($) {
    $(document).ready(function(){

        var $loading = $('#loading');

        $.getJSON("/api/v1/users", function(result) {
            var $dropdown = $("#user-id");

            $.each(result, function(item) {
               $dropdown.append($('<option />', {
                    'val': this.user_id,
                    'text': this.name
                }));
            });

            $dropdown.show();
            $loading.hide();

        });
        $('#user-id').change(function(){
            var selected_user = $("#user-id").val(),
                $chart_div = $('#chart-div'),
                $avatar = $("#avatar");

            if(selected_user) {

                $loading.show();
                $chart_div.hide();
                $avatar.hide();

                $.getJSON("/api/v1/presence_weekday/"+selected_user, function(result) {
                    if (result!=0){
                        var chart = new google.visualization.PieChart($chart_div[0]),
                            data = google.visualization.arrayToDataTable(result),
                            options = {};

                        $chart_div.show();
                        chart.draw(data, options);
                    }else{
                        $chart_div.show();
                        $chart_div.text("No data for this user.");
                    }
                    $loading.hide();

                    $.getJSON("/api/v1/users/"+selected_user, function(result) {
                        $avatar.attr("src", result).show();
                    });
                });
            }
        });
    });
})(jQuery);
