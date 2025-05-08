document.addEventListener("DOMContentLoaded", function () {
  // Spider Data and Image Rendering
  fetch("data/jumping_spider_list.json")
    .then((response) => response.json())
    .then((data) => {
      data.sort((a, b) => (b.sightings ?? 0) - (a.sightings ?? 0));

      const container = document.getElementById("spiders");

      data.forEach((spider) => {
        const scientificName =
          spider.scientific_name.charAt(0).toLowerCase() +
          spider.scientific_name.slice(1);
        const regularName =
          spider.regular_name && spider.regular_name.trim() !== ""
            ? spider.regular_name
            : "No common name";
        const sightings = spider.sightings ?? 0;

        const card = document.createElement("div");
        card.className = "spider-card";

        const header = document.createElement("h2");
        header.textContent = `${spider.scientific_name} - ${regularName} (${sightings} sightings)`;
        card.appendChild(header);

        const imageGrid = document.createElement("div");
        imageGrid.className = "image-grid";

        for (let i = 1; i <= 4; i++) {
          const img = document.createElement("img");
          img.src = `media/${scientificName.replace(/ /g, "_")}_${i}.jpg`;
          img.alt = regularName;
          img.loading = "lazy"; // Add lazy loading
          img.onerror = () => {
            img.style.display = "none"; // Hide broken images
          };
          imageGrid.appendChild(img);
        }

        card.appendChild(imageGrid);
        container.appendChild(card);
      });
    })
    .catch((err) => {
      console.error("Failed to load spider data:", err);
      const container = document.getElementById("spiders");
      container.innerHTML =
        "<p>Error loading spider data. Please try again later.</p>";
    });
});
