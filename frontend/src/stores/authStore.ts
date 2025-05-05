// stores/authStore.ts
import { writable } from 'svelte/store';
import { setAuthCookie, clearAuthCookie } from '../lib/auth';

export interface AuthState {
    isAuthenticated: boolean;
    username: string;
    calibrated: boolean;
}

function createAuthStore() {
    const { subscribe, set, update } = writable<AuthState>({
        isAuthenticated: false,
        username: '',
        calibrated: false
    });

    const updateAuth = (newState: Partial<AuthState>) => {
        update(state => {
            return { ...state, ...newState };
        });
    };

    return {
        subscribe,
        login: (username: string, calibrated: boolean) => {
            updateAuth({
                isAuthenticated: true,
                username,
                calibrated
            });
            setAuthCookie(username, calibrated); 
        },
        logout: () => {
            updateAuth({
                isAuthenticated: false,
                username: '',
                calibrated: false
            });
            clearAuthCookie();
        },
        setCalibrated: (calibrated: boolean) => {
            updateAuth({ calibrated });
            update(state => {
                if (state.username) {
                    setAuthCookie(state.username, calibrated);
                }
                return state;
            });
        }
    };
}

export const authStore = createAuthStore();
