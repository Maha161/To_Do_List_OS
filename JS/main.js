document.addEventListener('DOMContentLoaded', () => {
    const taskForm = document.getElementById('task-form');
    const taskList = document.getElementById('task-list');

    const filterStatus = document.getElementById('filter-status');
    const filterPriority = document.getElementById('filter-priority');
    const filterDueDate = document.getElementById('filter-due-date');
    const resetFiltersBtn = document.getElementById('reset-filters');

    let editingTaskId = null; 

    function fetchTasks(filters = {}) {
        const queryParams = new URLSearchParams(filters).toString();
        fetch(`/api/tasks?${queryParams}`)
            .then(res => res.json())
            .then(tasks => {
                taskList.innerHTML = '';
                tasks.forEach(task => renderTask(task));
            })
            .catch(error => {
                console.error('Error fetching tasks:', error);
            });
    }

    function renderTask(task) {
        const li = document.createElement('li');
        li.className = `task ${task.completed ? 'completed' : ''}`;
        li.innerHTML = `
            <strong>${task.title}</strong><br>
            <small>${task.description || ''}</small><br>
            <small>Due: ${task.due_date || 'N/A'} | Priority: ${task.priority || 'N/A'}</small>
            <div class="task-buttons">
                <button onclick="toggleComplete('${task.id}', ${task.completed})">
                    ${task.completed ? 'Undo' : 'Complete'}
                </button>
                <button onclick="editTask(${JSON.stringify(task).replace(/"/g, '&quot;')})">Edit</button>
                <button onclick="deleteTask('${task.id}')">Delete</button>
            </div>
        `;
        taskList.appendChild(li);
    }

    taskForm.addEventListener('submit', e => {
        e.preventDefault();
        const title = document.getElementById('title').value;
        const description = document.getElementById('description').value;
        const due_date = document.getElementById('due_date').value;
        const priority = document.getElementById('priority').value;

        const taskData = { title, description, due_date, priority };

        if (editingTaskId) {
            // Update existing task
            fetch(`/api/tasks/${editingTaskId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(taskData)
            })
            .then(() => {
                editingTaskId = null;
                taskForm.reset();
                fetchTasks();
            })
            .catch(error => console.error('Error updating task:', error));
        } else {
            fetch('/api/tasks', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(taskData)
            })
            .then(res => res.json())
            .then(task => {
                renderTask(task);
                taskForm.reset();
            })
            .catch(error => console.error('Error creating task:', error));
        }
    });

    window.deleteTask = (id) => {
        fetch(`/api/tasks/${id}`, { method: 'DELETE' })
            .then(() => fetchTasks())
            .catch(error => console.error('Error deleting task:', error));
    };

    window.toggleComplete = (id, completed) => {
        const endpoint = completed ? 'incomplete' : 'complete';
        fetch(`/api/tasks/${id}/${endpoint}`, { method: 'PUT' })
            .then(() => fetchTasks())
            .catch(error => console.error('Error updating task status:', error));
    };

    window.editTask = (task) => {
        document.getElementById('title').value = task.title;
        document.getElementById('description').value = task.description;
        document.getElementById('due_date').value = task.due_date;
        document.getElementById('priority').value = task.priority;
        editingTaskId = task.id;
        taskForm.scrollIntoView({ behavior: 'smooth' });
    };

    function applyFilters() {
        const filters = {};
        if (filterStatus.value) filters.completed = filterStatus.value;
        if (filterPriority.value) filters.priority = filterPriority.value;
        if (filterDueDate.value) filters.due_date = filterDueDate.value;

        fetchTasks(filters);
    }

    filterStatus.addEventListener('input', applyFilters);
    filterPriority.addEventListener('input', applyFilters);
    filterDueDate.addEventListener('input', applyFilters);

    resetFiltersBtn.addEventListener('click', () => {
        filterStatus.value = '';
        filterPriority.value = '';
        filterDueDate.value = '';
        fetchTasks();
    });

    fetchTasks(); 
});
