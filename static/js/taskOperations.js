const tasksContainer = document.getElementById("list-tasks");
const addTaskButton = document.getElementById('add-task-btn');
const taskContentInput = document.getElementById('task-content');

const socketAdd = new WebSocket("ws://" + window.location.host + "/ws/add");
const socketDelete = new WebSocket("ws://" + window.location.host + "/ws/delete");

// Add event to button for adding a task
addTaskButton.addEventListener('click', function(){
    if (taskContentInput.value.length < 3) {
        return;
    }

    tasksContainer.appendChild(
        createTask(taskContentInput.value)
    );
    ws_sendTaskToServer(taskContentInput.value)

    // Reset input
    taskContentInput.value = '';
}, false);



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

    const span = document.createElement("span");
    span.textContent = content;

    const button = document.createElement("button");
    button.onclick = ws_deleteTaskFromServer;
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
function ws_sendTaskToServer(taskContent) {
    const taskData = {
        content: taskContent
    };

    socketAdd.send(JSON.stringify(taskData));
}

// Function to handle task deletion from the server
function ws_deleteTaskFromServer(element){
    let taskID = element.parentNode.getAttribute("id");

    socketDelete.send(JSON.stringify({ id: taskID }));
    element.parentNode.remove();
}