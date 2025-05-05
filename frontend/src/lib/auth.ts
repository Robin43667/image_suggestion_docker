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
    
    document.cookie = `auth=${encodeURIComponent(cookieValue)}; expires=${expirationDate.toUTCString()}; path=/; SameSite=Lax`;
    console.log('Cookie d\'authentification défini:', username, calibrated); 
}

export function getAuthCookie(): AuthCookie | null {
    const cookies = document.cookie.split(';');
    const authCookie = cookies.find(cookie => cookie.trim().startsWith('auth='));
    
    if (!authCookie) {
        console.log('Aucun cookie d\'authentification trouvé'); 
        return null;
    }
    
    try {
        const cookieValue = decodeURIComponent(authCookie.split('=')[1]);
        const parsed = JSON.parse(cookieValue);
        console.log('Cookie d\'authentification trouvé:', parsed); 
        return parsed;
    } catch (error) {
        console.error('Erreur lors de la lecture du cookie:', error);
        return null;
    }
}

export function clearAuthCookie(): void {
    document.cookie = 'auth=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    console.log('Cookie d\'authentification effacé');
}

export async function checkAuthentication(): Promise<AuthStatus> {
    const authData = getAuthCookie();
    
    if (!authData) {
        return { isAuthenticated: false, username: '', calibrated: false };
    }
    
    const now = new Date().getTime();
    if (now > authData.expiry) {
        clearAuthCookie();
        return { isAuthenticated: false, username: '', calibrated: false };
    }
    
    console.log('Utilisateur authentifié:', authData.username); 
    return {
        isAuthenticated: true,
        username: authData.username,
        calibrated: authData.calibrated
    };
}