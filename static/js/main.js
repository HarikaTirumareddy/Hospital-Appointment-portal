/**
 * Hospital & Patient Appointment Management Portal - JavaScript ES6+
 * Features:
 * - Dynamic Doctor Filtering by Department and Search Query (Req #3)
 * - Real-Time Slot Checker and Double-Booking Prevention (Req #5 & #6)
 * - Auto-dismissing alerts
 * - Demo Login quick autofill
 */

document.addEventListener('DOMContentLoaded', () => {
    initDoctorFilter();
    initAppointmentSlotChecker();
    initDemoLoginAutofill();
    initAutoDismissAlerts();
    initDatePickerMinConstraint();
});

/**
 * 1. JavaScript Doctor Filtering & Instant Search (Requirement #3)
 */
function initDoctorFilter() {
    const filterContainer = document.getElementById('doctor-filter-container');
    if (!filterContainer) return;

    const departmentButtons = document.querySelectorAll('.dept-filter-btn');
    const searchInput = document.getElementById('doctor-search-input');
    const doctorCards = document.querySelectorAll('.doctor-item-col');
    const countDisplay = document.getElementById('doctor-count-display');
    const noResultsState = document.getElementById('no-doctors-found');
    const clearFilterBtn = document.getElementById('clear-filter-btn');

    let currentDept = 'all';
    let currentSearch = '';

    function applyFilter() {
        let visibleCount = 0;

        doctorCards.forEach(card => {
            const cardDept = card.getAttribute('data-department') || '';
            const cardName = (card.getAttribute('data-name') || '').toLowerCase();
            const cardSpecialty = (card.getAttribute('data-specialty') || '').toLowerCase();

            const matchesDept = (currentDept === 'all' || cardDept.toLowerCase() === currentDept.toLowerCase());
            const matchesSearch = !currentSearch || 
                cardName.includes(currentSearch) || 
                cardSpecialty.includes(currentSearch);

            if (matchesDept && matchesSearch) {
                card.style.display = 'block';
                card.classList.add('fade-in');
                visibleCount++;
            } else {
                card.style.display = 'none';
            }
        });

        if (countDisplay) {
            countDisplay.textContent = `Showing ${visibleCount} doctor${visibleCount === 1 ? '' : 's'}`;
        }

        if (noResultsState) {
            noResultsState.style.display = visibleCount === 0 ? 'block' : 'none';
        }
    }

    // Department button clicks
    departmentButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            departmentButtons.forEach(b => b.classList.remove('active', 'btn-primary'));
            departmentButtons.forEach(b => b.classList.add('btn-outline-secondary'));

            btn.classList.remove('btn-outline-secondary');
            btn.classList.add('active', 'btn-primary');

            currentDept = btn.getAttribute('data-dept-slug') || 'all';
            applyFilter();
        });
    });

    // Instant search input
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            currentSearch = e.target.value.trim().toLowerCase();
            applyFilter();
        });
    }

    // Clear filter button
    if (clearFilterBtn) {
        clearFilterBtn.addEventListener('click', () => {
            if (searchInput) searchInput.value = '';
            currentSearch = '';
            currentDept = 'all';
            departmentButtons.forEach(b => {
                if (b.getAttribute('data-dept-slug') === 'all') {
                    b.classList.add('active', 'btn-primary');
                    b.classList.remove('btn-outline-secondary');
                } else {
                    b.classList.remove('active', 'btn-primary');
                    b.classList.add('btn-outline-secondary');
                }
            });
            applyFilter();
        });
    }

    // Initial check from URL hash/query
    const urlParams = new URLSearchParams(window.location.search);
    const initialDept = urlParams.get('department');
    if (initialDept) {
        const matchingBtn = document.querySelector(`.dept-filter-btn[data-dept-slug="${initialDept}"]`);
        if (matchingBtn) {
            matchingBtn.click();
        }
    }
}

/**
 * 2. Real-Time Slot Checker and Double-Booking Prevention (Requirement #5 & #6)
 */
