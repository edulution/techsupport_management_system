$(document).ready(function() {
    $('.ticket-trend').on('click', function() {
        var category = $(this).data('category');
        $('.ticket-item').hide(); // Hide all ticket items
        $('.ticket-item[data-category="' + category + '"]').show(); // Show tickets of the clicked category
    });
});