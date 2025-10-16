
const API_URL = "https://ucc-campus-hostel-backend.onrender.com/hostels";

async function fetchHostels() {
  const res = await fetch(API_URL);
  const data = await res.json();
  const list = document.getElementById("hostelList");
  list.innerHTML = "";

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
}

fetch("https://ucc-campus-hostel-backend.onrender.com/login", {...})

fetchHostels();



