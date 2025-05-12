/**
 * Due Process AI - Case Timeline Visualization
 * Helps identify procedural violations and speedy trial issues
 */

// Initialize the timeline visualization
function initializeTimeline(containerId, timelineData) {
    // Clear any existing content
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = '';
    
    // Create the timeline container
    const timelineContainer = document.createElement('div');
    timelineContainer.className = 'dp-timeline-container';
    
    // Create the timeline header with legend
    const legendContainer = document.createElement('div');
    legendContainer.className = 'timeline-legend';
    legendContainer.innerHTML = `
        <div class="legend-item">
            <span class="legend-marker marker-regular"></span>
            <span>Regular Event</span>
        </div>
        <div class="legend-item">
            <span class="legend-marker marker-critical"></span>
            <span>Critical Deadline</span>
        </div>
        <div class="legend-item">
            <span class="legend-marker marker-violation"></span>
            <span>Potential Violation</span>
        </div>
    `;
    
    // Create timeline scale
    const timelineScale = document.createElement('div');
    timelineScale.className = 'timeline-scale';
    
    // Create timeline events container
    const timelineEvents = document.createElement('div');
    timelineEvents.className = 'timeline-events';
    
    // Append components to container
    timelineContainer.appendChild(legendContainer);
    timelineContainer.appendChild(timelineScale);
    timelineContainer.appendChild(timelineEvents);
    container.appendChild(timelineContainer);
    
    // Process and visualize the data if available
    if (timelineData && timelineData.events && timelineData.events.length > 0) {
        visualizeTimeline(timelineScale, timelineEvents, timelineData);
    } else {
        // Display placeholder if no data
        timelineEvents.innerHTML = '<div class="timeline-placeholder">No timeline data available. Add case events to see your timeline.</div>';
    }
    
    // Add the speedy trial analysis button if we have events
    if (timelineData && timelineData.events && timelineData.events.length > 0) {
        const analysisBtn = document.createElement('button');
        analysisBtn.className = 'btn btn-primary mt-3';
        analysisBtn.textContent = 'Analyze Speedy Trial Rights';
        analysisBtn.onclick = function() {
            analyzeSpeedyTrialRights(timelineData);
        };
        container.appendChild(analysisBtn);
    }
}

// Visualize the timeline based on data
function visualizeTimeline(scaleContainer, eventsContainer, timelineData) {
    // Sort events by date
    timelineData.events.sort((a, b) => new Date(a.date) - new Date(b.date));
    
    // Calculate timeline range
    const firstDate = new Date(timelineData.events[0].date);
    const lastDate = new Date(timelineData.events[timelineData.events.length - 1].date);
    
    // Add some buffer
    firstDate.setDate(firstDate.getDate() - 7);
    lastDate.setDate(lastDate.getDate() + 7);
    
    const totalDays = Math.ceil((lastDate - firstDate) / (1000 * 60 * 60 * 24));
    
    // Create scale markers
    const scaleMarkers = [];
    let currentDate = new Date(firstDate);
    
    // Create monthly scale markers
    while (currentDate <= lastDate) {
        const marker = document.createElement('div');
        marker.className = 'scale-marker';
        
        const label = document.createElement('span');
        label.className = 'scale-label';
        label.textContent = currentDate.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
        
        marker.appendChild(label);
        scaleContainer.appendChild(marker);
        
        // Move to next month
        currentDate.setMonth(currentDate.getMonth() + 1);
    }
    
    // Position based on relative days from start
    timelineData.events.forEach(event => {
        const eventDate = new Date(event.date);
        const daysFromStart = Math.ceil((eventDate - firstDate) / (1000 * 60 * 60 * 24));
        const position = (daysFromStart / totalDays) * 100;
        
        // Create event marker
        const eventMarker = document.createElement('div');
        eventMarker.className = `event-marker ${event.type}-event`;
        eventMarker.style.left = `${position}%`;
        
        // Create event details
        const eventDetails = document.createElement('div');
        eventDetails.className = 'event-details';
        eventDetails.innerHTML = `
            <h6>${event.title}</h6>
            <p class="event-date">${new Date(event.date).toLocaleDateString()}</p>
            <p>${event.description}</p>
        `;
        
        // Add violation warning if applicable
        if (event.violation) {
            const violationWarning = document.createElement('div');
            violationWarning.className = 'violation-warning';
            violationWarning.innerHTML = `
                <i class="fas fa-exclamation-triangle"></i>
                <span>${event.violation}</span>
            `;
            eventDetails.appendChild(violationWarning);
        }
        
        eventMarker.appendChild(eventDetails);
        eventsContainer.appendChild(eventMarker);
        
        // Add event listeners
        eventMarker.addEventListener('mouseenter', function() {
            this.classList.add('active');
        });
        
        eventMarker.addEventListener('mouseleave', function() {
            this.classList.remove('active');
        });
    });
}

