
// Backend API URL
const API_URL = "https://ucc-campus-hostel-backend.onrender.com/hostels";

// Fetch all hostels from backend
async function fetchHostels() {
  try {
    const res = await fetch(API_URL);
    if (!res.ok) throw new Error("Failed to fetch hostels");

    const data = await res.json();
    const list = document.getElementById("hostelList");
    list.innerHTML = "";

    // Loop through and display hostels
    data.forEach(hostel => {
      const card = document.createElement("div");
      card.className = "hostel-card";
      card.innerHTML = `
        <h2>${hostel.name}</h2>
        <div class="images">
          <img src="https://ucc-campus-hostel-backend.onrender.com/${hostel.image1}" alt="${hostel.name} image 1">
          <img src="https://ucc-campus-hostel-backend.onrender.com/${hostel.image2}" alt="${hostel.name} image 2">
        </div>
        <p><strong>Owner Contact:</strong> ${hostel.contact}</p>
      `;
      list.appendChild(card);
    });
  } catch (error) {
    console.error("Error loading hostels:", error);
    const list = document.getElementById("hostelList");
    list.innerHTML = `<p style="color:red; text-align:center;">Unable to load hostels. Please try again later.</p>`;
  }
}

// Search/filter function
function filterHostels() {
  const query = document.getElementById("searchBox").value.toLowerCase();
  const hostels = document.getElementsByClassName("hostel-card");

  for (let i = 0; i < hostels.length; i++) {
    const name = hostels[i].getElementsByTagName("h2")[0].innerText.toLowerCase();
    hostels[i].style.display = name.includes(query) ? "block" : "none";
  }
}

// Run when page loads
window.onload = fetchHostels;