function initAppointmentSlotChecker() {
    const doctorSelect = document.getElementById('id_doctor');
    const dateInput = document.getElementById('id_appointment_date');
    const slotSelect = document.getElementById('id_time_slot');
    const slotFeedback = document.getElementById('slot-availability-feedback');

    if (!doctorSelect || !dateInput || !slotSelect) return;

    // Cache original option labels
    const originalOptionTexts = {};
    Array.from(slotSelect.options).forEach(opt => {
        if (opt.value) {
            originalOptionTexts[opt.value] = opt.text;
        }
    });

    const slotPills = document.querySelectorAll('.slot-pill');

    function syncPillsWithSelect(selectedVal) {
        slotPills.forEach(pill => {
            const val = pill.getAttribute('data-slot-val');
            if (val && val === selectedVal) {
                pill.classList.add('active');
            } else {
                pill.classList.remove('active');
            }
        });
    }

    slotPills.forEach(pill => {
        pill.addEventListener('click', (e) => {
            e.preventDefault();
            if (pill.disabled || pill.classList.contains('disabled')) return;
            const val = pill.getAttribute('data-slot-val');
            if (val) {
                slotSelect.value = val;
                syncPillsWithSelect(val);
            }
        });
    });

    slotSelect.addEventListener('change', () => {
        syncPillsWithSelect(slotSelect.value);
    });

    async function checkAvailability() {
        const doctorId = doctorSelect.value;
        const dateValue = dateInput.value;

        if (!doctorId || !dateValue) {
            if (slotFeedback) {
                slotFeedback.innerHTML = '<span class="text-muted"><i class="bi bi-info-circle me-1"></i>Select doctor and date to view available slots.</span>';
            }
            // Reset select options
            Array.from(slotSelect.options).forEach(opt => {
                opt.disabled = false;
                if (originalOptionTexts[opt.value]) {
                    opt.text = originalOptionTexts[opt.value];
                }
            });
            // Reset visual pills
            slotPills.forEach(pill => {
                pill.disabled = false;
                pill.classList.remove('disabled');
            });
            syncPillsWithSelect(slotSelect.value);
            return;
        }

        if (slotFeedback) {
            slotFeedback.innerHTML = '<span class="text-primary"><i class="bi bi-hourglass-split me-1"></i>Checking slot availability...</span>';
        }

        try {
            const response = await fetch(`/api/booked-slots/?doctor_id=${encodeURIComponent(doctorId)}&date=${encodeURIComponent(dateValue)}`);
            if (!response.ok) throw new Error('Network error');
            const data = await response.json();
            const bookedSlots = data.booked_slots || [];

            let availableCount = 0;
            let bookedCount = 0;

            // 1. Update Dropdown Options
            Array.from(slotSelect.options).forEach(opt => {
                if (!opt.value) return;

                const baseText = originalOptionTexts[opt.value] || opt.text;
                if (bookedSlots.includes(opt.value)) {
                    opt.disabled = true;
                    opt.text = `${baseText} ❌ [BOOKED]`;
                    bookedCount++;
                    // If the user already had this selected, reset it
                    if (slotSelect.value === opt.value) {
                        slotSelect.value = '';
                    }
                } else {
                    opt.disabled = false;
                    opt.text = `${baseText} ✅ [Available]`;
                    availableCount++;
                }
            });

            // 2. Update Interactive Slot Pills
            slotPills.forEach(pill => {
                const val = pill.getAttribute('data-slot-val');
                if (val && bookedSlots.includes(val)) {
                    pill.disabled = true;
                    pill.classList.add('disabled');
                    pill.classList.remove('active');
                    pill.title = 'Slot is already booked for this doctor.';
                } else if (val) {
                    pill.disabled = false;
                    pill.classList.remove('disabled');
                    pill.title = 'Click to select this slot';
                }
            });
            syncPillsWithSelect(slotSelect.value);

            if (slotFeedback) {
                if (availableCount === 0) {
                    slotFeedback.innerHTML = '<span class="text-danger fw-bold"><i class="bi bi-exclamation-triangle-fill me-1"></i>All slots booked for this doctor on this day. Please choose another date.</span>';
                } else if (bookedCount > 0) {
                    slotFeedback.innerHTML = `<span class="text-success"><i class="bi bi-check-circle-fill me-1"></i><strong>${availableCount}</strong> slots available (<strong>${bookedCount}</strong> already booked).</span>`;
                } else {
                    slotFeedback.innerHTML = `<span class="text-success"><i class="bi bi-check-circle-fill me-1"></i>All <strong>${availableCount}</strong> time slots are currently available!</span>`;
                }
            }
        } catch (err) {
            console.error('Error fetching booked slots:', err);
            if (slotFeedback) {
                slotFeedback.innerHTML = '<span class="text-warning"><i class="bi bi-exclamation-circle me-1"></i>Could not verify live slots. Server validation will confirm booking.</span>';
            }
        }
    }

    doctorSelect.addEventListener('change', checkAvailability);
    dateInput.addEventListener('change', checkAvailability);

    // Initial check if values are already populated
    if (doctorSelect.value && dateInput.value) {
        checkAvailability();
    }

}

/**
 * 3. Restrict Date Pickers to prevent selecting past dates (Req #6)
 */
function initDatePickerMinConstraint() {
    const dateInputs = document.querySelectorAll('input[type="date"]');
    const today = new Date().toISOString().split('T')[0];
    dateInputs.forEach(input => {
        if (!input.hasAttribute('min') && input.id !== 'id_date_of_birth') {
            input.setAttribute('min', today);
        }
    });
}

/**
 * 4. Demo Login Autofill Helpers for Project Review
 */
function initDemoLoginAutofill() {
    const btnPatient = document.getElementById('demo-fill-patient');
    const btnAdmin = document.getElementById('demo-fill-admin');
    const userInput = document.getElementById('id_username');
    const passInput = document.getElementById('id_password');

    if (btnPatient && userInput && passInput) {
        btnPatient.addEventListener('click', () => {
            userInput.value = 'john_patient';
            passInput.value = 'patientpassword123';
        });
    }

    if (btnAdmin && userInput && passInput) {
        btnAdmin.addEventListener('click', () => {
            userInput.value = 'admin';
            passInput.value = 'adminpassword123';
        });
    }
}

/**
 * 5. Auto dismiss bootstrap alerts after 5 seconds
 */
function initAutoDismissAlerts() {
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 6000);
    });
}
