// Ultra-optimized JavaScript for CPE Management Platform

document.addEventListener('DOMContentLoaded', function() {
    // Prevent double submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
                setTimeout(() => {
                    if (submitBtn) {
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = submitBtn.getAttribute('data-original') || 'Submit';
                    }
                }, 10000);
            }
        });
    });

    // Auto-hide alerts faster
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => setTimeout(() => alert.remove(), 3000));

    // Fast progress bars
    document.querySelectorAll('.progress-bar').forEach(bar => {
        const width = bar.style.width;
        bar.style.width = '0%';
        requestAnimationFrame(() => bar.style.width = width);
    });

    // Set today's date
    const dateInput = document.getElementById('activity_date');
    if (dateInput && !dateInput.value) {
        dateInput.value = new Date().toISOString().split('T')[0];
    }
});