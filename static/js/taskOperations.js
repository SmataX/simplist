

socket.on("connect", () => {
    console.log("Connected to server with id:", socket.id);
});


const tasksContainer = document.getElementById("list-tasks");
const addTaskButton = document.getElementById('add-task-btn');
const taskContentInput = document.getElementById('task-content');

addTaskButton.addEventListener('click', function(){
    if (taskContentInput.value.length < 3) {
        return;
    }

    tasksContainer.appendChild(
        createTask(taskContentInput.value)
    );

    // Reset input
    taskContentInput.value = '';
}, false);


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
    const img = document.createElement("img");
    img.classList.add("icon");
    img.src = "/static/icons/trash.png";
    img.alt = "delete task";

    button.appendChild(img);
    taskDiv.appendChild(span);
    taskDiv.appendChild(button);

    return taskDiv;
}