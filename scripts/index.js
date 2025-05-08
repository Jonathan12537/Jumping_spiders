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
});
