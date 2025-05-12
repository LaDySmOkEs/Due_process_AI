// Main JavaScript for Due Process AI

// DOM Ready function
document.addEventListener('DOMContentLoaded', function() {
    // Initialize loading overlay
    initializeLoadingOverlay();
    
    // Initialize file upload handlers
    initializeFileUploads();
    
    // Initialize legal term search
    initializeLegalTermSearch();
});

// Loading overlay functions
function initializeLoadingOverlay() {
    // Create loading overlay if it doesn't exist
    if (!document.querySelector('.loading-overlay')) {
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        
        const progressContainer = document.createElement('div');
        progressContainer.className = 'upload-progress-container';
        
        const heading = document.createElement('h3');
        heading.textContent = 'Uploading...';
        
        const spinner = document.createElement('div');
        spinner.className = 'loading-spinner';
        
        const progressText = document.createElement('p');
        progressText.id = 'upload-progress-text';
        progressText.textContent = 'Processing your file...';
        
        const progressBarContainer = document.createElement('div');
        progressBarContainer.className = 'progress';
        
        const progressBar = document.createElement('div');
        progressBar.className = 'progress-bar';
        progressBar.id = 'upload-progress-bar';
        
        progressBarContainer.appendChild(progressBar);
        progressContainer.appendChild(heading);
        progressContainer.appendChild(spinner);
        progressContainer.appendChild(progressText);
        progressContainer.appendChild(progressBarContainer);
        overlay.appendChild(progressContainer);
        
        document.body.appendChild(overlay);
    }
}

function showLoadingOverlay(message = 'Processing your file...') {
    const overlay = document.querySelector('.loading-overlay');
    const progressText = document.getElementById('upload-progress-text');
    const progressBar = document.getElementById('upload-progress-bar');
    
    if (progressText) {
        progressText.textContent = message;
    }
    
    if (progressBar) {
        progressBar.style.width = '0%';
    }
    
    if (overlay) {
        overlay.classList.add('visible');
    }
}

function hideLoadingOverlay() {
    const overlay = document.querySelector('.loading-overlay');
    if (overlay) {
        overlay.classList.remove('visible');
    }
}

function updateProgressBar(percent) {
    const progressBar = document.getElementById('upload-progress-bar');
    if (progressBar) {
        progressBar.style.width = percent + '%';
    }
}

// File upload functions
function initializeFileUploads() {
    const evidenceForm = document.getElementById('evidence-form');
    if (evidenceForm) {
        evidenceForm.addEventListener('submit', function(e) {
            const fileInput = document.getElementById('file');
            const fileTypeRadio = document.querySelector('input[name="evidence_type"]:checked');
            
            // Only show loading for file uploads, not links
            if (fileTypeRadio && fileTypeRadio.value === 'file' && fileInput && fileInput.files.length > 0) {
                e.preventDefault();
                const file = fileInput.files[0];
                
                // Show the loading overlay
                showLoadingOverlay(`Uploading ${file.name}...`);
                
                // Simulate progress for large files (especially audio/video)
                simulateProgress();
                
                // Submit the form after a brief delay
                setTimeout(() => {
                    evidenceForm.submit();
                }, 500);
            }
        });
    }
}

function simulateProgress() {
    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 90) {
            progress = 90; // Cap at 90% for the simulation
            clearInterval(interval);
        }
        updateProgressBar(progress);
    }, 500);
    
    // Store the interval ID in case we need to clear it
    window.progressInterval = interval;
}

// Legal term search functions
function initializeLegalTermSearch() {
    const searchForm = document.getElementById('legal-term-search-form');
    const termSuggestions = document.querySelectorAll('.term-suggestion');
    
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const searchTerm = document.getElementById('search-term').value.trim();
            if (searchTerm) {
                showLoadingOverlay('Translating legal term...');
                fetchTermExplanation(searchTerm);
            }
        });
    }
    
    if (termSuggestions) {
        termSuggestions.forEach(suggestion => {
            suggestion.addEventListener('click', function() {
                const term = this.textContent.trim();
                document.getElementById('search-term').value = term;
                showLoadingOverlay('Translating legal term...');
                fetchTermExplanation(term);
            });
        });
    }
}

function fetchTermExplanation(term) {
    fetch(`/jargon/translate?term=${encodeURIComponent(term)}`)
        .then(response => response.json())
        .then(data => {
            hideLoadingOverlay();
            displayTermExplanation(data);
        })
        .catch(error => {
            console.error('Error fetching term explanation:', error);
            hideLoadingOverlay();
        });
}

function displayTermExplanation(data) {
    const resultContainer = document.getElementById('term-result');
    if (resultContainer && data.term) {
        resultContainer.innerHTML = `
            <div class="card mb-4 jargon-card">
                <div class="card-header bg-attorney-navy text-white">
                    <h5 class="mb-0">${data.term}</h5>
                </div>
                <div class="card-body">
                    <h6 class="text-muted">Definition:</h6>
                    <p>${data.definition}</p>
                    
                    <h6 class="text-muted">Plain Language:</h6>
                    <p>${data.plain_language}</p>
                    
                    <h6 class="text-muted">Fun Explanation:</h6>
                    <p>${data.fun_explanation}</p>
                </div>
            </div>
        `;
        resultContainer.scrollIntoView({ behavior: 'smooth' });
    }
}

// Generic utility functions
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}