// Depends on nipplejs and socket (from common.js)

let move = {x: 0, y: 0};
let turn = 0;

/**
 * Sends joystick data to the backend.
 */
function sendData() {
    socket.emit('joystick_data', {lx: move.x, ly: move.y, rx: turn});
}

// Left Stick (Movement)
// @ts-ignore - nipplejs global
const leftManager = nipplejs.create({
    zone: document.getElementById('left-zone'),
    mode: 'static', position: {left: '50%', top: '50%'}, color: 'cyan'
});

// Right Stick (Rotation)
// @ts-ignore - nipplejs global
const rightManager = nipplejs.create({
    zone: document.getElementById('right-zone'),
    mode: 'static', position: {left: '50%', top: '50%'}, color: 'red',
    lockX: true // Only allow left/right movement for turning
});

leftManager.on('move', (evt, data) => {
    move.x = data.vector.x;
    move.y = data.vector.y;
    sendData();
});

leftManager.on('end', () => {
    move.x = 0;
    move.y = 0;
    sendData();
});

rightManager.on('move', (evt, data) => {
    turn = data.vector.x;
    sendData();
});

rightManager.on('end', () => {
    turn = 0;
    sendData();
});
