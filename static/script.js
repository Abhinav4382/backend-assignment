document.addEventListener("DOMContentLoaded", function () {
    const apiForm = document.getElementById("apiForm");
    const facilityDropdown = document.getElementById("facilityDropdown");
    const addFacilityButton = document.getElementById("addFacilityButton");
    const facilityList = document.getElementById("facilityList");
    const responseTableBody = document.getElementById("responseTableBody");
    const responseContainer = document.getElementById("responseContainer");

    
    let selectedFacilities = [];


    addFacilityButton.addEventListener("click", function () {
        const selectedFacility = facilityDropdown.value;


        if (selectedFacility && !selectedFacilities.includes(selectedFacility)) {
            selectedFacilities.push(selectedFacility);


            const listItem = document.createElement("li");
            listItem.className = "list-group-item d-flex justify-content-between align-items-center";


            listItem.textContent = selectedFacility;


            const removeButton = document.createElement("button");
            removeButton.className = "btn btn-sm btn-danger";
            removeButton.textContent = "Remove";


            removeButton.addEventListener("click", function () {
                selectedFacilities = selectedFacilities.filter((facility) => facility !== selectedFacility);
                listItem.remove();
            });


            listItem.appendChild(removeButton);


            facilityList.appendChild(listItem);
        }
    });


    apiForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const startDate = document.getElementById("startdate").value;
        const endDate = document.getElementById("enddate").value;

        if (!startDate || !endDate) {
            alert("Please select a valid date range.");
            return;
        }

        if (selectedFacilities.length === 0) {
            alert("Please select at least one facility.");
            return;
        }


        const payload = {
            startDate: startDate,
            endDate: endDate,
            businessFacilities: selectedFacilities,
        };

        try {

            const response = await fetch("http://127.0.0.1:8000/api/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }


            const data = await response.json();


            responseTableBody.innerHTML = ""; 
            for (const [facility, emission] of Object.entries(data)) {
                const row = `<tr>
                    <td>${facility}</td>
                    <td>${emission}</td>
                </tr>`;
                responseTableBody.innerHTML += row;
            }


            responseContainer.classList.remove("d-none");
        } catch (error) {
            console.error("Error:", error);
            alert(`Failed to fetch data from the API: ${error.message}`);
        }
    });
});
