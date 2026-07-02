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