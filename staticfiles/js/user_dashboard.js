(function($) {
  $(document).ready(function() {
    // Handle widget click event using event delegation
    $(document).on('click', '.card', function(event) {
      event.preventDefault();
      var url = $(this).find('a').attr('href');
      updateTicketTable(url);
    });

    // Function to update ticket table with data from the provided URL
    function updateTicketTable(url) {
      $.ajax({
        url: url,
        type: 'GET',
        dataType: 'html',
        beforeSend: function() {
          // Show loading indicator or perform any visual feedback
        },
        success: function(data) {
          $('#ticket-table').html($(data).find('#ticket-table').html());
        },
        error: function(xhr, textStatus, errorThrown) {
          // Handle AJAX errors and provide feedback to the user
          console.log('Error: ' + errorThrown);
        },
        complete: function() {
        }
      });
    }
  });
})(jQuery);
