const form = document.getElementById('magazineForm');

if (form) {
    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const title = document.getElementById('title').value;
        const description = document.getElementById('description').value;
        const cover = document.getElementById('cover').value;

        localStorage.setItem('magazineTitle', title);
        localStorage.setItem('magazineDescription', description);
        localStorage.setItem('magazineCover', cover);

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

const pageForm =
    document.getElementById("pageForm");

if (pageForm) {

    pageForm.addEventListener("submit", function (e) {

        e.preventDefault();

        const pageTitle =
            document.getElementById("pageTitle").value;

        const pageContent =
            document.getElementById("pageContent").value;

        let pages =
            JSON.parse(localStorage.getItem("pages")) || [];

        pages.push({
            title: pageTitle,
            content: pageContent
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

    pages.forEach(function(page) {

        const pageDiv =
            document.createElement("div");

        pageDiv.classList.add("card");

        pageDiv.innerHTML = `
            <h2>${page.title}</h2>
            <p>${page.content}</p>
        `;

        pagesContainer.appendChild(pageDiv);

    });

}

