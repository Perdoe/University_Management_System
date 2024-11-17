// Function to fetch department information
async function fetchDepartmentInfo() {
    try {
        const response = await fetch('/api/staff/department-info');
        if (!response.ok) throw new Error('Failed to fetch department info');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching department info:', error);
        return null;
    }
}

// Function to fetch performance data
async function fetchPerformanceData() {
    try {
        const response = await fetch('/api/staff/performance-data');
        if (!response.ok) throw new Error('Failed to fetch performance data');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching performance data:', error);
        return null;
    }
}

// Function to handle search
async function handleSearch(query) {
    try {
        const response = await fetch(`/api/staff/search?q=${encodeURIComponent(query)}`);
        if (!response.ok) throw new Error('Failed to perform search');
        const results = await response.json();
        return results;
    } catch (error) {
        console.error('Error performing search:', error);
        return [];
    }
}