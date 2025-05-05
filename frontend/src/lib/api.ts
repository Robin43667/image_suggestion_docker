// lib/api.ts
interface AuthResponse {
    status: string;
    message: string;
    user?: {
        username: string;
        calibrated: boolean;
    };
}

interface User {
    username: string;
    calibrated: boolean;
}

interface LoginResponse {
    status: string;
    message?: string;
    user?: User;
}

export async function login(username: string, password: string): Promise<LoginResponse> {
    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
            credentials: 'include'
        });

        if (!response.ok) {
            console.error(`Erreur HTTP: ${response.status} - ${response.statusText}`);
            return { status: 'error', message: `Erreur serveur: ${response.statusText}` };
        }

        const data = await response.json();
        console.log('Réponse de connexion:', data);

        if (data.status === 'success') {
            const meResponse = await fetch('/me', {
                method: 'GET',
                credentials: 'include'
            });

            console.log('Réponse de /me:', meResponse); 

            if (meResponse.ok) {
                try {
                    const meData = await meResponse.json();
                    console.log('Données /me reçues:', meData); 

                    if (meData.status === 'success' && meData.user) {
                        return {
                            status: 'success',
                            user: meData.user
                        };
                    } else {
                        console.warn('/me ne contient pas d\'utilisateur:', meData);
                    }
                } catch (err) {
                    console.error('Erreur lors du parsing de /me:', err);
                }
            } else {
                console.warn('Erreur HTTP lors de /me:', meResponse.statusText);
            }

            return {
                status: 'success',
                user: {
                    username,
                    calibrated: false
                }
            };
        }

        return {
            status: 'error',
            message: data.message || 'Identifiants incorrects'
        };

    } catch (error) {
        console.error('Erreur lors de la connexion:', error);
        return {
            status: 'error',
            message: 'Erreur de connexion au serveur'
        };
    }
}



export async function register(username: string, password: string): Promise<AuthResponse> {
    try {
        const response = await fetch(`/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password }),
            credentials: 'include'
        });
       
        if (!response.ok) {
            console.error(`Erreur HTTP: ${response.status} - ${response.statusText}`);
            throw new Error(`Erreur serveur: ${response.statusText}`);
        }
       
        return await response.json();
    } catch (error) {
        console.error('Erreur lors de l\'inscription:', error);
        throw error;
    }
}