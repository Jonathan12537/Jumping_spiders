document.addEventListener("DOMContentLoaded", function () {
  // Menu Toggle Functionality
  const menuToggle = document.getElementById("menu-toggle");
  const menuLinks = document.getElementById("menu-links");

  // Initially hide the menu
  menuLinks.classList.add("invisible");

  menuToggle.addEventListener("click", function () {
    // Toggle visibility of the menu
    menuLinks.classList.toggle("invisible");
    menuLinks.classList.toggle("visible");
  });

  // Close menu when clicking outside
  document.addEventListener("click", function (event) {
    if (
      !menuToggle.contains(event.target) &&
      !menuLinks.contains(event.target)
    ) {
      menuLinks.classList.add("invisible");
      menuLinks.classList.remove("visible");
    }
  });

  // Dark Mode Toggle
  const darkModeToggle = document.createElement("button");
  darkModeToggle.textContent = "Toggle Dark Mode";
  darkModeToggle.style.position = "fixed";
  darkModeToggle.style.top = "1rem";
  darkModeToggle.style.left = "1rem";
  darkModeToggle.style.zIndex = "1000";
  darkModeToggle.style.padding = "0.5rem 1rem";
  darkModeToggle.style.backgroundColor = "#3b7c57";
  darkModeToggle.style.color = "white";
  darkModeToggle.style.border = "none";
  darkModeToggle.style.borderRadius = "4px";
  darkModeToggle.style.cursor = "pointer";
  document.body.appendChild(darkModeToggle);

  darkModeToggle.addEventListener("click", function () {
    document.body.classList.toggle("dark-mode");
    // Save preference to localStorage
    const isDarkMode = document.body.classList.contains("dark-mode");
    localStorage.setItem("darkMode", isDarkMode);
  });

  // Check for saved dark mode preference
  if (localStorage.getItem("darkMode") === "true") {
    document.body.classList.add("dark-mode");
  }

  // Spider Data and Image Rendering
  fetch("../data/jumping_spider_list.json")
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
          img.src = `../media/${scientificName.replace(/ /g, "_")}_${i}.jpg`;
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
