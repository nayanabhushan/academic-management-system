
document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById("searchAssignment");
    const statusFilter = document.getElementById("statusFilter");
    const assignmentItems = document.querySelectorAll(".assignment-item");
    const emptyMessage = document.getElementById("emptyMessage");

    const createButton = document.getElementById("createAssignmentBtn");



    function filterAssignments() {
        const searchText = searchInput.value.toLowerCase().trim();
        const selectedStatus = statusFilter.value;

        let visibleCount = 0;

        assignmentItems.forEach(function (item) {
            const text = item.innerText.toLowerCase();
            const status = item.dataset.status;

            const matchesSearch = text.includes(searchText);
            const matchesStatus =
                selectedStatus === "all" || status === selectedStatus;

            if (matchesSearch && matchesStatus) {
                item.style.display = "";
                visibleCount++;
            } else {
                item.style.display = "none";
            }
        });

        emptyMessage.style.display =
            visibleCount === 0 ? "block" : "none";
    }

    if (searchInput && statusFilter && emptyMessage) {
        searchInput.addEventListener("input", filterAssignments);
        statusFilter.addEventListener("change", filterAssignments);
    }


    if (createButton) {
        createButton.addEventListener("click", function () {
            alert(
                "The Create Assignment feature will be connected to the backend later."
            );
        });
    }


});
