import { writable, get } from "svelte/store";
import { IP } from "$lib/IP.js"

//Menu Stuff
export const menuOpen = writable(false);

//scope stuff(info store in project route)
export const ipsAllowed = writable([]);
export const ipsDisallowed = writable([]);


// Function to send store data to the backend
export const sendIPSToBackend = async () => {
  const disallowedData = get(ipsDisallowed).map(ipInstance => ipInstance.ip);
  const payload = {
      ips: disallowedData.join(","), // Comma-separated string of disallowed IPs
  };

  // Log payload to confirm data being sent
  console.log('Sending disallowed IPs to backend:', payload);

  try {
      const response = await fetch('/flask-api/get-ips', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify(payload)
      });

      const result = await response.json();
      console.log('Data sent to backend successfully:', result);
  } catch (error) {
      console.error('Error sending data to backend:', error);
  }
};
export function updateAllowedAndDisallowedIPs(allIps, selectedIps) {
  // Filter to find selected and disallowed IPs
  const selectedIpInstances = allIps
      .filter(ip => selectedIps.includes(ip.ip))
      .map(ip => new IP(ip));

  const disallowedIpInstances = allIps
      .filter(ip => !selectedIps.includes(ip.ip))
      .map(ip => new IP(ip));

  // Update the stores
  ipsAllowed.set(selectedIpInstances);
  ipsDisallowed.set(disallowedIpInstances);
}
  //should be ran once a nessus file is uploaded
  export async function getIPsFromBackend(fileName) {
    const ipData = get(ipsDisallowed).map(ipInstance => ipInstance.ip);  // Assuming IP has an `ip` property
    const payload = {
        project_id: 1, // Or dynamically assign this based on the project
        ips: ipData.join(","), // Convert array to comma-separated string
        exploits: ["SQL Injection", "DDOS Attack"] // Example exploit types
    };
    try {
        const response = await fetch('/flask-api/get-ips', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        const result = await response.json();
        console.log('Data sent to backend:', result);
    } catch (error) {
        console.error('Error sending data:', error);
    }
};

  function addIPstoStore(data) {
    const ipInstances = data.map(ipAddress => new IP(ipAddress)); // Create IP instances
    console.log(ipInstances)
    ipsDisallowed.set(ipInstances); // Update the store with IP instances
}

// DARK MODE LOGIC
// Load dark mode preference from localStorage, defaulting to 'light' mode
const savedTheme = (typeof window !== 'undefined' && localStorage.getItem("color-theme")) || "light";

// Create a writable store for dark mode state based on saved preference
export const darkMode = writable(savedTheme === "dark");

// Subscribe to darkMode store to watch for changes and sync with localStorage
darkMode.subscribe((value) => {
  if (typeof window !== "undefined") {
    localStorage.setItem("color-theme", value ? "dark" : "light");
    document.documentElement.classList.toggle("dark", value);
  }
});

// Colorblind Mode Logic
const savedColorMode = (typeof window !== 'undefined' && localStorage.getItem("colorblind-mode")) || "Normal";
export const colorblindMode = writable(savedColorMode);

colorblindMode.subscribe((value) => {
  if (typeof window !== 'undefined') {
    localStorage.setItem("colorblind-mode", value);

    // Apply the appropriate colorblind filter
    const root = document.documentElement;
    root.style.filter = 'none';
    if (value === 'Protanopia') {
      root.style.filter = 'url(#protanopia-filter)';
    } else if (value === 'Deuteranopia') {
      root.style.filter = 'url(#deuteranopia-filter)';
    }
  }
});