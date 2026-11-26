


document.addEventListener("DOMContentLoaded", function () {

    const filter = document.getElementById("assignmentFilter");

    const assignments = document.querySelectorAll(".assignment-item");

    if (!filter) {
        return;
    }

    filter.addEventListener("change", function () {

        const selectedStatus = filter.value;

        assignments.forEach(function (item) {

            const status = item.dataset.status;

            if (selectedStatus === "all" || status === selectedStatus) {
                item.style.display = "block";
            } else {
                item.style.display = "none";
            }

        });

    });

});


@login_required
def teacher_assignments(request):
    if request.user.role != "TEACHER":
        return HttpResponseForbidden("Only teachers can access this page.")

    assignments = Assignment.objects.filter(
        teaching_assignment__teacher=request.user
    ).select_related(
        "teaching_assignment__section",
        "teaching_assignment__subject"
    )

    total_assignments = assignments.count()

    active_count = assignments.filter(
        status=Assignment.Status.ACTIVE
    ).count()

    closed_count = assignments.filter(
        status=Assignment.Status.CLOSED
    ).count()

    draft_count = assignments.filter(
        status=Assignment.Status.DRAFT
    ).count()

    context = {
        "assignments": assignments,
        "total_assignments": total_assignments,
        "active_count": active_count,
        "closed_count": closed_count,
        "draft_count": draft_count,
    }

    return render(
        request,
        "teacher/assignments.html",
        context
    )

