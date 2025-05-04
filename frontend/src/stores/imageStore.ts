// stores/imageServices.ts
import { writable } from 'svelte/store';
import * as imageService from '../services/imageService';

export interface EncodedImage {
    filename: string;
    content: string;
    mimeType: string;
}

export interface ImageStoreState {
    images: EncodedImage[];
    likedImages: EncodedImage[];
    currentIndex: number;
    isLoading: boolean;
    isSending: boolean;
    resultMessage: string;
    username: string;
    calibrated: boolean;

}

function createImageStore() {
    const { subscribe, set, update } = writable<ImageStoreState>({
        images: [],
        likedImages: [],
        currentIndex: 0,
        isLoading: true,
        isSending: false,
        resultMessage: '',
        username: '',
        calibrated: false
    });

    const self = {
        subscribe,
        fetchImages: async () => {
            update(state => ({ ...state, isLoading: true, resultMessage: '' }));
            try {
                const data = await imageService.fetchImages();
                if (data.images && data.images.length > 0) {
                    update(state => ({
                        ...state,
                        images: data.images,
                        isLoading: false
                    }));
                } else {
                    update(state => ({
                        ...state,
                        isLoading: false,
                        resultMessage: 'Aucune image disponible'
                    }));
                }
            } catch (error) {
                console.error('Erreur lors de la récupération des images:', error);
                update(state => ({
                    ...state,
                    isLoading: false,
                    resultMessage: 'Erreur lors du chargement des images'
                }));
            }
        },
        fetchCalibrationImages: async () => {
            update(state => ({ ...state, isLoading: true, resultMessage: '' }));
            try {
                const data = await imageService.fetchCalibrationImages();
                if (data.images && data.images.length > 0) {
                    update(state => ({
                        ...state,
                        images: data.images,
                        isLoading: false
                    }));
                } else {
                    update(state => ({
                        ...state,
                        isLoading: false,
                        resultMessage: 'Aucune image de calibration disponible'
                    }));
                }
            } catch (error) {
                console.error('Erreur lors de la récupération des images de calibration:', error);
                update(state => ({
                    ...state,
                    isLoading: false,
                    resultMessage: 'Erreur lors du chargement des images de calibration'
                }));
            }
        },        
        likeImage: async () => {
            let calibrated = false;
            const unsubscribe = self.subscribe(state => { calibrated = state.calibrated; });
            unsubscribe();
        
            update(state => {
                if (state.currentIndex < state.images.length) {
                    return {
                        ...state,
                        likedImages: [...state.likedImages, state.images[state.currentIndex]],
                        currentIndex: state.currentIndex + 1
                    };
                }
                return state;
            });
        
            if (calibrated) {
                await self.sendPreferences(); // envoie auto
                await self.fetchRecommendedImages(); // récup reco auto
            }
        },
        
        skipImage: async () => {
            let calibrated = false;
            const unsubscribe = self.subscribe(state => { calibrated = state.calibrated; });
            unsubscribe();
        
            update(state => {
                if (state.currentIndex < state.images.length) {
                    return {
                        ...state,
                        currentIndex: state.currentIndex + 1
                    };
                }
                return state;
            });
        
            if (calibrated) {
                await self.sendPreferences();
                await self.fetchRecommendedImages();
            }
        },
        
        setUsername: (name: string) => {
            update(state => ({ ...state, username: name }));
          },
          setCalibrated: (status: boolean) => {
            update(state => ({ ...state, calibrated: status }));
        },
        
        
        fetchRecommendedImages: async () => {
            let currentUsername = '';
            const unsubscribe = self.subscribe(state => {
                currentUsername = state.username;
            });
            unsubscribe();
        
            update(state => ({ ...state, isLoading: true, resultMessage: '' }));
            try {
                const data = await imageService.fetchRecommendedImages(currentUsername);
                if (data.recommendation) {
                    update(state => ({
                        ...state,
                        images: [data.recommendation],
                        currentIndex: 0,
                        isLoading: false
                    }));
                } else {
                    update(state => ({
                        ...state,
                        images: [],
                        currentIndex: 0,
                        isLoading: false,
                        resultMessage: 'Aucune image recommandée disponible'
                    }));
                }
            } catch (error) {
                console.error('Erreur lors de la récupération des recommandations:', error);
                update(state => ({
                    ...state,
                    images: [],
                    currentIndex: 0,
                    isLoading: false,
                    resultMessage: 'Erreur lors du chargement des recommandations'
                }));
            }
        }
,        
                
        sendPreferences: async () => {
            let currentLikedImages: string[] = [];
            let currentUsername = '';
            
            update(state => {
              currentLikedImages = state.likedImages.map(img => img.filename);
              currentUsername = state.username;
            
              if (state.likedImages.length === 0) {
                return {
                  ...state,
                  resultMessage: 'Veuillez liker au moins une image'
                };
              }
            
              return {
                ...state,
                isSending: true,
                resultMessage: ''
              };
            });
            
            if (currentLikedImages.length === 0) return;
            
            try {
              const result = await imageService.sendUserPreferences({
                username: currentUsername || 'anonymous',
                likedImages: currentLikedImages
              });
                  
                update(state => ({
                    ...state,
                    resultMessage: result.message || 'Préférences envoyées avec succès',
                    likedImages: [],
                    currentIndex: 0,
                    isSending: false
                }));

            } catch (error) {
                console.error('Erreur lors de l\'envoi des préférences:', error);
                update(state => ({
                    ...state,
                    resultMessage: 'Erreur lors de l\'envoi des préférences',
                    isSending: false
                }));
            }
        },
        resetSelection: () => {
            update(state => ({
                ...state,
                likedImages: [],
                currentIndex: 0,
                resultMessage: ''
            }));
        }
    };

    return self;
}

export const imageStore = createImageStore();
