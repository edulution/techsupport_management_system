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
  });