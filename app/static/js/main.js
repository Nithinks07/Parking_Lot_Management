// Main JavaScript file for Parking Management System

// AJAX functions for API calls
async function fetchCustomerHistory(customerId) {
    try {
        const response = await fetch(`/api/customer_history/${customerId}`);
        if (!response.ok) {
            throw new Error('Failed to fetch customer history');
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching customer history:', error);
        throw error;
    }
}

// Utility function to format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-PH', {
        style: 'currency',
        currency: 'PHP'
    }).format(amount);
}

// Utility function to format duration
function formatDuration(minutes) {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}h ${mins}m`;
}

// Customer History Modal Functions
let currentCustomerId = null;

function showCustomerHistory(customerId) {
    currentCustomerId = customerId;
    const modal = document.getElementById('customerHistoryModal');
    const content = document.getElementById('customerHistoryContent');
    
    if (!modal || !content) {
        console.error('Customer history modal elements not found');
        return;
    }
    
    // Show loading state
    content.innerHTML = `
        <div class="text-center py-8">
            <i class="fas fa-spinner fa-spin text-blue-500 text-3xl mb-3"></i>
            <p class="text-gray-600">Loading customer history...</p>
        </div>
    `;
    
    modal.classList.remove('hidden');
    
    // Fetch customer history
    fetchCustomerHistory(customerId)
        .then(data => {
            if (data.length > 0) {
                content.innerHTML = `
                    <div class="overflow-x-auto">
                        <table class="min-w-full divide-y divide-gray-200">
                            <thead class="bg-gray-50">
                                <tr>
                                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Customer</th>
                                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">License Plate</th>
                                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Entry Time</th>
                                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Exit Time</th>
                                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Duration</th>
                                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Fee</th>
                                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Method</th>
                                </tr>
                            </thead>
                            <tbody class="bg-white divide-y divide-gray-200">
                                ${data.map(record => `
                                    <tr class="hover:bg-gray-50">
                                        <td class="px-4 py-3 text-sm text-gray-900">${escapeHtml(record.CustomerName)}</td>
                                        <td class="px-4 py-3 text-sm text-gray-600 font-mono">${escapeHtml(record.LicensePlate)}</td>
                                        <td class="px-4 py-3 text-sm text-gray-500">${formatDateTime(record.EntryTime)}</td>
                                        <td class="px-4 py-3 text-sm text-gray-500">
                                            ${record.ExitTime ? formatDateTime(record.ExitTime) : '<span class="text-green-600 font-semibold">Active</span>'}
                                        </td>
                                        <td class="px-4 py-3 text-sm text-gray-600">${formatDuration(record.DurationMinutes)}</td>
                                        <td class="px-4 py-3 text-sm font-medium text-gray-900">${formatCurrency(record.FeePaid)}</td>
                                        <td class="px-4 py-3 text-sm text-gray-600">
                                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium 
                                                ${record.Method === 'Cash' ? 'bg-green-100 text-green-800' : 
                                                  record.Method === 'Card' ? 'bg-blue-100 text-blue-800' : 
                                                  'bg-purple-100 text-purple-800'}">
                                                ${escapeHtml(record.Method)}
                                            </span>
                                        </td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                `;
            } else {
                content.innerHTML = `
                    <div class="text-center py-8">
                        <i class="fas fa-inbox text-gray-400 text-5xl mb-4"></i>
                        <p class="text-gray-600 text-lg">No history found for this customer.</p>
                    </div>
                `;
            }
        })
        .catch(error => {
            content.innerHTML = `
                <div class="text-center py-8">
                    <i class="fas fa-exclamation-triangle text-red-500 text-5xl mb-4"></i>
                    <p class="text-red-600 text-lg font-semibold">Error loading customer history</p>
                    <p class="text-sm text-gray-500 mt-2">${escapeHtml(error.message)}</p>
                </div>
            `;
        });
}

function closeCustomerHistory() {
    const modal = document.getElementById('customerHistoryModal');
    if (modal) {
        modal.classList.add('hidden');
    }
    currentCustomerId = null;
}

// Utility function to escape HTML
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return String(text).replace(/[&<>"']/g, m => map[m]);
}

// Utility function to format date and time
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-PH', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Initialize event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Close modal when clicking outside
    const modal = document.getElementById('customerHistoryModal');
    if (modal) {
        modal.addEventListener('click', function(event) {
            if (event.target === modal) {
                closeCustomerHistory();
            }
        });
    }
    
    // Close modal with Escape key
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            closeCustomerHistory();
        }
    });
    
    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => message.remove(), 300);
        }, 5000);
    });
});

