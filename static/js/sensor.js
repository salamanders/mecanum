// Depends on socket (from common.js)

const disp = document.getElementById('val');
const accelDisp = document.getElementById('accel');

let currentHeading = 0;
let currentAccel = {x: 0, y: 0, z: 0};
let sensorsActive = false;

// Prevent screen sleep
async function wakeLock() {
    if (!('wakeLock' in navigator)) {
        updateStatus('Wake Lock API not supported', 'warn');
        return;
    }
    try {
        // @ts-ignore - navigator.wakeLock
        await navigator.wakeLock.request('screen');
        updateStatus('Wake Lock active');
    } catch (err) {
        updateStatus('Wake Lock failed: ' + err.message, 'error');
    }
}

wakeLock();

/**
 * Handles DeviceOrientation events (Compass).
 * @param {DeviceOrientationEvent} event
 */
function handleOrientation(event) {
    // Alpha is usually the compass heading (0-360)
    if (event.alpha !== null) {
        currentHeading = event.alpha;
        if (disp) disp.innerText = Math.round(currentHeading).toString();
    }
}

/**
 * Handles DeviceMotion events (Accelerometer).
 * @param {DeviceMotionEvent} event
 */
function handleMotion(event) {
    // acceleration excluding gravity
    const a = event.acceleration;
    if (a) {
        currentAccel = {
            x: a.x || 0,
            y: a.y || 0,
            z: a.z || 0
        };
        if (accelDisp) {
            accelDisp.innerText = `Accel: ${currentAccel.x.toFixed(2)}, ${currentAccel.y.toFixed(2)}, ${currentAccel.z.toFixed(2)}`;
        }
    }
}

// Transmission Loop (100ms)
setInterval(() => {
    if (sensorsActive) {
        socket.emit('sensor_data', {
            heading: currentHeading,
            ax: currentAccel.x,
            ay: currentAccel.y,
            az: currentAccel.z
        });
    }
}, 100);

/**
 * Requests permission for iOS 13+ devices and starts listeners.
 */
// eslint-disable-next-line no-unused-vars
function requestPerms() {
    // @ts-ignore - DeviceOrientationEvent
    if (!window.DeviceOrientationEvent) {
        updateStatus('DeviceOrientationEvent not supported', 'error');
        return;
    }

    console.debug('Requesting sensor permissions...');

    // iOS requires explicit permission
    // @ts-ignore - DeviceOrientationEvent.requestPermission
    if (typeof DeviceOrientationEvent.requestPermission === 'function') {
        // @ts-ignore
        DeviceOrientationEvent.requestPermission()
            .then((/** @type {PermissionState} */ response) => {
                if (response === 'granted') {
                    window.addEventListener('deviceorientation', handleOrientation);
                    updateStatus('Orientation granted');

                    // Try requesting motion permission
                    // @ts-ignore
                    if (typeof DeviceMotionEvent.requestPermission === 'function') {
                        // @ts-ignore
                        return DeviceMotionEvent.requestPermission();
                    } else {
                        // Non-iOS or older iOS where one permission might cover both or Motion doesn't need it
                        window.addEventListener('devicemotion', handleMotion);
                        sensorsActive = true;
                        updateStatus('Sensors active (Motion implied)');
                        return null;
                    }
                } else {
                    throw new Error('Orientation permission denied');
                }
            })
            .then((/** @type {PermissionState|null} */ response) => {
                if (response === 'granted') {
                    window.addEventListener('devicemotion', handleMotion);
                    sensorsActive = true;
                    updateStatus('All Sensors active');
                }
            })
            .catch((/** @type {Error} */ err) => {
                updateStatus('Permission error: ' + err.message, 'error');
            });
    } else {
        // Non-iOS
        window.addEventListener('deviceorientation', handleOrientation);
        window.addEventListener('devicemotion', handleMotion);
        sensorsActive = true;
        updateStatus('Sensors started (non-iOS)');
    }
}
