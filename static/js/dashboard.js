// Function to show GPA section
function showGPA() {
    hideAllDisplays();
    const gpaDisplay = document.getElementById('gpaDisplay');
    gpaDisplay.style.display = 'block';
}

// Function to show transcript section
function showTranscript() {
    hideAllDisplays();
    const transcriptDisplay = document.getElementById('transcriptDisplay');
    transcriptDisplay.style.display = 'block';
}

// Function to show current courses section
function showCurrentCourses() {
    hideAllDisplays();
    const currentCourses = document.getElementById('currentCourses');
    currentCourses.style.display = 'block';
}

// Helper function to hide all display sections
function hideAllDisplays() {
    document.getElementById('gpaDisplay').style.display = 'none';
    document.getElementById('transcriptDisplay').style.display = 'none';
    document.getElementById('currentCourses').style.display = 'none';
}

// Calculate GPA helper function
function calculateGPA(grades) {
    const gradePoints = {
        'A': 4.0, 'A-': 3.7,
        'B+': 3.3, 'B': 3.0, 'B-': 2.7,
        'C+': 2.3, 'C': 2.0, 'C-': 1.7,
        'D+': 1.3, 'D': 1.0, 'F': 0.0
    };
    let totalPoints = 0;
    let totalCourses = 0;

    grades.forEach(grade => {
        if (grade in gradePoints) {
            totalPoints += gradePoints[grade];
            totalCourses++;
        }
    });

    return totalCourses > 0 ? (totalPoints / totalCourses).toFixed(2) : '0.00';
}

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', function() {
    // Show current courses by default
    showCurrentCourses();
});