// ============================================== HELPERS ==============================================================

function feedbackState(feedback, message) {
    feedback.disabled = true;
    feedback.textContent = message;
};

function feedbackStateFinal(feedback, message) {
    feedback.disabled = false;
    feedback.textContent = message;
};

function temporaryUIMessage(feedback, message) {
    feedback.textContent = message;

    setTimeout(() => {
        feedback.textContent = "";
    }, 3000);
};

// ================================================= SIDEBAR ==========================================================



const sidebar = document.getElementById("sidebar");
const overlay = document.getElementById("overlay");
const openBtn = document.getElementById("sidebarBtn");
const closeBtn = document.getElementById("closeBtn");

if (openBtn && sidebar && overlay) {
    openBtn.addEventListener("click", function() {
        sidebar.classList.add("active");
        overlay.classList.add("active");
    });
};
if (closeBtn && sidebar && overlay) {
    closeBtn.addEventListener("click", function() {
        sidebar.classList.remove("active");
        overlay.classList.remove("active");
    });
};
if (overlay && sidebar) {
    overlay.addEventListener("click", function() {
        sidebar.classList.remove("active");
        overlay.classList.remove("active");
    });
};



// ================================================= HOME ===============================================================





// ================================================ ADD STUDENT =========================================================





const addForm = document.getElementById("myForm");
const addMessage = document.getElementById("addMessage");


if (addForm) {

  const submitBtn = document.querySelector('button[type="submit"]');

addForm.addEventListener("submit", function(e) {
    e.preventDefault();

    const formData = new FormData(addForm);

    feedbackState(submitBtn, "Adding...")
    
    fetch("/add_student", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        document.querySelectorAll(".errorField").forEach(input => {
            input.classList.remove("errorField");
        });
        if (data.success) {
            temporaryUIMessage(addMessage, data.message);
            addForm.reset();
        }
        else {
            const input = document.getElementById(data.field);
            temporaryUIMessage(addMessage, data.message);
            input.classList.add("errorField");
        }
    })
    .finally(() => {
        feedbackStateFinal(submitBtn, "Add Student")
    });
});
};






// ================================================== VIEW STUDENTS =====================================================




const viewStudents = document.getElementById("viewStudents");

const viewStudentsTbody = document.getElementById("viewStudentsTbody");
const viewStudentsCount = document.getElementById("viewStudentsCount");

//pagination
const pagination = document.getElementById("pagination");
const paginationBtns = document.getElementById("paginationBtns");


const sortBy = document.getElementById("sortBy");
const sortOrder = document.getElementById("sortOrder");

// VIEW STUDENTS TABLE

if (viewStudents) {

    function renderStudents(students) {
    

    let rows = "";


        students.forEach(student => {
        rows +=    `<tr data-id="${student[0]}">
                     <td><strong>${student[0]}</strong></td>
                     <td><strong>${student[1]}</strong></td>
                     <td>${student[2]}</td>
                     <td>${student[3]}</td>
                     <td>${student[4]}</td>
                     <td>${student[5]}</td>
                     <td>${student[6]}</td>
                    </tr>`
        });
        viewStudentsTbody.innerHTML = rows;
    

        viewStudentsTbody.addEventListener("click", function(event) {
            const row = event.target.closest("tr");
            if (!row) return;

            const studentId = row.dataset.id;
            window.location.href = `/student/${studentId}?from=/view_students`;
        });

    };

    fetch("/view_students_results", {
        method: "GET"
    })
    .then(response => response.json())
    .then(data => {
        const students = data.students;
        const count = data.count;
        const studentsPerPage = 10;

        paginate(1, students);
        renderPagination(students);

        // ---------------------------- PAGINATION -------------------------- //


        function renderPagination(students) {

            let currentPage = document.getElementById("pageNum").dataset.id;

            paginationBtns.innerHTML = "";
            
            const totalPages = Math.ceil(students.length / studentsPerPage);


            // ----------- Previous ----------- //

            const previous = document.createElement("button");
            previous.textContent = "Prev";
            previous.classList.add("page-button")
     
            previous.addEventListener("click", () => {
                if (currentPage == 1) {
                    return previous.disabled;
                }
                currentPage-- ;
                paginate(currentPage, students);
            });
            paginationBtns.appendChild(previous);

            // ---------- Buttons ---------- //

            for (let i = 1; i <= totalPages; i++) {
                    const button = document.createElement("button");
                    button.textContent = i;
                    button.classList.add("page-button-i");
            
                    button.addEventListener("click", () => {
                        currentPage = i;
                        paginate(currentPage, students);
                    });

                    paginationBtns.appendChild(button);
                };

            // ---------- Next ------------ //

            const next = document.createElement("button");
            next.textContent = "Next";
            next.classList.add("page-button")

            next.addEventListener("click", () => {
                if (currentPage == totalPages) {
                    return next.disabled;
                }
                currentPage++;
                paginate(currentPage, students);
            });
            paginationBtns.appendChild(next);

        };

        function paginate(currentPage, students) {   

            // Pagination

            const start = (currentPage - 1) * studentsPerPage;
            const end = start + studentsPerPage;

            const pageStudents = students.slice(start, end);
            renderStudents(pageStudents);
            pagination.innerHTML = `<p data-id=${currentPage} id="pageNum" class="pageNum">Page ${currentPage}</p>`
            viewStudentsCount.textContent = `Showing ${pageStudents.length} out of ${count} students`

        };
        
        

        // ---------------------------- SORT RESULTS ------------------------ //



        sortBy.addEventListener("change", sortStudents);
        sortOrder.addEventListener("change", sortStudents);
        
        function sortStudents() {
            const sort = sortBy.value;
            const order = sortOrder.value;
    
            //------- Getting the sort options -----------

            const sortOptions = {
                default: {property: 0, type: "num"},
                name: {property: 1, type: "str"},
                age: {property: 2, type: "num"},
                grade: {property: 3, type: "num"},
                course: {property: 4, type: "str"}
            };

            const selected = sortOptions[sort];

            const property = selected.property;
            const type = selected.type;

        // order multiplier

            const direction = order === "ASC" ? 1: - 1


        // -------------- sort code ----------------

            if (type == "str") {
                const sorted = students.toSorted((a, b) => a[property].localeCompare(b[property]) * direction);
                paginate(1,sorted);
                renderPagination(sorted);
            }
            else if (type == "num") {
                const sorted = students.toSorted((a, b) => (a[property] - b[property]) * direction);
                paginate(1, sorted);    
                renderPagination(sorted);
            }
        };

    });
    

}






