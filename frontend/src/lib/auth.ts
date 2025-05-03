// lib/auth.ts

interface AuthCookie {
	username: string;
	expiry: number;
	calibrated: boolean;
}

interface AuthStatus {
	isAuthenticated: boolean;
	username: string;
	calibrated: boolean;
}

export function setAuthCookie(username: string, calibrated: boolean): void {
	const expirationDate = new Date();
	expirationDate.setDate(expirationDate.getDate() + 7);
	
	const cookieValue = JSON.stringify({
		username,
		calibrated,
		expiry: expirationDate.getTime()
	});
	
	document.cookie = `auth=${encodeURIComponent(cookieValue)}; expires=${expirationDate.toUTCString()}; path=/`;
}

export function checkAuthentication(): AuthStatus {
	const authCookie = getAuthCookie();
	
	if (!authCookie) {
		return { isAuthenticated: false, username: '', calibrated: false };
	}
	
	const now = new Date().getTime();
	
	if (now > authCookie.expiry) {
		document.cookie = 'auth=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
		return { isAuthenticated: false, username: '', calibrated: false };
	}
	
	return { 
		isAuthenticated: true, 
		username: authCookie.username,
		calibrated: authCookie.calibrated
	};
}


export function getAuthCookie(): AuthCookie | null {
	const cookies = document.cookie.split(';');
	const authCookie = cookies.find(cookie => cookie.trim().startsWith('auth='));
	
	if (!authCookie) {
		return null;
	}
	
	try {
		const cookieValue = decodeURIComponent(authCookie.split('=')[1]);
		return JSON.parse(cookieValue);
	} catch (error) {
		console.error('Erreur lors de la lecture du cookie:', error);
		return null;
	}
}