// Status button functionality
function setupStatusButtons() {
    const statusButtons = document.querySelectorAll('.status-btn');
    
    statusButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            // Remove active class from sibling buttons
            const siblings = e.target.parentElement.querySelectorAll('.status-btn');
            siblings.forEach(btn => btn.classList.remove('active'));
            
            // Add active class to clicked button
            button.classList.add('active');
        });
    });
  }
  
  // Leave form functionality
  function setupLeaveForm() {
    const form = document.querySelector('.leave-request-form');
    const halfDayOptions = document.querySelector('.half-day-options');
    const halfDayRadios = document.querySelectorAll('input[name="half-day-type"]');
    
    // Handle leave duration changes
    document.querySelectorAll('input[name="leave-duration"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            const isHalfDay = e.target.value === 'half';
            halfDayOptions.classList.toggle('active', isHalfDay);
            halfDayRadios.forEach(radio => {
                radio.disabled = !isHalfDay;
                if (!isHalfDay) radio.checked = false;
            });
            
            // Select first half by default when half day is selected
            if (isHalfDay) {
                halfDayRadios[0].checked = true;
            }
        });
    });
    
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        
        // Get form data
        const formData = {
            studentName: document.getElementById('student-name').value,
            reason: document.getElementById('leave-reason').value,
            startDate: document.getElementById('leave-start').value,
            endDate: document.getElementById('leave-end').value,
            duration: document.querySelector('input[name="leave-duration"]:checked').value,
            halfDayType: document.querySelector('input[name="half-day-type"]:checked')?.value
        };
        
        // Here you would typically send this data to a server
        console.log('Leave request submitted:', formData);
        
        // Reset form
        form.reset();
        halfDayOptions.classList.remove('active');
        halfDayRadios.forEach(radio => {
            radio.disabled = true;
            radio.checked = false;
        });
        alert('Leave request submitted successfully!');
    });
  }
  
  // Initialize all functionality
  document.addEventListener('DOMContentLoaded', () => {
    setupStatusButtons();
    setupLeaveForm();
  });