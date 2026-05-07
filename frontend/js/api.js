// Модуль для HTTP-запросов
class API {
    static getToken() {
        return localStorage.getItem('access_token');
    }

    static getHeaders() {
        const headers = { 'Content-Type': 'application/json' };
        const token = this.getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        return headers;
    }

    static async request(method, endpoint, body = null) {
        const url = `${CONFIG.API_URL}${endpoint}`;
        const options = {
            method,
            headers: this.getHeaders(),
        };
        if (body) {
            options.body = JSON.stringify(body);
        }
        const response = await fetch(url, options);
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || 'Ошибка запроса');
        }
        return data;
    }

    static get(endpoint) {
        return this.request('GET', endpoint);
    }

    static post(endpoint, body) {
        return this.request('POST', endpoint, body);
    }

    static put(endpoint, body) {
        return this.request('PUT', endpoint, body);
    }

    static delete(endpoint) {
        return this.request('DELETE', endpoint);
    }
}
// Валидация и очистка ввода
class Validator {
    // Только буквы, пробелы, дефис (для ФИО, названий)
    static namePattern(value) {
        return value.replace(/[^a-zA-Zа-яА-ЯёЁ\s\-']/g, '');
    }

    // Только буквы, цифры, подчёркивание (для логина)
    static usernamePattern(value) {
        return value.replace(/[^a-zA-Z0-9_]/g, '');
    }

    // Только буквы, цифры, дефис (для названий групп, предметов)
    static alphanumericPattern(value) {
        return value.replace(/[^a-zA-Zа-яА-ЯёЁ0-9\s\-]/g, '');
    }

    // Только цифры
    static numbersOnly(value) {
        return value.replace(/\D/g, '');
    }
}