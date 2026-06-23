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

