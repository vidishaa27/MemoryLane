// --------------------
// Global Variables
// --------------------

const pageForm = document.getElementById("pageForm");
const pagesContainer = document.getElementById("pagesContainer");
const magazinesContainer = document.getElementById("magazinesContainer");

const titleDisplay = document.getElementById("magazineTitle");
const descriptionDisplay = document.getElementById("magazineDescription");

const exportBtn = document.getElementById("exportBtn");

const currentMagazineId =
    localStorage.getItem("currentMagazineId");

const editingPageId =
    localStorage.getItem("editingPageId");

let magazineTitle = "";
let magazineDescription = "";

// --------------------
// Page Initializers
// --------------------

if (magazinesContainer) {
    loadDashboard();
}

if (pagesContainer) {
    initializeMagazine();
}

if (pageForm) {
    initializePageForm();
}

if (exportBtn) {
    exportBtn.addEventListener("click", exportMagazine);
}

async function loadDashboard() {

    try {

        const response =
            await fetch("/magazines");

        const data =
            await response.json();

        const magazines =
            data.magazines;

        magazinesContainer.innerHTML = "";

        const statsResponse =
            await fetch("/stats");

        const stats =
            await statsResponse.json();

        document.getElementById("magazineCount").textContent =
            stats.magazines;

        document.getElementById("pageCount").textContent =
            stats.pages;

        document.getElementById("songCount").textContent =
            stats.songs;

        if (magazines.length === 0) {

            magazinesContainer.innerHTML = `
                <div class="page">
                    <h2>📖 Welcome to MemoryLane</h2>

                    <p>
                        You haven't created any magazines yet.
                    </p>
                </div>
            `;

            return;

        }

        magazines.forEach(magazine => {

            const card =
                document.createElement("div");

            card.classList.add("magazine-card");

            card.innerHTML = `
                <h2>${magazine.title}</h2>

                <p>${magazine.description}</p>

                <div class="page-actions">

                    <button
                        class="song-btn"
                        onclick="openMagazine(${magazine.id})">
                        📖 Open
                    </button>

                    <button
                        class="delete-btn"
                        onclick="deleteMagazine(${magazine.id})">
                        🗑 Delete
                    </button>

                </div>
            `;

            magazinesContainer.appendChild(card);

        });

    }

    catch (error) {

        console.error(error);

    }

}

async function initializeMagazine() {

    const response =
        await fetch("/magazines");

    const data =
        await response.json();

    const magazine =
        data.magazines.find(
            m => m.id == currentMagazineId
        );

    if (!magazine) {

        alert("Magazine not found.");

        window.location.href =
            "/dashboard";

        return;

    }

    magazineTitle =
        magazine.title;

    magazineDescription =
        magazine.description;

    const pagesResponse =
        await fetch(
            `/pages/${currentMagazineId}`
        );

    const pagesData =
        await pagesResponse.json();

    renderPages(pagesData.pages);

}

function renderPages(pages) {

    pagesContainer.innerHTML = "";

    if (pages.length === 0) {

        pagesContainer.innerHTML = `
            <div class="page">
                <h2>No Pages Yet</h2>

                <p>
                    Start adding memories.
                </p>
            </div>
        `;

        return;

    }

    const cover =
        document.createElement("div");

    cover.classList.add("cover-page");

    cover.innerHTML = `

        <h1>${magazineTitle}</h1>

        <p>${magazineDescription}</p>

        <a
            href="/create-page"
            class="primary-btn">
            + Add New Page
        </a>

    `;

    pagesContainer.appendChild(cover);

    pages.forEach((page, index) => {

        const pageDiv =
            document.createElement("div");

        pageDiv.classList.add("page");

        pageDiv.innerHTML = `

        <p class="page-number">
            Page ${index + 1}
        </p>

        <h2>${page.title}</h2>

        <img
            src="${page.image_url}"
            class="page-image"
            alt="${page.title}">

        <p>${page.content}</p>

        <a
            href="${page.spotify_link}"
            target="_blank"
            class="song-btn">
            🎵 Listen to Song
        </a>

        <div class="page-actions">

            <button
                class="edit-btn"
                onclick="editPage(${page.id})">
                ✏ Edit
            </button>

            <button
                class="delete-btn"
                data-id="${page.id}">
                🗑 Delete
            </button>

            <button
                class="move-up-btn">
                ⬆ Move Up
            </button>

            <button
                class="move-down-btn">
                ⬇ Move Down
            </button>

        </div>

    `;

        pagesContainer.appendChild(pageDiv);

        const deleteBtn =
            pageDiv.querySelector(".delete-btn");

        deleteBtn.addEventListener("click", async function () {

            const confirmDelete =
                confirm("Delete this page?");

            if (!confirmDelete) return;

            await fetch(
                `/page/${page.id}`,
                {
                    method: "DELETE"
                }
            );

            initializeMagazine();

        });

        const moveUpBtn =
            pageDiv.querySelector(".move-up-btn");

        const moveDownBtn =
            pageDiv.querySelector(".move-down-btn");

        moveUpBtn.addEventListener("click", async function () {

            await fetch(
                `/page/${page.id}/move`,
                {
                    method: "PUT",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        direction: "up"
                    })
                }
            );

            initializeMagazine();

        });

        moveDownBtn.addEventListener("click", async function () {

            await fetch(
                `/page/${page.id}/move`,
                {
                    method: "PUT",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        direction: "down"
                    })
                }
            );

            initializeMagazine();

        });

        if (index === 0) {

            moveUpBtn.disabled = true;

        }

        if (index === pages.length - 1) {

            moveDownBtn.disabled = true;

        }

    });

}

