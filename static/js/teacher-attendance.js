



document.addEventListener("DOMContentLoaded", function () {
    const dateFilter = document.getElementById("dateFilter");
    const sectionFilter = document.getElementById("sectionFilter");
    const subjectFilter = document.getElementById("subjectFilter");
    const statusFilter = document.getElementById("statusFilter");

    const attendanceRows = document.querySelectorAll(".attendance-row");
    const emptyState = document.getElementById("emptyState");

    if (!dateFilter || !sectionFilter || !subjectFilter || !statusFilter || !emptyState) {
        return;
    }

    function filterAttendance() {
        const selectedDate = dateFilter.value;
        const selectedSection = sectionFilter.value;
        const selectedSubject = subjectFilter.value;
        const selectedStatus = statusFilter.value;

        let visibleCount = 0;

        attendanceRows.forEach(function (row) {
            const matchesDate =
                !selectedDate || row.dataset.date === selectedDate;

            const matchesSection =
                selectedSection === "all" ||
                row.dataset.section === selectedSection;

            const matchesSubject =
                selectedSubject === "all" ||
                row.dataset.subject === selectedSubject;

            const matchesStatus =
                selectedStatus === "all" ||
                row.dataset.status === selectedStatus;


            if (matchesDate && matchesSection &&
                matchesSubject && matchesStatus) {

            if (
                matchesDate &&
                matchesSection &&
                matchesSubject &&
                matchesStatus
            ) {

                row.style.display = "";
                visibleCount++;
            } else {
                row.style.display = "none";
            }
        });

        emptyState.style.display =
            visibleCount === 0 ? "block" : "none";
    }

    dateFilter.addEventListener("change", filterAttendance);
    sectionFilter.addEventListener("change", filterAttendance);
    subjectFilter.addEventListener("change", filterAttendance);
    statusFilter.addEventListener("change", filterAttendance);

});


    filterAttendance();
});

