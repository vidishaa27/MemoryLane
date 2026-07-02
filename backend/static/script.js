console.log("script.js loaded");//debugging line
const form = document.getElementById('magazineForm');
console.log("1");//debugging line
if (form) {
    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const title = document.getElementById('title').value;
        const description = document.getElementById('description').value;
        const cover = document.getElementById('cover').value;

        const response = await fetch(
            "/magazines",
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

console.log("2");//debugging line

const titleDisplay = document.getElementById('magazineTitle');

const descriptionDisplay = document.getElementById('magazineDescription');

const currentMagazineId =
    localStorage.getItem("currentMagazineId");

console.log("3");//debugging line

if (titleDisplay) {

    fetch("/magazines")
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

console.log("4");//debugging line
const pageForm =
    document.getElementById("pageForm");

const editingPageId =
    localStorage.getItem("editingPageId");
console.log("5");//debugging line
if (pageForm) {

    if (editingPageId !== null) {

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
    pageForm.addEventListener("submit", function (e) {
        e.preventDefault();

        const pageTitle = document.getElementById("pageTitle").value;
        const pageContent = document.getElementById("pageContent").value;
        const pageImage = document.getElementById("pageImage").value;
        const pageSong = document.getElementById("pageSong").value;

        const magazineId =
    currentMagazineId || 1;

        const pageData = {
            magazine_id: Number(magazineId),
            title: pageTitle,
            content: pageContent,
            image_url: pageImage,
            spotify_link: pageSong
        };
        const url = editingPageId !== null
            ? `/pages/${editingPageId}`
            : "/pages";

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

                window.location.href = "/magazine";

            })
            .catch(err => {

                console.error("Error saving page:", err);

            });
    });
}

console.log("6");//debugging line
const pagesContainer =
    document.getElementById("pagesContainer");

let magazineTitle = "";
let magazineDescription = "";
console.log("7");//debugging line
async function loadMagazine() {

    const response =
        await fetch("/magazines")

    const data =
        await response.json();

    const magazine =
        data.magazines.find(
            m => m.id == currentMagazineId
        );

    if (!magazine) {

        alert("Magazine not found.");

        window.location.href = "/dashboard";

        return;

    }

    magazineTitle =
        magazine.title;

    magazineDescription =
        magazine.description;

}
console.log("8");//debugging line
async function deleteMagazine(id) {

    const confirmDelete =
        confirm("Delete this magazine?");

    if (!confirmDelete) return;

    await fetch(
        `/magazines/${id}`,
        {
            method: "DELETE"
        }
    );

    loadDashboard();

}
console.log("9");//debugging line
async function loadPages() {

    const response =
        await fetch(
            `/pages/${currentMagazineId}`
        );

    const data =
        await response.json();

    renderPages(data.pages);

}
console.log("10");//debugging line
if (pagesContainer) {

    initializeMagazine();

}
console.log("11");//debugging line
async function initializeMagazine() {

    await loadMagazine();

    await loadPages();

}
console.log("12");//debugging line
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
            console.log("13");//debugging line
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

                loadPages();

            });
            console.log("14");//debugging line
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
                `/page/${page.id}`,
                {
                    method: "DELETE"
                }
            );
            loadPages();

        });

        if (pagesContainer) {

            const magazineId =
    currentMagazineId || 1;

            fetch(`/pages/${magazineId}`)
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
                "/create-page";

        }

        const magazinesContainer =
            document.getElementById("magazinesContainer");

        console.log("About to call loadDashboard");
        async function loadDashboard() {

            console.log("loadDashboard started");//debugging line

            const response =
                await fetch("/magazines");

            const data =
                await response.json();

            const magazines =
                data.magazines;

                console.log("Magazines:", magazines);

            magazinesContainer.innerHTML = "";

            const statsResponse =
                await fetch("/stats");

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

            console.log("Rendering cards..."); //debugging line

            magazines.forEach((magazine) => {

                console.log(magazine); //debugging line

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

        if (magazinesContainer) {

            loadDashboard();

            console.log(magazinesContainer);//debugging line
        }

        const exportBtn = document.getElementById("exportBtn");

        if (exportBtn) {

            exportBtn.addEventListener("click", exportMagazine);

        }
        console.log("13");//debugging line
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
                await fetch(
                    `/pages/${magazineId}`
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

        
    }
}