// Analyze speedy trial rights based on timeline data
function analyzeSpeedyTrialRights(timelineData) {
    // Sort events by date
    const events = [...timelineData.events].sort((a, b) => new Date(a.date) - new Date(b.date));
    
    // Get arrest and current date
    const arrestEvent = events.find(event => event.type === 'arrest' || event.title.toLowerCase().includes('arrest'));
    const currentDate = new Date();
    
    if (!arrestEvent) {
        showAnalysisResults('No arrest date found in timeline. Add your arrest date to analyze speedy trial rights.');
        return;
    }
    
    const arrestDate = new Date(arrestEvent.date);
    const daysSinceArrest = Math.ceil((currentDate - arrestDate) / (1000 * 60 * 60 * 24));
    
    // Check for arraignment
    const arraignmentEvent = events.find(event => 
        event.type === 'arraignment' || 
        event.title.toLowerCase().includes('arraignment') ||
        event.title.toLowerCase().includes('initial appearance')
    );
    
    // Check for preliminary hearing if applicable
    const preliminaryHearingEvent = events.find(event => 
        event.type === 'preliminary_hearing' || 
        event.title.toLowerCase().includes('preliminary hearing')
    );
    
    // Check for trial date
    const trialEvent = events.find(event => 
        event.type === 'trial' || 
        event.title.toLowerCase().includes('trial')
    );
    
    // Build analysis
    let analysis = `<h5>Speedy Trial Rights Analysis</h5>`;
    analysis += `<p>Days since arrest: <strong>${daysSinceArrest}</strong></p>`;
    
    // Check for federal rules violations
    if (timelineData.courtType === 'federal') {
        // Federal Speedy Trial Act - 70 days from indictment to trial
        const indictmentEvent = events.find(event => 
            event.type === 'indictment' || 
            event.title.toLowerCase().includes('indictment') ||
            event.title.toLowerCase().includes('information filed')
        );
        
        if (indictmentEvent) {
            const indictmentDate = new Date(indictmentEvent.date);
            const daysSinceIndictment = Math.ceil((currentDate - indictmentDate) / (1000 * 60 * 60 * 24));
            
            analysis += `<p>Days since indictment: <strong>${daysSinceIndictment}</strong></p>`;
            
            if (daysSinceIndictment > 70 && !trialEvent) {
                analysis += `<div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle"></i>
                    <strong>Federal Speedy Trial Act Violation Detected!</strong> 
                    The Speedy Trial Act requires trial to begin within 70 days of indictment or initial appearance, 
                    whichever is later. Your case has exceeded this threshold by ${daysSinceIndictment - 70} days.
                    <p class="mt-2"><strong>Recommended Action:</strong> File a Motion to Dismiss under 18 U.S.C. § 3162(a)(2) immediately.</p>
                </div>`;
            }
        }
    }
    else {
        // Generic state speedy trial analysis
        // Most states have speedy trial rules ranging from 60-180 days
        
        let stateViolation = false;
        let violationDays = 0;
        
        // Conservative estimate - 180 days without trial date is concerning in most jurisdictions
        if (daysSinceArrest > 180 && !trialEvent) {
            stateViolation = true;
            violationDays = daysSinceArrest - 180;
        }
        
        if (stateViolation) {
            analysis += `<div class="alert alert-warning">
                <i class="fas fa-exclamation-triangle"></i>
                <strong>Potential State Speedy Trial Violation Detected!</strong> 
                Your case has been pending for ${daysSinceArrest} days without a trial date.
                Many states require cases to be tried within 180 days of arrest or arraignment.
                <p class="mt-2"><strong>Recommended Action:</strong> Research the specific speedy trial rules for your state 
                and consider filing a Motion to Dismiss for speedy trial violations.</p>
            </div>`;
        }
    }
    
    // Constitutional analysis - Barker v. Wingo factors
    if (daysSinceArrest > 365) {
        analysis += `<div class="alert alert-danger">
            <i class="fas fa-gavel"></i>
            <strong>Constitutional Speedy Trial Concern Detected!</strong>
            Your case has been pending for over 1 year (${daysSinceArrest} days).
            Under <em>Barker v. Wingo</em>, 407 U.S. 514 (1972), courts analyze four factors:
            <ol>
                <li>Length of delay (over 1 year is presumptively prejudicial)</li>
                <li>Reason for the delay</li>
                <li>Defendant's assertion of the right</li>
                <li>Prejudice to the defendant</li>
            </ol>
            <p class="mt-2"><strong>Recommended Action:</strong> File a Motion to Dismiss for violation of 
            your Sixth Amendment right to a speedy trial, citing <em>Barker v. Wingo</em> and detailing any 
            prejudice you've suffered from the delay.</p>
        </div>`;
    }
    
    // Display the analysis
    showAnalysisResults(analysis);
}