function initializePageForm() {

    if (editingPageId) {

        fetch(`/page/${editingPageId}`)
            .then(res => res.json())
            .then(page => {

                document.getElementById("pageTitle").value =
                    page.title;

                document.getElementById("pageContent").value =
                    page.content;

                document.getElementById("pageImage").value =
                    page.image_url || "";

                document.getElementById("pageSong").value =
                    page.spotify_link || "";

                document.getElementById("pageHeading").textContent =
                    "Edit Page";

                document.getElementById("pageSubmitBtn").textContent =
                    "Save Changes";

            });

    }

    pageForm.addEventListener("submit", async function (e) {

        e.preventDefault();

        const pageData = {

            magazine_id: Number(currentMagazineId),

            title:
                document.getElementById("pageTitle").value,

            content:
                document.getElementById("pageContent").value,

            image_url:
                document.getElementById("pageImage").value,

            spotify_link:
                document.getElementById("pageSong").value

        };

        if (editingPageId) {
            await fetch(

                `/page/${editingPageId}`,

                {

                    method: "PUT",

                    headers: {

                        "Content-Type": "application/json"

                    },

                    body: JSON.stringify(pageData)

                }

            );

        }
        else {
            await fetch(

                "/pages",

                {

                    method: "POST",

                    headers: {

                        "Content-Type": "application/json"

                    },

                    body: JSON.stringify(pageData)

                }

            );
        }

        localStorage.removeItem("editingPageId");

        window.location.href =
            "/magazine";

    });

}

async function exportMagazine() {

    const magazineId =
        currentMagazineId;

    const { jsPDF } = window.jspdf;

    const doc = new jsPDF();

    const magazineResponse =
        await fetch("/magazines");

    const magazineData =
        await magazineResponse.json();

    const magazine =
        magazineData.magazines.find(
            m => m.id == magazineId
        );

    const pagesResponse =
        await fetch(`/pages/${magazineId}`);

    const pagesData =
        await pagesResponse.json();

    const pages =
        pagesData.pages;

    doc.setFontSize(22);
    doc.text("MemoryLane", 20, 20);

    doc.setFontSize(18);
    doc.text(magazine.title, 20, 40);

    doc.setFontSize(12);
    doc.text(magazine.description || "", 20, 50);

    pages.forEach((page, index) => {

        doc.addPage();

        doc.setFontSize(18);
        doc.text(`Page ${index + 1}`, 20, 20);

        doc.setFontSize(16);
        doc.text(page.title, 20, 35);

        const wrapped =
            doc.splitTextToSize(
                page.content,
                170
            );

        doc.setFontSize(12);
        doc.text(wrapped, 20, 50);

        let y =
            50 + wrapped.length * 7;

        if (page.spotify_link) {

            doc.text(
                `Song: ${page.spotify_link}`,
                20,
                y + 10
            );

        }

        if (page.image_url) {

            doc.text(
                `Image: ${page.image_url}`,
                20,
                y + 20
            );

        }

    });

    doc.save("MemoryLane.pdf");

}

function openMagazine(id) {

    localStorage.setItem(
        "currentMagazineId",
        id
    );

    window.location.href =
        "/magazine";

}

function editPage(pageId) {

    localStorage.setItem(
        "editingPageId",
        pageId
    );

    window.location.href =
        "/create-page";

}

async function deleteMagazine(id) {

    const confirmDelete =
        confirm("Delete this magazine?");

    if (!confirmDelete) {

        return;

    }

    await fetch(

        `/magazine/${id}`,

        {

            method: "DELETE"

        }

    );

    loadDashboard();
}