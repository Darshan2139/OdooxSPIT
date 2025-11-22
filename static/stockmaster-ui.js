// ===== StockMaster UI Scripts =====

document.addEventListener('DOMContentLoaded', function() {
  // Initialize all interactive features
  initNavigation();
  initViewToggle();
  initEditableStock();
  initQuantityValidation();
  initButtonStates();
  initSearchIcon();
  initProfileIcon();
});

// ===== Navigation =====
function initNavigation() {
  const navLinks = document.querySelectorAll('.nav-link');
  navLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      // Remove active class from all links
      navLinks.forEach(l => l.classList.remove('active'));
      // Add active class to clicked link
      this.classList.add('active');
    });
  });
}

// ===== View Toggle (List/Kanban) =====
function initViewToggle() {
  const listViewBtn = document.getElementById('listViewBtn');
  const kanbanViewBtn = document.getElementById('kanbanViewBtn');
  const listView = document.getElementById('listView');
  const kanbanView = document.getElementById('kanbanView');

  if (listViewBtn && kanbanViewBtn) {
    listViewBtn.addEventListener('click', function() {
      listViewBtn.classList.add('active');
      kanbanViewBtn.classList.remove('active');
      if (listView) listView.style.display = 'block';
      if (kanbanView) kanbanView.style.display = 'none';
    });

    kanbanViewBtn.addEventListener('click', function() {
      kanbanViewBtn.classList.add('active');
      listViewBtn.classList.remove('active');
      if (listView) listView.style.display = 'none';
      if (kanbanView) kanbanView.style.display = 'block';
    });
  }
}

// ===== Editable Stock =====
function initEditableStock() {
  const stockCells = document.querySelectorAll('[data-editable="stock"]');
  
  stockCells.forEach(cell => {
    cell.addEventListener('click', function() {
      if (this.querySelector('input')) return; // Already editing
      
      const currentValue = this.textContent.trim();
      const input = document.createElement('input');
      input.type = 'number';
      input.value = currentValue;
      input.className = 'form-control';
      input.style.width = '100%';
      
      this.textContent = '';
      this.appendChild(input);
      input.focus();
      
      function saveValue() {
        const newValue = input.value;
        cell.textContent = newValue || currentValue;
        // Trigger quantity validation if needed
        validateQuantityInRow(cell.closest('tr'));
      }
      
      input.addEventListener('blur', saveValue);
      input.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') saveValue();
      });
    });
  });
}

// ===== Quantity Validation (Highlight red if exceeds available) =====
function initQuantityValidation() {
  const quantityInputs = document.querySelectorAll('[data-validate="quantity"]');
  
  quantityInputs.forEach(input => {
    input.addEventListener('change', function() {
      validateQuantityInRow(this.closest('tr'));
    });
  });
}

function validateQuantityInRow(row) {
  if (!row) return;
  
  const quantityInput = row.querySelector('[data-validate="quantity"]');
  const availableCell = row.querySelector('[data-available]');
  
  if (quantityInput && availableCell) {
    const quantity = parseFloat(quantityInput.value) || 0;
    const available = parseFloat(availableCell.textContent) || 0;
    
    if (quantity > available) {
      row.classList.add('table-danger');
      row.style.backgroundColor = '#f8d7da';
    } else {
      row.classList.remove('table-danger');
      row.style.backgroundColor = '';
    }
  }
}

// ===== Button States (Visual feedback) =====
function initButtonStates() {
  const buttons = document.querySelectorAll('.btn');
  
  buttons.forEach(btn => {
    btn.addEventListener('mousedown', function() {
      this.style.transform = 'scale(0.98)';
    });
    
    btn.addEventListener('mouseup', function() {
      this.style.transform = 'scale(1)';
    });
    
    btn.addEventListener('mouseleave', function() {
      this.style.transform = 'scale(1)';
    });
  });
}

// ===== Utility: Toggle element visibility =====
function toggleElement(elementId) {
  const element = document.getElementById(elementId);
  if (element) {
    element.style.display = element.style.display === 'none' ? 'block' : 'none';
  }
}

// ===== Utility: Add product line (for receipts/deliveries) =====
function addProductLine(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;
  
  const firstLine = container.querySelector('.product-line');
  if (!firstLine) return;
  
  const newLine = firstLine.cloneNode(true);
  newLine.querySelectorAll('input, select').forEach(el => el.value = '');
  container.appendChild(newLine);
}

// ===== Utility: Remove product line =====
function removeProductLine(button) {
  const container = button.closest('.product-lines');
  const lines = container.querySelectorAll('.product-line');
  
  if (lines.length > 1) {
    button.closest('.product-line').remove();
  } else {
    alert('At least one product line is required');
  }
}

// ===== Utility: Format currency =====
function formatCurrency(value) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(value);
}

// ===== Utility: Format date =====
function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
}

// ===== Search Icon Handler =====
function initSearchIcon() {
  const searchIcons = document.querySelectorAll('[title="Search"]');
  searchIcons.forEach(icon => {
    icon.style.cursor = 'pointer';
    icon.addEventListener('click', function(e) {
      e.preventDefault();
      showSearchModal();
    });
  });
}

