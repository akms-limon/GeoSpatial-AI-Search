
(() => {
    async function fetchPage(url) {
        const response = await fetch(url, {
            headers: {
                "X-Requested-With": "XMLHttpRequest",
            },
        });

        if (!response.ok) {
            throw new Error("Could not load the page.");
        }

        const html = await response.text();

        return new DOMParser().parseFromString(html, "text/html");
    }

    function replaceElement(current, incoming) {
        if (current && incoming) {
            current.replaceWith(incoming);
        } else if (current) {
            current.remove();
        }
    }

    async function navigate(url, type, updateHistory = true) {
        const doc = await fetchPage(url);

        if (type === "show-more") {
            const currentGrid = document.querySelector(
                "#featured .property-grid"
            );
            const nextGrid = doc.querySelector(
                "#featured .property-grid"
            );

            if (!currentGrid || !nextGrid) {
                throw new Error("Property grid not found.");
            }

            currentGrid.replaceWith(nextGrid);

            replaceElement(
                document.querySelector("#featured .load-more-wrap"),
                doc.querySelector("#featured .load-more-wrap")
            );
        }

        if (type === "pagination") {
            const currentGrid = document.querySelector(".property-grid");
            const nextGrid = doc.querySelector(".property-grid");

            if (!currentGrid || !nextGrid) {
                throw new Error("Property grid not found.");
            }

            currentGrid.replaceWith(nextGrid);

            replaceElement(
                document.querySelector(".property-pagination"),
                doc.querySelector(".property-pagination")
            );
        }

        if (updateHistory) {
            history.pushState({ type }, "", url);
        }
    }

    document.addEventListener("click", async (event) => {
        const link = event.target.closest(
            '[data-ajax="show-more"], ' +
            '[data-ajax="pagination"] a:not(.is-disabled)'
        );

        if (!link || event.ctrlKey || event.metaKey || event.shiftKey) {
            return;
        }

        if (link.target === "_blank") {
            return;
        }

        event.preventDefault();

        if (link.dataset.loading === "true") {
            return;
        }

        const type = link.dataset.ajax === "show-more"
            ? "show-more"
            : "pagination";

        link.dataset.loading = "true";

        try {
            await navigate(link.href, type);
        } catch (error) {
            window.location.href = link.href;
        }
    });

    window.addEventListener("popstate", async () => {
        const type = document.querySelector("#featured")
            ? "show-more"
            : "pagination";

        try {
            await navigate(window.location.href, type, false);
        } catch (error) {
            window.location.reload();
        }
    });
})();
