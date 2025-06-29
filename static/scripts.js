// Collaborators Dashboard JS

document.addEventListener('DOMContentLoaded', function () {
    loadCollaborators();

    document.getElementById('searchForm').addEventListener('submit', function (e) {
        e.preventDefault();
        loadCollaborators();
    });

    document.getElementById('addCollaboratorBtn').addEventListener('click', function () {
        openModal();
    });

    document.getElementById('closeModal').onclick = closeModal;
    document.getElementById('cancelBtn').onclick = closeModal;

    document.getElementById('collaboratorForm').onsubmit = function (e) {
        e.preventDefault();
        saveCollaborator();
    };
});

function loadCollaborators() {
    let query = document.getElementById('searchQuery').value;
    let url = '/collaborators';
    if (query) {
        url += `?search=${encodeURIComponent(query)}`;
    }
    fetch(url)
        .then(response => response.json())
        .then(data => renderCollaborators(data));
}

function renderCollaborators(collaborators) {
    let tbody = document.getElementById('collaboratorsTableBody');
    tbody.innerHTML = '';
    const today = new Date();
    collaborators.forEach(col => {
        let certDate = new Date(col.certification_date);
        let daysLeft = Math.ceil((certDate - today) / (1000 * 60 * 60 * 24));
        let highlight = daysLeft <= 14 ? 'expiring-soon' : '';
        let row = document.createElement('tr');
        row.className = highlight;
        row.innerHTML = `
            <td>${col.name}</td>
            <td>${col.surname}</td>
            <td>${col.certification}</td>
            <td>${certDate.toLocaleDateString()}</td>
            <td>
                <button class="btn btn-primary" onclick="editCollaborator(${col.id})">Edit</button>
                <button class="btn btn-danger" onclick="deleteCollaborator(${col.id})">Delete</button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function openModal(collaborator = null) {
    document.getElementById('collaboratorModal').style.display = 'block';
    document.getElementById('modalTitle').textContent = collaborator ? 'Edit Collaborator' : 'Add Collaborator';
    document.getElementById('collaboratorId').value = collaborator ? collaborator.id : '';
    document.getElementById('name').value = collaborator ? collaborator.name : '';
    document.getElementById('surname').value = collaborator ? collaborator.surname : '';
    document.getElementById('certification').value = collaborator ? collaborator.certification : '';
    document.getElementById('certification_date').value = collaborator ? collaborator.certification_date : '';
}

function closeModal() {
    document.getElementById('collaboratorModal').style.display = 'none';
    document.getElementById('collaboratorForm').reset();
}

function saveCollaborator() {
    let id = document.getElementById('collaboratorId').value;
    let data = {
        name: document.getElementById('name').value,
        surname: document.getElementById('surname').value,
        certification: document.getElementById('certification').value,
        certification_date: document.getElementById('certification_date').value
    };
    let method = id ? 'PUT' : 'POST';
    let url = id ? `/collaborators/${id}` : '/collaborators';
    fetch(url, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    }).then(response => {
        if (response.ok) {
            closeModal();
            loadCollaborators();
        } else {
            alert('Error saving collaborator');
        }
    });
}

function editCollaborator(id) {
    fetch(`/collaborators/${id}`)
        .then(response => response.json())
        .then(data => openModal(data));
}

function deleteCollaborator(id) {
    if (!confirm('Are you sure you want to delete this collaborator?')) return;
    fetch(`/collaborators/${id}`, { method: 'DELETE' })
        .then(response => {
            if (response.ok) {
                loadCollaborators();
            } else {
                alert('Error deleting collaborator');
            }
        });
}
