document.addEventListener("DOMContentLoaded", () => {
  console.log("Profile.js loaded");
  
  // Get all steps and pages
  const steps = document.querySelectorAll(".step")
  const pages = document.querySelectorAll(".page")
  const nextButtons = document.querySelectorAll(".next-btn")
  const prevButtons = document.querySelectorAll(".prev-btn")
  const submitButton = document.querySelector(".submit-btn")

  // Function to navigate to a specific page
  function navigateToPage(pageNumber) {
    pages.forEach((page) => page.classList.remove("active"))
    document.getElementById(`page${pageNumber}`).classList.add("active")
    steps.forEach((step) => step.classList.remove("active"))
    steps[pageNumber - 1].classList.add("active")
  }

  steps.forEach((step) => {
    step.addEventListener("click", function () {
      const pageNumber = this.getAttribute("data-page")
      navigateToPage(pageNumber)
    })
  })

  nextButtons.forEach((button) => {
    button.addEventListener("click", function () {
      const nextPage = this.getAttribute("data-next")
      if (nextPage) navigateToPage(nextPage)
    })
  })

  prevButtons.forEach((button) => {
    button.addEventListener("click", function () {
      const prevPage = this.getAttribute("data-prev")
      if (prevPage) navigateToPage(prevPage)
    })
  })

  if (submitButton) {
    submitButton.addEventListener("click", () => {
      alert("Form submitted successfully!")
    })
  }

  const formInputs = document.querySelectorAll("input, select, textarea")
  formInputs.forEach((input) => {
    input.addEventListener("focus", function () {
      this.parentElement.classList.add("focused")
    })
    input.addEventListener("blur", function () {
      this.parentElement.classList.remove("focused")
    })
  })

  // Photo upload functionality
  const fileInput = document.querySelector("#profile-picture-input")
  const photoPlaceholder = document.querySelector("#profile-picture-img")
  const errorDiv = document.querySelector("#profile-picture-error")
  const uploadButton = document.querySelector(".upload-btn")
  const uploadForm = document.querySelector("#student-form")

  console.log("File input:", fileInput);
  console.log("Photo placeholder:", photoPlaceholder);
  console.log("Upload button:", uploadButton);

  if (fileInput && photoPlaceholder) {
    // Store original src for reset
    const originalSrc = photoPlaceholder.src
    console.log("Original src:", originalSrc);

    // Handle file selection and preview
    fileInput.addEventListener("change", function () {
      console.log("File input changed");
      const file = this.files[0]
      
      if (file) {
        console.log("File selected:", file.name, file.type, file.size);
        
        // Validate file type
        if (!file.type.match("image/jpeg|image/png|image/jpg")) {
          errorDiv.textContent = "Only PNG, JPG, or JPEG files are allowed."
          errorDiv.style.display = "block"
          photoPlaceholder.src = originalSrc
          fileInput.value = ""
          return
        }

        // Validate file size (5MB limit)
        if (file.size > 5 * 1024 * 1024) {
          errorDiv.textContent = "File size must be less than 5MB."
          errorDiv.style.display = "block"
          photoPlaceholder.src = originalSrc
          fileInput.value = ""
          return
        }

        // Clear any previous error
        errorDiv.textContent = ""
        errorDiv.style.display = "none"

        // Preview the selected image
        const reader = new FileReader()
        reader.onload = (e) => {
          console.log("File read successfully");
          photoPlaceholder.src = e.target.result
        }
        reader.readAsDataURL(file)
      } else {
        console.log("No file selected");
        photoPlaceholder.src = originalSrc
      }
    })
  }

  // Handle upload button click
  if (uploadButton) {
    uploadButton.addEventListener("click", (e) => {
      e.preventDefault()
      console.log("Upload button clicked");

      if (!fileInput.files.length) {
        errorDiv.textContent = "Please select a file to upload."
        errorDiv.style.display = "block"
        return
      }

      const file = fileInput.files[0]
      console.log("Uploading file:", file.name);

      // Create FormData for file upload
      const formData = new FormData()
      formData.append("profile_picture", file)

      // Add CSRF token
      const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value
      formData.append("csrfmiddlewaretoken", csrfToken)

      console.log("FormData created, sending request...");

      // Show loading state
      uploadButton.disabled = true
      uploadButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Uploading...'

      // Submit via fetch
      fetch(window.location.href, {
        method: "POST",
        body: formData,
      })
        .then((response) => {
          console.log("Response received:", response.status);
          if (response.ok) {
            console.log("Upload successful, reloading page...");
            window.location.reload()
          } else {
            throw new Error(`Upload failed with status: ${response.status}`)
          }
        })
        .catch((error) => {
          console.error("Upload error:", error)
          errorDiv.textContent = "Upload failed. Please try again."
          errorDiv.style.display = "block"
        })
        .finally(() => {
          // Reset button state
          uploadButton.disabled = false
          uploadButton.innerHTML = '<i class="fas fa-upload"></i> Upload Picture'
        })
    })
  }
})
