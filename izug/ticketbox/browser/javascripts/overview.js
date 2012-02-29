jQuery(function($){
    $('.ticketbox-overview a').live('click', function(e){
        e.preventDefault();

        tabbedview.flush_params('filterid');
        tabbedview.flush_params('filtervalue');

        params = $.find_param($(this).attr('href'));
        tabbedview.param('filterid', params['filterid']);
        tabbedview.param('filtervalue', params['filtervalue']);
        tabbedview.reload_view();
    });

});