// ============================================ SEARCH STUDENT ========================================================




// Search Form Elements
const searchForm = document.getElementById("searchForm");
const searchMessage = document.getElementById("searchMessage");
const itemCount = document.getElementById("itemCount");
const clearBtn = document.getElementById("clearBtn")
const clickMsg = document.getElementById("clickMsg");

// Table Elements
const tableContainer = document.getElementById("tableContainer");
const tableBody = document.getElementById("tableBody");
const nameInput = document.getElementById("name");

// Pagination
const searchPaginationBtns = document.getElementById("searchPaginationBtns");
const pageNumDiv = document.getElementById("pageNumDiv");

// Sort & Sort Order
const searchSortBy = document.getElementById("searchSortBy");
const searchSortOrder = document.getElementById("searchSortOrder");




if (searchForm) {

    function renderStudents(students, count, params) {
    

    let rows = "";

    // empty message

    if (students.length == 0) {
        if (nameInput.value == "") {
            itemCount.textContent = "No students found";
        }
        else {
            itemCount.textContent = "No students found, try checking your spelling";
        }
    }
    
    // actual render students code

    else {
        students.forEach(student => {
        rows +=    `<tr data-id="${student[0]}">
                     <td><strong>${student[0]}</strong></td>
                     <td><strong>${student[1]}</strong></td>
                     <td>${student[2]}</td>
                     <td>${student[3]}</td>
                     <td>${student[4]}</td>
                    </tr>`
        });
        tableBody.innerHTML = rows;
    };

    // count message

    if (students.length == 1) {
        itemCount.textContent = count + " student found";
    }
    if (students.length > 1) {
        itemCount.textContent = count + " students found";
    };
    

    tableBody.addEventListener("click", function(event) {
        const row = event.target.closest("tr");
        if (!row) return;

        const studentId = row.dataset.id;
 
        window.location.href = `/student/${studentId}?from=/search_student`;
    });

    };

    // ------------------ SEARCH FORM --------------------

    searchForm.addEventListener("submit", function(event) {
    event.preventDefault();
 
    tableContainer.classList.remove("active");

    const searchFormData = new FormData(searchForm);
    const params = new URLSearchParams(searchFormData);

    fetch(`/search_student_results?${params}`, {
        method: "GET",
    })
    .then(response => response.json())
    .then(data => {
        const students = data.students;
        const count = data.count;

        if ( students.length >= 1) {
           tableContainer.classList.add("active");
        }
        const studentsPerPage = 5;
        paginate(1, students, params);
        renderPagination(students, params);


        // ---------------------------- PAGINATION -------------------------- //


        function renderPagination(students, params) {
            

            searchPaginationBtns.innerHTML = "";
            
            const totalPages = Math.ceil(students.length / studentsPerPage);


            // ----------- Previous ----------- //

            const previous = document.createElement("button");
            previous.textContent = "Previous";
            previous.classList.add("page-button");
     
            previous.addEventListener("click", () => {
                let currentPage = document.getElementById("searchPageNum").dataset.id;
                if (currentPage == 1) {
                    return previous.disabled;
                }
                currentPage-- ;
                paginate(currentPage, students, params);
            });
            searchPaginationBtns.appendChild(previous);


            // ---------- Buttons ---------- //

            for (let i = 1; i <= totalPages; i++) {
                    const button = document.createElement("button");
                    button.textContent = i;
                    button.classList.add("page-button-i");
            
                    button.addEventListener("click", () => {
                        let currentPage = document.getElementById("searchPageNum").dataset.id;
                        currentPage = i;
                        paginate(currentPage, students, params);
                    });

                    searchPaginationBtns.appendChild(button);
                };

            // ---------- Next ------------ //

            const next = document.createElement("button");
            next.textContent = "Next";
            next.classList.add("page-button");

            next.addEventListener("click", () => {
                let currentPage = document.getElementById("searchPageNum").dataset.id;
                if (currentPage == totalPages) {
                    return next.disabled;
                }
                currentPage++;
                paginate(currentPage, students, params);
            });
            searchPaginationBtns.appendChild(next);

        };

        function paginate(currentPage, students, params) {   

            // Pagination

            const start = (currentPage - 1) * studentsPerPage;
            const end = start + studentsPerPage;

            const pageStudents = students.slice(start, end);
            renderStudents(pageStudents, count, params);
            pageNumDiv.innerHTML = `<p data-id=${currentPage} id="searchPageNum">Page ${currentPage}</p>`

        };
        
        

        // ---------------------------- SORT RESULTS ------------------------ //



        searchSortBy.addEventListener("change", sortStudents);
        searchSortOrder.addEventListener("change", sortStudents);
        
        function sortStudents() {
            const sort = searchSortBy.value;
            const order = searchSortOrder.value;
    
            //------- Getting the sort options -----------

            const sortOptions = {
                default: {property: 0, type: "num"},
                name: {property: 1, type: "str"},
                age: {property: 2, type: "num"},
                grade: {property: 3, type: "num"},
                course: {property: 4, type: "str"}
            };

            const selected = sortOptions[sort];

            const property = selected.property;
            const type = selected.type;

        // order multiplier

            const direction = order === "ASC" ? 1: - 1


        // -------------- sort code ----------------

            if (type == "str") {
                const sorted = students.toSorted((a, b) => a[property].localeCompare(b[property]) * direction);
                paginate(1, sorted, params);
                renderPagination(sorted, params);
            }
            else if (type == "num") {
                const sorted = students.toSorted((a, b) => (a[property] - b[property]) * direction);
                paginate(1, sorted, params);    
                renderPagination(sorted, params);
            }
        };
    });

    clearBtn.addEventListener("click", function() {
        searchForm.reset();
    });
    });

};







