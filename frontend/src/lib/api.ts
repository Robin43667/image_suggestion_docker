// lib/api.ts

interface AuthResponse {
	status: string;
	message: string;
	user?: {
		username: string;
		calibrated: boolean;
	};
}


export async function login(username: string, password: string): Promise<AuthResponse> {
	try {
		const response = await fetch(`/login`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({ username, password })
		});
		
		return await response.json();
	} catch (error) {
		console.error('Erreur lors de la connexion:', error);
		throw error;
	}
}

export async function register(username: string, password: string): Promise<AuthResponse> {
	try {
		const response = await fetch(`/register`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({ username, password })
		});
		
		return await response.json();
	} catch (error) {
		console.error('Erreur lors de l\'inscription:', error);
		throw error;
	}
}