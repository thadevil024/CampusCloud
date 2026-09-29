// ================================
// CampusCloud - Main JavaScript
// ================================


// --------------------------------
// Register Page - Role Fields
// --------------------------------

function toggleFields() {

    const role = document.getElementById("role");

    if (!role) {
        return;
    }

    const selectedRole = role.value;

    const studentFields = document.getElementById("studentFields");
    const teacherFields = document.getElementById("teacherFields");
    const adminFields = document.getElementById("adminFields");


    // Hide all fields first

    if (studentFields) {
        studentFields.style.display = "none";
    }

    if (teacherFields) {
        teacherFields.style.display = "none";
    }

    if (adminFields) {
        adminFields.style.display = "none";
    }


    // Show fields according to role

    if (selectedRole === "student") {

        if (studentFields) {
            studentFields.style.display = "block";
        }

    }

    else if (selectedRole === "teacher") {

        if (teacherFields) {
            teacherFields.style.display = "block";
        }

    }

    else if (selectedRole === "admin") {

        if (adminFields) {
            adminFields.style.display = "block";
        }

    }

}


// --------------------------------
// Page Load
// --------------------------------

document.addEventListener("DOMContentLoaded", function () {

    toggleFields();

});