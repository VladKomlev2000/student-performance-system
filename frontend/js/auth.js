// Модуль авторизации
class Auth {
    static async login(username, password) {
        const data = await API.post('/api/auth/login', { username, password });
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));
        return data.user;
    }

    static logout() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        window.location.href = 'login.html';
    }

    static getUser() {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    }

    static isLoggedIn() {
        return !!localStorage.getItem('access_token');
    }

    static getRole() {
        const user = this.getUser();
        return user ? user.role : null;
    }

    static checkAuth() {
        if (!this.isLoggedIn()) {
            window.location.href = 'login.html';
        }
    }
}