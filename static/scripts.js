function searchVehicles() {
    let query = document.getElementById('searchQuery').value;
    
    fetch(`/search?query=${query}`)
        .then(response => response.json())
        .then(data => {
            let tableBody = document.getElementById('vehicleTableBody');
            tableBody.innerHTML = '';

            data.forEach(vehicle => {
                let inspectionDate = new Date(vehicle.inspection_date);
                let formattedInspectionDate = `${inspectionDate.getDate()}/${inspectionDate.getMonth() + 1}/${inspectionDate.getFullYear()}`;

                let row = document.createElement('tr');
                row.innerHTML = `
                    <td>${vehicle.license_plate}</td>
                    <td>${vehicle.make}</td>
                    <td>${vehicle.model}</td>
                    <td>${formattedInspectionDate}</td>
                    <td>${vehicle.status}</td>
                    <td>
                        <a href="/edit/${vehicle.id}">Edit</a>
                        <form action="/delete/${vehicle.id}" method="post" style="display:inline;">
                            <button type="submit">Delete</button>
                        </form>
                    </td>
                `;
                tableBody.appendChild(row);
            });
        });
}
