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

                $.getJSON("/api/v1/presence_start_end/"+selected_user, function(result) {
                    var chart = new google.visualization.Timeline($chart_div[0]),
                        formatter = new google.visualization.DateFormat({pattern: 'HH:mm:ss'}),
                        data = new google.visualization.DataTable();

                    $.each(result, function(index, value) {
                        value[1] = new Date(parseInterval(value[1]));
                        value[2] = new Date(parseInterval(value[2]));
                    });

                    data.addColumn('string', 'Weekday');
                    data.addColumn({ type: 'datetime', id: 'Start' });
                    data.addColumn({ type: 'datetime', id: 'End' });
                    data.addRows(result);
                    var options = {
                        hAxis: {title: 'Weekday'}
                    };

                    formatter.format(data, 1);
                    formatter.format(data, 2);

                    $chart_div.show();
                    $loading.hide();
                    chart.draw(data, options);
                });
                $.getJSON("/api/v1/users/"+selected_user, function(result) {

                    $avatar.attr("src", result).show();

                });
            }    
        });
    });
})(jQuery);
