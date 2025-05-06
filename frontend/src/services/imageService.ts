// services/imageService.ts
export async function fetchImages() {
  const response = await fetch('/list-images');
  return await response.json();
}

export async function fetchCalibrationImages() {
  const response = await fetch('/image-for-calibration');
  return await response.json();
}

export async function fetchRecommendedImages(username: string) {
  const response = await fetch(`/recommend/${username}`);
  return await response.json();
}

export interface UserPreferencesPayload {
  username: string;
  likedImages: string[];
}

export async function sendUserPreferences(payload: UserPreferencesPayload) {
  const response = await fetch('/send-preferences', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
  });

  return await response.json();
}

// Interface pour les données de dislike
interface DislikeData {
  username: string;
  image: string;
}

export async function sendDislikedImage(data: DislikeData) {
  const response = await fetch('/dislike-image', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
  });
 
  if (!response.ok) {
      throw new Error('Échec de l\'envoi de l\'image non aimée');
  }
 
  return await response.json();
}