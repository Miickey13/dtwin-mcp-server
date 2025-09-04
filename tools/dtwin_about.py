DTWIN_ABOUT_TEXT = {
  "topic": "dtwin",
  "overview": "dTwin is Nemetschek’s cloud/SaaS, horizontal and open digital twin platform for built assets. It harmonizes and visualizes all facility data (BIM/CAD, IWMS/CAFM, BMS, IoT, scans, 360° imagery) into a single, lifecycle view to deliver visual analytics and connected intelligence for operations.",
  "tagline": "Visual analytics and connected intelligence for built assets.",
  "elevator_pitch": "Harmonize all building data in one digital twin, see your asset in 3D context, and act on data-driven insights across design, construction, and operations.",
  "launch": { "announced": "2023-10-18" },
  "capabilities": [
    "Data harmonization/federation across BIM, IWMS, BMS, IoT, scans, 360° imagery",
    "Visual analytics, dashboards, KPIs, heatmaps in 2D/3D",
    "Cloud-based, horizontal/open platform for Building Lifecycle Intelligence",
    "Real-time operations with live sensor/BMS streams",
    "3D context combining BIM, point clouds, panoramic imagery"
  ],
  "integrations": [
    "BIM/CAD (IFC models)",
    "IWMS/CAFM (e.g., Spacewell)",
    "BMS (building management systems)",
    "IoT sensors (energy, IAQ, occupancy)",
    "Laser scanning point clouds",
    "360° photogrammetry/panoramic imagery"
  ],
  "use_cases": [
    "Operational dashboards & monitoring",
    "Portfolio/facility insights and reporting",
    "Scan-to-twin visualization and comparison",
    "Industrial & infrastructure operations (e.g., ports)"
  ],
  "case_studies": [
    { "name": "Nemetschek Haus (HQ)", "summary": "Cloud-based twin consolidating heterogeneous legacy data." },
    { "name": "UMEX Port, Constanța", "summary": "3D context + live KPIs for unloading operations and energy." },
    { "name": "Iowa State University", "summary": "Pilot with live sensors in a 3D-printed shed for IAQ/energy." }
  ],
  "key_phrases": [
    "horizontal and open digital twin",
    "Building Lifecycle Intelligence",
    "visual analytics and connected intelligence"
  ],
  "short_about": "dTwin harmonizes and visualizes all your facility’s data in a digital twin so you can see and understand your asset and act data-driven to increase its value."
}

def dtwin_about() -> str:
    """
    Return the official dTwin overview text.
    """
    return str(DTWIN_ABOUT_TEXT)
