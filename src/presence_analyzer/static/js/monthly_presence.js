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

                $.getJSON("/api/v1/monthly_presence/"+selected_user, function(result) {
                    var chart = new google.visualization.LineChart($chart_div[0]),
                        data = google.visualization.arrayToDataTable(result),
                        options = {
                            curveType: 'function',
                        };

                    $chart_div.show();
                    $loading.hide();
                    chart.draw(data, options);

                    $.getJSON("/api/v1/users/"+selected_user, function(result) {
                        $avatar.attr("src", result).show();
                    });
                });
            }    
        });
    });
})(jQuery);
