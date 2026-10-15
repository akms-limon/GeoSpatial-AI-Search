
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

        if (
            !link ||
            event.ctrlKey ||
            event.metaKey ||
            event.shiftKey ||
            link.target === "_blank"
        ) {
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

    // Semantic search autocomplete
    const searchInput = document.querySelector("#id_query");
    const searchType = document.querySelector("#id_search_type");
    const suggestionsBox = document.querySelector("#search-suggestions");
    const searchForm = searchInput?.closest("form");

    const locationIdInput = document.querySelector("#selected_location_id");
    const propertyIdInput = document.querySelector("#selected_property_id");

    if (searchInput && searchType && suggestionsBox && searchForm) {
        let debounceTimer;
        let requestNumber = 0;

        function clearSelectedIds() {
            if (locationIdInput) {
                locationIdInput.value = "";
            }

            if (propertyIdInput) {
                propertyIdInput.value = "";
            }
        }

        function hideSuggestions() {
            suggestionsBox.hidden = true;
            suggestionsBox.replaceChildren();
        }

        function renderSuggestions(results) {
            suggestionsBox.replaceChildren();

            if (!results.length) {
                hideSuggestions();
                return;
            }

            results.forEach((result) => {
                const option = document.createElement("button");
                option.type = "button";
                option.className = "search-suggestion";
                option.setAttribute("role", "option");

                const label = document.createElement("span");
                label.className = "suggestion-label";
                label.textContent = result.label;

                const subtitle = document.createElement("span");
                subtitle.className = "suggestion-subtitle";
                subtitle.textContent = result.subtitle || "";

                option.append(label, subtitle);

                option.addEventListener("click", () => {
                    searchInput.value = result.label;
                    clearSelectedIds();

                    if (searchType.value === "location" && locationIdInput) {
                        locationIdInput.value = result.id;
                    } else if (
                        searchType.value === "property" &&
                        propertyIdInput
                    ) {
                        propertyIdInput.value = result.id;
                    }

                    hideSuggestions();
                    searchInput.focus();
                });

                suggestionsBox.append(option);
            });

            suggestionsBox.hidden = false;
        }

        searchInput.addEventListener("input", () => {
            clearTimeout(debounceTimer);
            clearSelectedIds();

            const currentRequest = ++requestNumber;
            const query = searchInput.value.trim();

            if (query.length < 2) {
                hideSuggestions();
                return;
            }

            debounceTimer = setTimeout(async () => {
                const params = new URLSearchParams({
                    q: query,
                    type: searchType.value,
                });

                try {
                    const response = await fetch(
                        `/api/search-suggestions/?${params.toString()}`
                    );

                    if (!response.ok) {
                        throw new Error("Suggestion request failed.");
                    }

                    const data = await response.json();

                    if (
                        currentRequest === requestNumber &&
                        searchInput.value.trim() === query
                    ) {
                        renderSuggestions(data.results || []);
                    }
                } catch (error) {
                    if (currentRequest === requestNumber) {
                        hideSuggestions();
                    }

                    console.error(
                        "Could not load search suggestions.",
                        error
                    );
                }
            }, 150);
        });

        searchType.addEventListener("change", () => {
            clearSelectedIds();
            hideSuggestions();

            if (searchInput.value.trim().length >= 2) {
                searchInput.dispatchEvent(new Event("input"));
            }
        });

        searchForm.addEventListener("submit", () => {
            hideSuggestions();
        });

        document.addEventListener("click", (event) => {
            if (!event.target.closest(".autocomplete-wrap")) {
                hideSuggestions();
            }
        });
    }
})();
