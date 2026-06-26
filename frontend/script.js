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

if (pageForm) {

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

        pages.push({
            title: pageTitle,
            content: pageContent,
            image: pageImage,
            song: pageSong
        });

        localStorage.setItem(
            "pages",
            JSON.stringify(pages)
        );

        alert("Page Added!");

        pageForm.reset();

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

    </div>
`;

            pagesContainer.appendChild(pageDiv);

        });

        document.querySelectorAll(".delete-btn").forEach(button => {

            button.addEventListener("click", () => {

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