document.addEventListener('DOMContentLoaded', function() {
  // Get all steps and pages
  const steps = document.querySelectorAll('.step');
  const pages = document.querySelectorAll('.page');
  const nextButtons = document.querySelectorAll('.next-btn');
  const prevButtons = document.querySelectorAll('.prev-btn');
  const submitButton = document.querySelector('.submit-btn');

  // Function to navigate to a specific page
  function navigateToPage(pageNumber) {
    const targetPage = document.querySelector(`#page${pageNumber}`);

    if (!targetPage) {
      console.error(`Page ${pageNumber} is missing!`);
      alert(`Error: Page ${pageNumber} does not exist.`);
      return;
    }

    // Hide all pages
    pages.forEach(page => page.classList.remove('active'));

    // Show the selected page
    targetPage.classList.add('active');

    // Update step indicators
    steps.forEach(step => step.classList.remove('active'));

    steps[pageNumber - 1]?.classList.add('active'); // Use optional chaining to avoid errors
  }

  // Add click event to steps for navigation
  steps.forEach(step => {
    step.addEventListener('click', function() {
      const pageNumber = parseInt(this.getAttribute('data-page'), 10);
      navigateToPage(pageNumber);
    });
  });

  // Next button click event
  nextButtons.forEach(button => {
    button.addEventListener('click', function() {
      const nextPage = parseInt(this.getAttribute('data-next'), 10);
      if (nextPage) {
        navigateToPage(nextPage);
      }
    });
  });

  // Previous button click event
  prevButtons.forEach(button => {
    button.addEventListener('click', function() {
      const prevPage = parseInt(this.getAttribute('data-prev'), 10);
      if (prevPage) {
        navigateToPage(prevPage);
      }
    });
  });

  // Submit button click event
  if (submitButton) {
    submitButton.addEventListener('click', function() {
      alert('Form submitted successfully!');
      // Here you would typically send the form data to a server
    });
  }

  // Add animation to form fields when focused
  const formInputs = document.querySelectorAll('input, select, textarea');

  formInputs.forEach(input => {
    input.addEventListener('focus', function() {
      this.parentElement?.classList.add('focused');
    });

    input.addEventListener('blur', function() {
      this.parentElement?.classList.remove('focused');
    });
  });

  // Photo upload simulation
  const uploadBtn = document.querySelector('.upload-btn');
  const photoPlaceholder = document.querySelector('.photo-placeholder img');

  if (uploadBtn && photoPlaceholder) {
    uploadBtn.addEventListener('click', function() {
      alert('Photo upload functionality would be implemented here.');
    });
  }
});
