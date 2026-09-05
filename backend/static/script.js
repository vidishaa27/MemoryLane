// --------------------
// Global Helper Functions & Variables
// --------------------

function escapeHTML(str) {
    if (!str) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function sanitizeHTML(html) {
    if (!html) return "";
    if (typeof DOMPurify !== "undefined") {
        return DOMPurify.sanitize(html);
    }
    return html;
}

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
                <h2>${escapeHTML(magazine.title)}</h2>

                <p>${escapeHTML(magazine.description)}</p>

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

            <a
                href="/create-page"
                class="primary-btn">
                + Add New Page
            </a>

        </div>
    `;

        return;

    }

    const cover =
        document.createElement("div");

    cover.classList.add("cover-page");

    cover.innerHTML = `

        <h1>${escapeHTML(magazineTitle)}</h1>

        <p>${escapeHTML(magazineDescription)}</p>

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

        const cleanTitle = escapeHTML(page.title);
        const cleanContent = sanitizeHTML(page.content);
        const cleanImageUrl = escapeHTML(page.image_url);
        const cleanSpotifyLink = escapeHTML(page.spotify_link);

        pageDiv.innerHTML = `

        <p class="page-number">
            Page ${index + 1}
        </p>

        <h2>${cleanTitle}</h2>

        <img
            src="${cleanImageUrl}"
            class="page-image"
            alt="${cleanTitle}">

        <div class="page-content">
            ${cleanContent}
        </div>

        <a
            href="${cleanSpotifyLink}"
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

            try {

                const response = await fetch(
                    `/page/${page.id}`,
                    {
                        method: "DELETE"
                    }
                );

                const data = await response.json();

                if (!response.ok) {
                    alert(data.message);
                    return;
                }

                initializeMagazine();

            } catch (error) {

                console.error(
                    "Error deleting page:",
                    error
                );

                alert(
                    "Something went wrong while deleting the page."
                );

            }

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

    let quill = null;

    const editorElement =
        document.getElementById("editor");

    if (editorElement) {

        quill = new Quill("#editor", {

            theme: "snow",

            placeholder:
                "Write your memory here...",

            modules: {

                toolbar: [

                    ["bold", "italic", "underline"],

                    [
                        {
                            "header": 1
                        },
                        {
                            "header": 2
                        }
                    ],

                    [
                        {
                            "list": "ordered"
                        },
                        {
                            "list": "bullet"
                        }
                    ],

                    ["link"]

                ]

            }

        });

    }

    const pageTitleInput =
        document.getElementById("pageTitle");

    const previewTitle =
        document.getElementById("previewTitle");


    if (
        pageTitleInput &&
        previewTitle
    ) {

        pageTitleInput.addEventListener(
            "input",
            function () {

                if (pageTitleInput.value.trim() === "") {

                    previewTitle.textContent =
                        "Your Page Title";

                } else {

                    previewTitle.textContent =
                        pageTitleInput.value;

                }

            }
        );

    }

    const previewContent =
        document.getElementById("previewContent");

    if (
        quill &&
        previewContent
    ) {

        quill.on(
            "text-change",
            function () {

                const html =
                    quill.root.innerHTML;

                if (
                    html.trim() === "" ||
                    html === "<p><br></p>"
                ) {

                    previewContent.innerHTML = `
                    <p>
                        Start writing your memory...
                    </p>
                `;

                } else {

                    previewContent.innerHTML =
                        html;

                }

            }
        );

    }

    const pageImageInput =
        document.getElementById("pageImage");

    const previewImage =
        document.getElementById("previewImage");

    if (
        pageImageInput &&
        previewImage
    ) {

        pageImageInput.addEventListener(
            "input",
            function () {

                const imageUrl =
                    pageImageInput.value.trim();

                if (imageUrl === "") {

                    previewImage.style.display =
                        "none";

                    previewImage.src = "";

                } else {

                    previewImage.src =
                        imageUrl;

                    previewImage.style.display =
                        "block";

                }

            }
        );

    }

    const pageSongInput =
        document.getElementById("pageSong");

    const previewSong =
        document.getElementById("previewSong");

    if (
        pageSongInput &&
        previewSong
    ) {

        pageSongInput.addEventListener(
            "input",
            function () {

                const songUrl =
                    pageSongInput.value.trim();

                if (songUrl === "") {

                    previewSong.style.display =
                        "none";

                    previewSong.href = "#";

                } else {

                    previewSong.href =
                        songUrl;

                    previewSong.style.display =
                        "inline-block";

                }

            }
        );

    }

    async function loadEditingPage() {
        const editingPageId =
            localStorage.getItem("editingPageId");

        if (editingPageId && quill) {

            try {

                const response =
                    await fetch(
                        `/page/${editingPageId}`
                    );

                if (!response.ok) {

                    throw new Error(
                        "Failed to load page"
                    );

                }

                const page =
                    await response.json();


                // =================================
                // TITLE
                // =================================

                const pageTitleInput =
                    document.getElementById(
                        "pageTitle"
                    );

                if (pageTitleInput) {

                    pageTitleInput.value =
                        page.title || "";

                }

                if (previewTitle) {

                    previewTitle.textContent =
                        page.title ||
                        "Your Page Title";

                }


                // =================================
                // CONTENT
                // =================================

                quill.root.innerHTML =
                    page.content || "";

                if (previewContent) {

                    previewContent.innerHTML =
                        page.content ||
                        `
                <p>
                    Start writing your memory...
                </p>
                `;

                }


                // =================================
                // IMAGE
                // =================================

                const pageImageInput =
                    document.getElementById(
                        "pageImage"
                    );

                const previewImage =
                    document.getElementById(
                        "previewImage"
                    );

                if (pageImageInput) {

                    pageImageInput.value =
                        page.image_url || "";

                }

                if (
                    previewImage &&
                    page.image_url
                ) {

                    previewImage.src =
                        page.image_url;

                    previewImage.style.display =
                        "block";

                }


                // =================================
                // SPOTIFY
                // =================================

                const pageSongInput =
                    document.getElementById(
                        "pageSong"
                    );

                const previewSong =
                    document.getElementById(
                        "previewSong"
                    );

                if (pageSongInput) {

                    pageSongInput.value =
                        page.spotify_link || "";

                }

                if (
                    previewSong &&
                    page.spotify_link
                ) {

                    previewSong.href =
                        page.spotify_link;

                    previewSong.style.display =
                        "inline-block";

                }


                // =================================
                // UPDATE UI
                // =================================

                document.getElementById(
                    "pageHeading"
                ).textContent =
                    "Edit Page";


                document.getElementById(
                    "pageSubmitBtn"
                ).textContent =
                    "Update Page";


            } catch (error) {

                console.error(
                    "Error loading page:",
                    error
                );

                alert(
                    "Could not load page."
                );

            }

        }
    }

    loadEditingPage();

    pageForm.addEventListener("submit", async function (e) {

        e.preventDefault();

        const pageData = {

            magazine_id: Number(currentMagazineId),

            title:
                document.getElementById("pageTitle").value,

            content:
                quill.root.innerHTML,

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

function openMagazine(magazineId) {

    console.log("Opening magazine:", magazineId);

    localStorage.setItem(
        "currentMagazineId",
        magazineId
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

const registerForm =
    document.getElementById("registerForm");

if (registerForm) {

    registerForm.addEventListener(
        "submit",
        async function (e) {

            e.preventDefault();

            const username =
                document.getElementById("username").value;

            const email =
                document.getElementById("email").value;

            const password =
                document.getElementById("password").value;


            const response =
                await fetch("/register", {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        username: username,

                        email: email,

                        password: password

                    })

                });


            const data =
                await response.json();


            const message =
                document.getElementById(
                    "registerMessage"
                );


            if (response.ok) {

                message.textContent =
                    "Account created successfully! Redirecting to login...";

                setTimeout(function () {

                    window.location.href =
                        "/login";

                }, 1000);

            } else {

                message.textContent =
                    data.message ||
                    "Registration failed.";

            }

        }
    );

}

const loginForm =
    document.getElementById("loginForm");

if (loginForm) {

    loginForm.addEventListener(
        "submit",
        async function (e) {

            e.preventDefault();


            const email =
                document.getElementById("email").value;

            const password =
                document.getElementById("password").value;


            const response =
                await fetch("/login", {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body: JSON.stringify({

                        email: email,

                        password: password

                    })

                });


            const data =
                await response.json();


            const message =
                document.getElementById(
                    "loginMessage"
                );


            if (response.ok) {

                message.textContent =
                    "Login successful! Redirecting...";


                setTimeout(function () {

                    window.location.href =
                        "/dashboard";

                }, 500);


            } else {

                message.textContent =
                    data.message ||
                    "Login failed.";

            }

        }
    );

}

async function updateNavbar() {

    const navLinks =
        document.getElementById("navLinks");

    if (!navLinks) return;

    try {

        const response =
            await fetch("/me");

        const data =
            await response.json();


        if (data.logged_in) {

            navLinks.innerHTML = `

                <a href="/">
                    Home
                </a>

                <a href="/dashboard">
                    Dashboard
                </a>

                <span>
                    Welcome, ${data.user.username}
                </span>

                <button
                    id="logoutBtn"
                    class="logout-btn"
                >
                    Logout
                </button>

            `;


            const logoutBtn =
                document.getElementById(
                    "logoutBtn"
                );


            logoutBtn.addEventListener(
                "click",
                async function () {

                    await fetch(
                        "/logout",
                        {
                            method: "POST"
                        }
                    );

                    window.location.href =
                        "/";

                }
            );

        } else {

            navLinks.innerHTML = `

                <a href="/">
                    Home
                </a>

                <a href="/login">
                    Login
                </a>

                <a href="/register">
                    Register
                </a>

            `;

        }

    } catch (error) {

        console.error(
            "Error checking authentication:",
            error
        );

    }

}

updateNavbar();

const logoutBtn =
    document.getElementById("logoutBtn");

if (logoutBtn) {

    logoutBtn.addEventListener(
        "click",
        async function () {

            const response =
                await fetch("/logout", {

                    method: "POST"

                });


            if (response.ok) {

                window.location.href =
                    "/login";

            }

        }
    );

}

const magazineForm =
    document.getElementById("magazineForm");

if (magazineForm) {

    magazineForm.addEventListener(
        "submit",
        async function (e) {

            e.preventDefault();

            const title =
                document.getElementById(
                    "title"
                ).value.trim();

            const description =
                document.getElementById(
                    "description"
                ).value.trim();

            const cover =
                document.getElementById(
                    "cover"
                ).value.trim();


            if (!title) {

                alert(
                    "Please enter a magazine title."
                );

                return;

            }


            try {

                const response =
                    await fetch(
                        "/magazines",
                        {

                            method: "POST",

                            headers: {

                                "Content-Type":
                                    "application/json"

                            },

                            body:
                                JSON.stringify({

                                    title:
                                        title,

                                    description:
                                        description,

                                    cover:
                                        cover

                                })

                        }
                    );


                const data =
                    await response.json();


                if (!response.ok) {

                    alert(
                        data.message ||
                        "Failed to create magazine."
                    );

                    return;

                }


                console.log(
                    "Magazine created:",
                    data
                );


                // Go to dashboard

                window.location.href =
                    "/dashboard";


            } catch (error) {

                console.error(
                    "Error creating magazine:",
                    error
                );

                alert(
                    "Something went wrong while creating the magazine."
                );

            }

        }
    );

}