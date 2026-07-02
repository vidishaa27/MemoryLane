const form = document.getElementById('magazineForm');

if (form) {
    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const title = document.getElementById('title').value;
        const description = document.getElementById('description').value;
        const cover = document.getElementById('cover').value;
        const theme = document.getElementById('magazineTheme').value;

        const response = await fetch(
            "http://127.0.0.1:5000/magazines",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    title,
                    description
                })
            }
        );

        const result = await response.json();

        console.log(result);
    });
}

const titleDisplay = document.getElementById('magazineTitle');

const descriptionDisplay = document.getElementById('magazineDescription');

const currentMagazineId =
    localStorage.getItem("currentMagazineId");

if (titleDisplay) {

    fetch("http://127.0.0.1:5000/magazines")
        .then(res => res.json())
        .then(data => {

            const magazine = data.magazines.find(
                m => m.id == currentMagazineId
            );

            if (!magazine) return;

            titleDisplay.textContent =
                magazine.title;

            descriptionDisplay.textContent =
                magazine.description;

        });

}

if (theme) {
    document.body.classList.add(`${theme}-theme`);
}

const pageForm =
    document.getElementById("pageForm");

const editingPageId =
    localStorage.getItem("editingPageId");

if (pageForm) {

    if (editingPageId !== null) {

        fetch(`http://127.0.0.1:5000/page/${editingPageId}`)
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

    pageForm.addEventListener("submit", function (e) {
        e.preventDefault();

        const pageTitle = document.getElementById("pageTitle").value;
        const pageContent = document.getElementById("pageContent").value;
        const pageImage = document.getElementById("pageImage").value;
        const pageSong = document.getElementById("pageSong").value;

        const currentMagazineId =
            localStorage.getItem("currentMagazineId") || 1;

        const pageData = {
            magazine_id: Number(currentMagazineId),
            page_number: 0,
            title: pageTitle,
            content: pageContent,
            image_url: pageImage,
            spotify_link: pageSong
        };

        const url = editingPageId !== null
            ? `http://127.0.0.1:5000/pages/${editingPageId}`
            : "http://127.0.0.1:5000/pages";

        const method = editingPageId !== null
            ? "PUT"
            : "POST";

        fetch(url, {
            method: method,
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(pageData)
        })

            .then(res => res.json())
            .then(data => {

                console.log("Page saved:", data);

                localStorage.removeItem("editingPageId");

                window.location.href = "magazine.html";

            })
            .catch(err => {

                console.error("Error saving page:", err);

            });
    });
}

const pagesContainer =
    document.getElementById("pagesContainer");

const currentMagazineId =
    localStorage.getItem("currentMagazineId");

let magazineTitle = "";
let magazineDescription = "";

async function loadMagazine() {

    const response =
        await fetch("http://127.0.0.1:5000/magazines");

    const data =
        await response.json();

    const magazine =
        data.magazines.find(
            m => m.id == currentMagazineId
        );

    if (!magazine) {

        alert("Magazine not found.");

        window.location.href = "dashboard.html";

        return;

    }

    magazineTitle =
        magazine.title;

    magazineDescription =
        magazine.description;

}

async function loadPages() {

    const response =
        await fetch(
            `http://127.0.0.1:5000/pages/${currentMagazineId}`
        );

    const data =
        await response.json();

    renderPages(data.pages);

}

if (pagesContainer) {

    initializeMagazine();

}

async function initializeMagazine() {

    await loadMagazine();

    await loadPages();

}

function renderPages(pages) {

    pagesContainer.innerHTML = "";

    if (pages.length === 0) {

        pagesContainer.innerHTML = `
        <div class="page">
            <h2>No Pages Yet</h2>
            <p>
                Start adding memories to your magazine.
            </p>
        </div>
    `;

    } else {
        const cover =
            document.createElement("div");

        cover.classList.add("cover-page");

        cover.innerHTML = `
        <h1>${magazineTitle}</h1>

        <p>${magazineDescription}</p>

        <a
            href="create-page.html"
            class="primary-btn">
            + Add New Page
        </a>
`;

        pagesContainer.appendChild(cover);

        pages.forEach(function (page, index) {

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
        alt="${page.title}"
        class="page-image">

    <p>${page.content}</p>

    <a href="${page.spotify_link}"
        target="_blank"
        class="song-btn">
        🎵 Listen to Song
    </a>

    <div class="page-actions">

        <button
            class="edit-btn"
            onclick="editPage(${page.id})"
            >
            ✏️ Edit
        </button>

        <button
            class="delete-btn"
            data-id="${page.id}"
            >
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

            const moveUpBtn =
                pageDiv.querySelector(".move-up-btn");

            const moveDownBtn =
                pageDiv.querySelector(".move-down-btn");

            moveUpBtn.addEventListener("click", async function () {

                await fetch(
                    `http://127.0.0.1:5000/page/${page.id}/move`,
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

                loadPages();

            });

            moveDownBtn.addEventListener("click", async function () {

                await fetch(
                    `http://127.0.0.1:5000/page/${page.id}/move`,
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

                loadPages();

            });


            if (index === 0) {
                moveUpBtn.disabled = true;
            }

            if (index === pages.length - 1) {
                moveDownBtn.disabled = true;
            }

        });

        const deleteBtn =
            pageDiv.querySelector(".delete-btn");

        deleteBtn.addEventListener("click", async function () {

            const confirmDelete =
                confirm("Delete this page?");

            if (!confirmDelete) return;

            await fetch(
                `http://127.0.0.1:5000/page/${page.id}`,
                {
                    method: "DELETE"
                }
            );

            loadPages();

        });

        if (pagesContainer) {

            const currentMagazineId =
                localStorage.getItem("currentMagazineId") || 1;

            fetch(`http://127.0.0.1:5000/pages/${currentMagazineId}`)
                .then(response => response.json())
                .then(data => {

                    renderPages(data.pages);

                })
                .catch(error => {

                    console.error("Error loading pages:", error);

                });
        }

        function editPage(pageId) {

            localStorage.setItem(
                "editingPageId",
                pageId
            );

            window.location.href =
                "create-page.html";

        }

        const magazinesContainer =
            document.getElementById("magazinesContainer");

        async function loadDashboard() {

            const response =
                await fetch("http://127.0.0.1:5000/magazines");

            const data =
                await response.json();

            const magazines =
                data.magazines;

            const statsResponse =
                await fetch("http://127.0.0.1:5000/stats");

            const stats =
                await statsResponse.json();

            // Empty state
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

            document.getElementById("magazineCount").textContent =
                stats.magazines;

            document.getElementById("pageCount").textContent =
                stats.pages;

            document.getElementById("songCount").textContent =
                stats.songs;

            magazines.forEach((magazine) => {

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

        </div>
    `;

                magazinesContainer.appendChild(card);

            });
        }

        if (magazinesContainer) {

            loadDashboard();

        }

        const exportBtn = document.getElementById("exportBtn");

        if (exportBtn) {

            exportBtn.addEventListener("click", exportMagazine);

        }

        async function exportMagazine() {

            const currentMagazineId =
                localStorage.getItem("currentMagazineId");

            const { jsPDF } = window.jspdf;

            const doc = new jsPDF();

            const magazineResponse =
                await fetch("http://127.0.0.1:5000/magazines");

            const magazineData =
                await magazineResponse.json();

            const magazine =
                magazineData.magazines.find(
                    m => m.id == currentMagazineId
                );

            const pagesResponse =
                await fetch(
                    `http://127.0.0.1:5000/pages/${currentMagazineId}`
                );

            const pagesData =
                await pagesResponse.json();

            const pages =
                pagesData.pages;

            doc.setFontSize(22);
            doc.text("MemoryLane", 20, 20);

            doc.setFontSize(18);
            doc.text(magazine.title, 20, 40);

            doc.setFontSize(12);
            doc.text(magazine.description, 20, 50);

            pages.forEach((page, index) => {

                doc.addPage();

                doc.setFontSize(20);

                doc.text(
                    `Page ${index + 1}`,
                    20,
                    20
                );

                doc.line(
                    20,
                    25,
                    190,
                    25
                );

                doc.setFontSize(16);
                doc.text(page.title, 20, 35);

                doc.setFontSize(12);
                const wrappedContent =
                    doc.splitTextToSize(page.content, 170);

                doc.text(wrappedContent, 20, 50);

                if (page.spotify_link) {

                    doc.text("Song:", 20, 70);
                    doc.text(page.spotify_link, 40, 70);

                }

                if (page.image_url) {

                    doc.text("Image:", 20, 70);
                    doc.text(page.image_url, 40, 70);

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
                "magazine.html";

        }