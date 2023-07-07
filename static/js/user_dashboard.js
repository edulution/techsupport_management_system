
$(document).ready(function() {
    // Handle widget click event
    $('.card').on('click', function() {
      var url = $(this).find('a').attr('href');
      updateTicketTable(url);
    });

    // Function to update ticket table with data from the provided URL
    function updateTicketTable(url) {
      $.ajax({
        url: url,
        type: 'GET',
        dataType: 'html',
        success: function(data) {
          $('#ticket-table').html($(data).find('#ticket-table').html());
        },
        error: function(xhr, textStatus, errorThrown) {
          console.log('Error: ' + errorThrown);
        }
      });
    }
  });