document.addEventListener('DOMContentLoaded', function() {
    const onTimeInput = document.getElementById('on-time');
    const offTimeInput = document.getElementById('off-time');
    const submitBtn = document.getElementById('submit-btn');
    const scheduleItems = document.getElementById('schedule-items');
    const currentState = document.getElementById('current-state');
    const nextEvent = document.getElementById('next-event');
    
    // Connect to WebSocket server
    const socket = new WebSocket('ws://localhost:8765');
    
    socket.onopen = function(e) {
        console.log('Connected to WebSocket server');
    };
    
    socket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        if (data.type === 'schedule_update') {
            updateScheduleList(data.schedules);
        } else if (data.type === 'status_update') {
            updateStatus(data.state, data.nextEvent);
        }
    };
    
    socket.onclose = function(event) {
        if (event.wasClean) {
            console.log(`Connection closed cleanly, code=${event.code}, reason=${event.reason}`);
        } else {
            console.log('Connection died');
            // Try to reconnect after 5 seconds
            setTimeout(() => {
                window.location.reload();
            }, 5000);
        }
    };
    
    socket.onerror = function(error) {
        console.log(`WebSocket error: ${error.message}`);
    };
    
    submitBtn.addEventListener('click', function() {
        const onTime = onTimeInput.value;
        const offTime = offTimeInput.value;
        
        if (!onTime || !offTime) {
            alert('Please set both ON and OFF times');
            return;
        }
        
        const schedule = {
            onTime: onTime,
            offTime: offTime
        };
        
        socket.send(JSON.stringify({
            type: 'set_schedule',
            schedule: schedule
        }));
    });
    
    function updateScheduleList(schedules) {
        scheduleItems.innerHTML = '';
        
        if (schedules.length === 0) {
            const item = document.createElement('li');
            item.textContent = 'No active schedules';
            scheduleItems.appendChild(item);
            return;
        }
        
        schedules.forEach(schedule => {
            const item = document.createElement('li');
            item.textContent = `ON at ${schedule.onTime}, OFF at ${schedule.offTime}`;
            scheduleItems.appendChild(item);
        });
    }
    
    function updateStatus(state, nextEventTime) {
        currentState.textContent = `Light: ${state === '1' ? 'ON' : 'OFF'}`;
        currentState.style.color = state === '1' ? 'green' : 'red';
        
        if (nextEventTime) {
            const eventType = nextEventTime.state === '1' ? 'ON' : 'OFF';
            nextEvent.textContent = `Next event: ${eventType} at ${nextEventTime.time}`;
        } else {
            nextEvent.textContent = 'Next event: Not scheduled';
        }
    }
    
    // Request initial data
    setTimeout(() => {
        if (socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ type: 'get_initial_data' }));
        }
    }, 1000);
});