// Export functions for use in other scripts if needed
window.parkingManagement = {
    fetchCustomerHistory,
    showCustomerHistory,
    closeCustomerHistory,
    formatCurrency,
    formatDuration,
    formatDateTime,
    escapeHtml
};

// ----------------------------------------------------
// Edit Service Modal Functions
// ----------------------------------------------------
const editServiceModal = document.getElementById('editServiceModal');
const editServiceForm = document.getElementById('editServiceForm');

function closeEditServiceModal() {
    if (editServiceModal) {
        editServiceModal.classList.add('hidden');
    }
}

async function openEditServiceModal(serviceId) {
    if (!editServiceModal || !editServiceForm) {
        console.error('Edit service modal elements not found');
        return;
    }

    try {
        // Fetch service data from the new API
        const response = await fetch(`/api/service/${serviceId}`);
        if (!response.ok) {
            throw new Error('Failed to fetch service data');
        }
        const service = await response.json();

        // Populate the form fields
        document.getElementById('edit_service_id').value = service.ServiceID;
        document.getElementById('edit_service_name').value = service.Name;
        document.getElementById('edit_service_description').value = service.Description;
        document.getElementById('edit_service_cost').value = service.Cost;

        // Show the modal
        editServiceModal.classList.remove('hidden');

    } catch (error) {
        console.error('Error opening edit modal:', error);
        alert('Could not load service data. ' + error.message);
    }
}

// Add keydown listener for Escape key to close the new modal
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeEditServiceModal();
    }
});


// Add this code to the end of main.js

// ----------------------------------------------------
// Edit Customer Modal Functions
// ----------------------------------------------------
// ----------------------------------------------------
// Edit Customer Modal Functions (Corrected)
// ----------------------------------------------------
const editCustomerModal = document.getElementById('editCustomerModal');
const editCustomerForm = document.getElementById('editCustomerForm');

function closeEditCustomerModal() {
    if (editCustomerModal) {
        editCustomerModal.classList.add('hidden');
    }
}

async function openEditCustomerModal(customerId) {
    if (!editCustomerModal || !editCustomerForm) {
        console.error('Edit customer modal elements not found');
        return;
    }

    try {
        const response = await fetch(`/api/customer/${customerId}`);
        if (!response.ok) {
            throw new Error('Failed to fetch customer data');
        }

        const customer = await response.json();

        // ✅ Populate fields using correct IDs from reports.html
        document.getElementById('editCustomerID').value = customer.CustomerID;
        document.getElementById('editCustomerName').value = customer.Name || '';
        document.getElementById('editCustomerPhone').value = customer.Phone || '';
        document.getElementById('editCustomerEmail').value = customer.Email || '';

        // Show the modal
        editCustomerModal.classList.remove('hidden');

    } catch (error) {
        console.error('Error opening edit modal:', error);
        alert('Could not load customer data. ' + error.message);
    }
}

// Add keydown listener for Escape key to close the modal
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeEditCustomerModal();
    }
});



// Add this code to the end of main.js

// ----------------------------------------------------
// Edit Lot Modal Functions
// ----------------------------------------------------
const editLotModal = document.getElementById('editLotModal');
const editLotForm = document.getElementById('editLotForm');

function closeEditLotModal() {
    if (editLotModal) {
        editLotModal.classList.add('hidden');
    }
}

async function openEditLotModal(lotId) {
    if (!editLotModal || !editLotForm) {
        console.error('Edit lot modal elements not found');
        return;
    }

    try {
        const response = await fetch(`/api/lot/${lotId}`);
        if (!response.ok) {
            throw new Error('Failed to fetch lot data');
        }
        const lot = await response.json();

        // Populate the form fields
        document.getElementById('edit_lot_id').value = lot.Lot_ID;
        document.getElementById('edit_name').value = lot.Name;
        document.getElementById('edit_total_spaces').value = lot.Total_spaces;
        document.getElementById('edit_address').value = lot.Address;

        editLotModal.classList.remove('hidden');

    } catch (error) {
        console.error('Error opening edit modal:', error);
        alert('Could not load lot data. ' + error.message);
    }
}

// Add keydown listener for Escape key to close the new modal
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeEditLotModal();
    }
});