// ===== Search Modal =====
function showSearchModal() {
  // Create overlay
  const overlay = document.createElement('div');
  overlay.id = 'searchOverlay';
  overlay.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    z-index: 2000;
    display: flex;
    align-items: center;
    justify-content: center;
  `;
  
  // Create modal
  const modal = document.createElement('div');
  modal.style.cssText = `
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    width: 90%;
    max-width: 500px;
    padding: 2rem;
    z-index: 2001;
  `;
  
  modal.innerHTML = `
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
      <h3 style="color: #003366; font-weight: 600; margin: 0;">Search</h3>
      <button id="closeSearchModal" style="background: none; border: none; font-size: 1.5rem; color: #999; cursor: pointer;">×</button>
    </div>
    
    <div style="margin-bottom: 1.5rem;">
      <input type="text" id="searchInput" placeholder="Search products, receipts, deliveries..." 
             style="width: 100%; padding: 0.75rem 1rem; border: 1px solid #e0e0e0; border-radius: 8px; font-size: 1rem; box-sizing: border-box;">
    </div>
    
    <div style="display: flex; gap: 1rem;">
      <button id="searchBtn" class="btn btn-primary" style="flex: 1;">
        <i class="bi bi-search"></i> Search
      </button>
      <button id="cancelSearchBtn" class="btn btn-secondary" style="flex: 1;">Cancel</button>
    </div>
  `;
  
  overlay.appendChild(modal);
  document.body.appendChild(overlay);
  
  // Focus input
  const searchInput = document.getElementById('searchInput');
  searchInput.focus();
  
  // Handle search
  const searchBtn = document.getElementById('searchBtn');
  searchBtn.addEventListener('click', function() {
    const query = searchInput.value.trim();
    if (query) {
      performSearch(query);
      overlay.remove();
    }
  });
  
  // Handle enter key
  searchInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
      const query = searchInput.value.trim();
      if (query) {
        performSearch(query);
        overlay.remove();
      }
    }
  });
  
  // Handle close
  const closeBtn = document.getElementById('closeSearchModal');
  const cancelBtn = document.getElementById('cancelSearchBtn');
  
  closeBtn.addEventListener('click', function() {
    overlay.remove();
  });
  
  cancelBtn.addEventListener('click', function() {
    overlay.remove();
  });
  
  // Close on overlay click
  overlay.addEventListener('click', function(e) {
    if (e.target === overlay) {
      overlay.remove();
    }
  });
}

// ===== Perform Search =====
function performSearch(query) {
  const currentPage = window.location.pathname;
  
  if (currentPage.includes('/products')) {
    window.location.href = '/products?search=' + encodeURIComponent(query);
  } else if (currentPage.includes('/receipts')) {
    window.location.href = '/receipts?search=' + encodeURIComponent(query);
  } else if (currentPage.includes('/deliveries')) {
    window.location.href = '/deliveries?search=' + encodeURIComponent(query);
  } else if (currentPage.includes('/ledger')) {
    window.location.href = '/ledger?search=' + encodeURIComponent(query);
  } else if (currentPage.includes('/warehouses')) {
    window.location.href = '/warehouses?search=' + encodeURIComponent(query);
  } else {
    // Default: search products
    window.location.href = '/products?search=' + encodeURIComponent(query);
  }
}

// ===== Profile Icon Handler =====
function initProfileIcon() {
  const profileIcons = document.querySelectorAll('[title="User Menu"]');
  profileIcons.forEach(icon => {
    icon.style.cursor = 'pointer';
    icon.addEventListener('click', function(e) {
      e.preventDefault();
      // Show profile menu
      const profileMenu = document.createElement('div');
      profileMenu.style.cssText = `
        position: fixed;
        top: 60px;
        right: 20px;
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 1001;
        min-width: 200px;
      `;
      
      profileMenu.innerHTML = `
        <a href="/profile" style="display: block; padding: 12px 16px; color: #003366; text-decoration: none; border-bottom: 1px solid #e0e0e0; font-weight: 500;">
          <i class="bi bi-person"></i> My Profile
        </a>
        <a href="/profile/edit" style="display: block; padding: 12px 16px; color: #003366; text-decoration: none; border-bottom: 1px solid #e0e0e0; font-weight: 500;">
          <i class="bi bi-pencil"></i> Edit Profile
        </a>
        <a href="/profile/change-password" style="display: block; padding: 12px 16px; color: #003366; text-decoration: none; border-bottom: 1px solid #e0e0e0; font-weight: 500;">
          <i class="bi bi-key"></i> Change Password
        </a>
        <a href="/logout" style="display: block; padding: 12px 16px; color: #dc3545; text-decoration: none; font-weight: 500;">
          <i class="bi bi-box-arrow-right"></i> Logout
        </a>
      `;
      
      document.body.appendChild(profileMenu);
      
      // Close menu when clicking outside
      document.addEventListener('click', function closeMenu(e) {
        if (!profileMenu.contains(e.target) && !icon.contains(e.target)) {
          profileMenu.remove();
          document.removeEventListener('click', closeMenu);
        }
      });
    });
  });
}