// Show analysis results in modal
function showAnalysisResults(analysisHtml) {
    // Check if modal exists, create if not
    let modal = document.getElementById('speedyTrialModal');
    
    if (!modal) {
        modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = 'speedyTrialModal';
        modal.tabIndex = '-1';
        modal.setAttribute('role', 'dialog');
        modal.setAttribute('aria-labelledby', 'speedyTrialModalLabel');
        modal.setAttribute('aria-hidden', 'true');
        
        modal.innerHTML = `
            <div class="modal-dialog modal-lg" role="document">
                <div class="modal-content">
                    <div class="modal-header bg-primary text-white">
                        <h5 class="modal-title" id="speedyTrialModalLabel">Speedy Trial Rights Analysis</h5>
                        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                    <div class="modal-body" id="speedyTrialAnalysisContent">
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
                        <button type="button" class="btn btn-primary" id="saveAnalysisBtn">Save Analysis</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Add event listener for save button
        document.getElementById('saveAnalysisBtn').addEventListener('click', function() {
            saveAnalysisToCase();
        });
    }
    
    // Update content
    document.getElementById('speedyTrialAnalysisContent').innerHTML = analysisHtml;
    
    // Show modal
    $('#speedyTrialModal').modal('show');
}

// Save analysis to case
function saveAnalysisToCase() {
    // Get analysis content
    const analysisContent = document.getElementById('speedyTrialAnalysisContent').innerHTML;
    
    // Get case ID from URL or data attribute
    const caseId = document.getElementById('caseTimeline').dataset.caseId;
    
    // Save via AJAX
    $.ajax({
        url: `/case/${caseId}/save-timeline-analysis`,
        method: 'POST',
        data: {
            analysis: analysisContent
        },
        success: function(response) {
            if (response.success) {
                alert('Analysis saved to case successfully!');
                $('#speedyTrialModal').modal('hide');
            } else {
                alert('Error saving analysis: ' + response.error);
            }
        },
        error: function() {
            alert('Error saving analysis. Please try again.');
        }
    });
}