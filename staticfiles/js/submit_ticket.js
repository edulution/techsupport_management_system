var dashboardUrl = document.getElementById('dashboard-url').getAttribute('data-url');
$(document).ready(function() {
  // Disable submit button until form is valid
  $('form').on('input', function() {
    var form = this;
    var isValid = form.checkValidity();
    $('#submit-btn').prop('disabled', !isValid);
  });

  // Add validation styles to form fields
  $('form').on('submit', function(event) {
    if (!this.checkValidity()) {
      event.preventDefault();
      event.stopPropagation();
      $(this).addClass('was-validated');
    }
  });

  // Update subcategory options based on the selected category
  $('#id_category').on('change', function() {
    var categoryId = $(this).val();
    var subcategoryField = $('#id_subcategory');

    // Clear existing options
    subcategoryField.empty().append('<option value="" selected disabled>Subcategory</option>');

    if (categoryId) {
      // Fetch subcategories based on the selected category using AJAX
      $.ajax({
        url: '/get_subcategories/',
        data: {category_id: categoryId},
        success: function(data) {
          // Add fetched subcategories as options
          $.each(data.subcategories, function(index, subcategory) {
            subcategoryField.append('<option value="' + subcategory.id + '">' + subcategory.name + '</option>');
          });

          // Enable subcategory field
          subcategoryField.prop('disabled', false);
        },
        error: function() {
          console.log('Error occurred while fetching subcategories.');
        }
      });
    } else {
      // Disable subcategory field if no category is selected
      subcategoryField.prop('disabled', true);
    }
  });

  // Handle form submission using AJAX
  $("#submit-ticket-form").submit(function(event) {
    event.preventDefault();

    // Serialize form data
    var formData = $(this).serialize();

    // Get the CSRF token from the form
    var csrfToken = $("input[name='csrfmiddlewaretoken']").val();

    // Add the CSRF token to the form data
    formData += "&csrfmiddlewaretoken=" + encodeURIComponent(csrfToken);

    // Send AJAX request to the server
    $.ajax({
      type: "POST",
      url: '/create_ticket/',
      data: formData,
      success: function(response) {
        // Handle the success response
        alert("Ticket created successfully");
        window.location.href = dashboardUrl;
      },
      error: function(error) {
        // Handle the error response
        alert("Ticket creation failed");
      }
    });
  });
});
