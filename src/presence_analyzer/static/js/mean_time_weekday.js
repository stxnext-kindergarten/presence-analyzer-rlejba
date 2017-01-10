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

                $.getJSON("/api/v1/mean_time_weekday/"+selected_user, function(result) {
                    if (result!=0){
                        var chart = new google.visualization.ColumnChart($chart_div[0]),
                            data = new google.visualization.DataTable(),
                            formatter = new google.visualization.DateFormat({pattern: 'HH:mm:ss'});

                        $.each(result, function(index, value) {
                            value[1] = parseInterval(value[1]);
                        });

                        data.addColumn('string', 'Weekday');
                        data.addColumn('datetime', 'Mean time (h:m:s)');
                        data.addRows(result);
                        var options = {
                            hAxis: {title: 'Weekday'}
                        };

                        formatter.format(data, 1);
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
