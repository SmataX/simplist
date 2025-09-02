const tasksContainer = document.getElementById("list-tasks");
const addTaskButton = document.getElementById('add-task-btn');
const taskContentInput = document.getElementById('task-content');

const socket = new WebSocket("ws://" + window.location.host + "/ws");

// Add event to button for adding a task
addTaskButton.addEventListener('click', function(){
    if (taskContentInput.value.length < 3) {
        return;
    }

    tasksContainer.appendChild(
        createTask(taskContentInput.value)
    );

    ws_addTask(taskContentInput.value)

    // Reset input
    taskContentInput.value = '';
}, false);
console.log("test ", addTaskButton.getAttribute("userid"));


// Add event to input for adding a task on Enter key press
taskContentInput.addEventListener("keyup", function(event) {
    event.preventDefault();
    if (event.keyCode === 13) {
        addTaskButton.click();
    }
});


// Create task element
function createTask(content) {
    const taskDiv = document.createElement("div");
    taskDiv.classList.add("task");
    taskDiv.addEventListener("click", function() {
        ws_updateTask(this);
    });

    const span = document.createElement("span");
    span.textContent = content;

    const button = document.createElement("button");
    button.addEventListener("click", function() {
        ws_deleteTask(this);
    });
    const img = document.createElement("img");
    img.classList.add("icon");
    img.src = "/static/icons/trash.png";
    img.alt = "delete task";

    button.appendChild(img);
    taskDiv.appendChild(span);
    taskDiv.appendChild(button);

    return taskDiv;
}

// Function to send task content to the server
function ws_addTask(taskContent) {
    const data = {
        action: "add",
        content: taskContent,
    };

    socket.send(JSON.stringify(data));
}

// Function to handle task deletion from the server
function ws_deleteTask(element){
    const data = {
        action: "delete",
        id: element.parentNode.getAttribute("id"),
    };

    socket.send(JSON.stringify(data));
}

// Function to handle task status update on the server
function ws_updateTask(element) {
    const data = {
        action: "update",
        id: element.getAttribute("id"),
    };

    socket.send(JSON.stringify(data));
}

// Websocket message handler
socket.onmessage = function(event) {
    const parsedData = JSON.parse(event.data);

    if (!parsedData.status === 0) {
        console.error("Error from server:", parsedData.error);
        return;
    }

    switch (parsedData.action) {
        case "add":
            handleAddTask(parsedData);
            break;
        case "delete":
            handleDeleteTask(parsedData);
            break;
        case "update":
            handleUpdateTask(parsedData);
            break;
        case "error":
            break;
        default:
            console.error("Unknown action:", parsedData.action);
    }
}

function handleAddTask(data) {
    tasksContainer.lastChild.setAttribute("id", data.id);
}

function handleDeleteTask(data) {
    let taskDiv = document.getElementById(data.id);
    if (taskDiv) {
        taskDiv.remove();

        // If no tasks left, show "No tasks available" message
        if (tasksContainer.children.length === 0) {
            const noTasksMessage = document.createElement("p");
            noTasksMessage.id = "no-tasks-available";
            noTasksMessage.textContent = "No tasks available.";
            tasksContainer.appendChild(noTasksMessage);
        }
    }
}

function handleUpdateTask(data) {
    let taskDiv = document.getElementById(data.id);
    if (taskDiv) {
        if (taskDiv.className === "task")
            taskDiv.className += " task-completed";
        else
            taskDiv.className = "task";
    }
}