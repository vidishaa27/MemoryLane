const form = document.getElementById('magazineForm');

if (form) {
    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const title = document.getElementById('title').value;
        const description = document.getElementById('description').value;
        const cover = document.getElementById('cover').value;
        const theme = document.getElementById('magazineTheme').value;

        localStorage.setItem('magazineTitle', title);

        localStorage.setItem('magazineDescription', description);
        localStorage.setItem('magazineCover', cover);
        localStorage.setItem('magazineTheme', theme);

        // Redirect to the magazine page
        window.location.href = 'magazine.html';
    });
}

const titleDisplay = document.getElementById('magazineTitle');

const descriptionDisplay = document.getElementById('magazineDescription');

if (titleDisplay) {
    titleDisplay.textContent = localStorage.getItem('magazineTitle');

    descriptionDisplay.textContent = localStorage.getItem('magazineDescription');
}

const theme = localStorage.getItem("magazineTheme");

console.log(theme);

if (theme) {
    document.body.classList.add(`${theme}-theme`);
}

const pageForm =
    document.getElementById("pageForm");

const editingIndex =
    localStorage.getItem("editingPage");

if (pageForm) {

    if (editingIndex !== null) {

        const pages =
            JSON.parse(localStorage.getItem("pages")) || [];

        const page =
            pages[editingIndex];

        if (page) {

            document.getElementById("pageTitle").value =
                page.title;

            document.getElementById("pageContent").value =
                page.content;

            document.getElementById("pageImage").value =
                page.image;

            document.getElementById("pageSong").value =
                page.song;

            document.getElementById("pageHeading").textContent =
                "Edit Page";

            document.getElementById("pageSubmitBtn").textContent =
                "Save Changes";

        }
    }

    pageForm.addEventListener("submit", function (e) {

        e.preventDefault();

        const pageTitle =
            document.getElementById("pageTitle").value;

        const pageContent =
            document.getElementById("pageContent").value;

        const pageImage =
            document.getElementById("pageImage").value;

        const pageSong =
            document.getElementById("pageSong").value;

        let pages =
            JSON.parse(localStorage.getItem("pages")) || [];

        if (editingIndex !== null) {

            pages[editingIndex] = {
                title: pageTitle,
                content: pageContent,
                image: pageImage,
                song: pageSong
            };

        } else {

            pages.push({
                title: pageTitle,
                content: pageContent,
                image: pageImage,
                song: pageSong
            });

        }

        localStorage.setItem(
            "pages",
            JSON.stringify(pages)
        );

        localStorage.removeItem("editingPage");

        window.location.href = "magazine.html";

    });

}

const pagesContainer =
    document.getElementById("pagesContainer");

if (pagesContainer) {

    let pages =
        JSON.parse(localStorage.getItem("pages")) || [];

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

        const magazineTitle =
            localStorage.getItem("magazineTitle") || "Untitled Magazine";

        const magazineDescription =
            localStorage.getItem("magazineDescription") || "";

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
        src="${page.image}"
        alt="${page.title}"
        class="page-image">

    <p>${page.content}</p>

    <a href="${page.song}"
        target="_blank"
        class="song-btn">
        🎵 Listen to Song
    </a>

    <div class="page-actions">

        <button
            class="edit-btn"
            onclick="editPage(${index})">
            ✏️ Edit
        </button>

        <button
            class="delete-btn"
            data-index="${index}">
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

            moveUpBtn.addEventListener("click", function () {

                if (index === 0) return;

                const temp = pages[index];

                pages[index] = pages[index - 1];

                pages[index - 1] = temp;

                localStorage.setItem(
                    "pages",
                    JSON.stringify(pages)
                );

                location.reload();

            });

            moveDownBtn.addEventListener("click", function () {

                if (index === pages.length - 1) return;

                const temp = pages[index];

                pages[index] = pages[index + 1];

                pages[index + 1] = temp;

                localStorage.setItem(
                    "pages",
                    JSON.stringify(pages)
                );

                location.reload();

            });

            if (index === 0) {
                moveUpBtn.disabled = true;
            }

            if (index === pages.length - 1) {
                moveDownBtn.disabled = true;
            }

        });

        document.querySelectorAll(".delete-btn").forEach(button => {

            button.addEventListener("click", () => {

                const confirmDelete =
                    confirm("Delete this page?");

                if (!confirmDelete) return;

                const index = button.dataset.index;

                let pages =
                    JSON.parse(localStorage.getItem("pages")) || [];

                pages.splice(index, 1);

                localStorage.setItem(
                    "pages",
                    JSON.stringify(pages)
                );

                location.reload();

            });

        });

    }
}

function editPage(index) {

    localStorage.setItem("editingPage", index);

    window.location.href = "create-page.html";

}

const magazinesContainer =
    document.getElementById("magazinesContainer");

if (magazinesContainer) {

    const title =
        localStorage.getItem("magazineTitle");

    const description =
        localStorage.getItem("magazineDescription");

    const theme =
        localStorage.getItem("magazineTheme");

    const pages =
        JSON.parse(localStorage.getItem("pages")) || [];


    document.getElementById("magazineCount").textContent =
        title ? 1 : 0;

    document.getElementById("pageCount").textContent =
        pages.length;

    const songCount =
        pages.filter(page => page.song && page.song.trim() !== "").length;

    document.getElementById("songCount").textContent =
        songCount;

    if (!title) {

        magazinesContainer.innerHTML = `
            <div class="page">
                <h2>📖 Welcome to MemoryLane</h2>
                <p>
                    You haven't created any magazines yet.
                </p>
            </div>
        `;

    } else {

        const card =
            document.createElement("div");

        card.classList.add("magazine-card");

        card.innerHTML = `
            <h2>${title}</h2>

            <p>${description}</p>

            <p><strong>Theme:</strong> ${theme}</p>

            <p><strong>Pages:</strong> ${pages.length}</p>

            <div class="page-actions">

                <button
                    onclick="window.location.href='magazine.html'"
                    class="song-btn">
                    📖 Open
                </button>

            </div>
        `;

        magazinesContainer.appendChild(card);

    }

}
const exportBtn = document.getElementById("exportBtn");

if (exportBtn) {

    exportBtn.addEventListener("click", exportMagazine);

}

function exportMagazine() {

    const { jsPDF } = window.jspdf;

    const doc = new jsPDF();

    const title =
        localStorage.getItem("magazineTitle") || "Untitled Magazine";

    const description =
        localStorage.getItem("magazineDescription") || "";

    const pages =
        JSON.parse(localStorage.getItem("pages")) || [];

    doc.setFontSize(22);
    doc.text("MemoryLane", 20, 20);

    doc.setFontSize(18);
    doc.text(title, 20, 40);

    doc.setFontSize(12);
    doc.text(description, 20, 50);

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

        if (page.song) {

            doc.text("Song:", 20, 70);
            doc.text(page.song, 40, 70);

        }

        if (page.image) {

            doc.text("Image:", 20, 70);
            doc.text(page.image, 40, 70);

        }

    });

    doc.save("MemoryLane.pdf");

}