// ========================================= STUDENT DETAILS PAGE ====================================================== 





const edit = document.getElementById("edit");

if (edit) {

    edit.addEventListener("click", function() {
        const studentId = edit.dataset.id;
        window.location.href = `/update_student/${studentId}`;
    });

}

const del = document.getElementById("delete");


if (del) {

    del.addEventListener("click", function() { 
        modalOverlay.classList.add("active");
    })
   
}







//============================================= UPADATE STUDENT =========================================================





const updateForm = document.getElementById("updateForm");
const updateMessage = document.getElementById("updateMessage");


if (updateForm) {

    const submitBtn = document.querySelector('button[type="submit"]');

    updateForm.addEventListener("submit", function(event) {
        event.preventDefault();
        
        const studentID = document.getElementById("studentID").value;
        const updateFormData = new FormData(updateForm);

        feedbackState(submitBtn, "Updating...");
        
        fetch(`/update_student/${studentID}`, {
            method: "POST",
            body: updateFormData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = `/student/${studentID}`;
                temporaryUIMessage(updateMessage, data.message);
            }
            else {
                const updateInput = document.getElementById(data.field);
                temporaryUIMessage(updateMessage, data.message);
                updateInput.classList.add("errorField");
            };
        })
        .finally(() => {
            feedbackStateFinal(submitBtn, "Save Changes");
        })
    });
 
};





//============================================= DELETE STUDENT =======================================================





const modalOverlay = document.getElementById("deleteModalOverlay");

const killSwitch = document.getElementById("killSwitch");
const source = document.getElementById("source");


if (killSwitch) {
    

    killSwitch.addEventListener("click", function() {
        const studentId = killSwitch.dataset.id

        fetch(`/delete_student/${studentId}`, {
            method: "DELETE",
        })
        .then(response => response.json())
        .then(data => {
            const studentId = data.studentId;
            modalOverlay.classList.remove("active");
            window.location.href = source.value

        });
    });
};

const cancel = document.getElementById("cancel");

if (cancel) {

    cancel.addEventListener("click", function() {
        modalOverlay.classList.remove("active");
    });
};
