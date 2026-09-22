const API_URL = "http://localhost:8000/";

export async function getSignalPosition() {
  const response = await fetch(API_URL+"signal");

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }

  const data = await response.json();

  if (
    !data.estimated ||
    typeof data.estimated.x !== "number" ||
    typeof data.estimated.y !== "number"
  ) {
    throw new Error("Invalid position data received from API");
  }

  return data;
}

export async function getFloorplanData() {
  const response = await fetch(API_URL+"misc");

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }

  const data = await response.json();

  if (
    !data.Floorplan_Path ||
    !data.Extent ||
    !Array.isArray(data.Anchors)
  ) {
    throw new Error("Invalid floorplan data received from API");
  }

  return data;
}

