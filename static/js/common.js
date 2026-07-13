/**
 * @typedef {Object} StatusData
 * @property {string} url - The Controller URL
 * @property {string|null} battery - Battery status string
 */

const socket = io();

// Common DOM elements that might exist
const statusDiv = document.getElementById('status');
const linkDiv = document.getElementById('controller-link');

/**
 * Updates the status display if the element exists.
 * @param {string} msg - The message to display.
 * @param {'info'|'warn'|'error'|'debug'} [level='info'] - Log level.
 */
function updateStatus(msg, level = 'info') {
    if (statusDiv) {
        statusDiv.innerText = msg;
        if (level === 'error') {
            statusDiv.style.color = 'red';
            console.error(msg);
        } else if (level === 'warn') {
            statusDiv.style.color = 'orange';
            console.warn(msg);
        } else if (level === 'debug') {
            console.debug(msg);
        } else {
            statusDiv.style.color = 'lime';
            console.info(msg);
        }
    } else {
        // Fallback if no UI element
        console.log(`[${level.toUpperCase()}] ${msg}`);
    }
}

// Global Socket Events
socket.on('connect', () => {
    updateStatus('Socket connected');
});

socket.on('disconnect', () => {
    updateStatus('Socket disconnected', 'warn');
});

socket.on('connect_error', (err) => {
    updateStatus('Socket error: ' + err.message, 'error');
});

socket.on('robot_status', (/** @type {StatusData} */ data) => {
    if (data.url && linkDiv) {
        linkDiv.innerHTML = `<a href="${data.url}" target="_blank">Open Controller</a><br><small>${data.url}</small>`;
    }
    // Could display battery here if data.battery is set
});
