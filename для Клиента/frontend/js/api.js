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
            let msg;
            if (typeof data.detail === 'string') {
                msg = data.detail;
            } else if (Array.isArray(data.detail)) {
                const first = data.detail[0];
                if (first && first.msg) {
                    const field = first.loc ? first.loc[first.loc.length - 1] : '';
                    if (first.msg.includes('too_short')) {
                        msg = `Поле "${field}" слишком короткое. Минимум ${first.ctx?.min_length || '?'} символов.`;
                    } else if (first.msg.includes('missing')) {
                        msg = `Поле "${field}" обязательно для заполнения.`;
                    } else if (first.msg.includes('string_type')) {
                        msg = `Поле "${field}" должно быть строкой.`;
                    } else {
                        msg = first.msg;
                    }
                } else {
                    msg = JSON.stringify(data.detail);
                }
            } else {
                msg = 'Ошибка запроса';
            }
            throw new Error(msg);
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

    // Скачивание файла (Excel/Word) с параметрами
    static async downloadFile(endpoint, filename) {
        const url = `${CONFIG.API_URL}${endpoint}`;
        const token = this.getToken();
        const headers = {};
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        const response = await fetch(url, { method: 'GET', headers });
        if (!response.ok) {
            throw new Error('Ошибка скачивания файла');
        }
        const blob = await response.blob();
        const downloadUrl = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(downloadUrl);
    }
}

// Валидация и очистка ввода
class Validator {
    static namePattern(value) {
        return value.replace(/[^a-zA-Zа-яА-ЯёЁ\s\-']/g, '');
    }

    static usernamePattern(value) {
        return value.replace(/[^a-zA-Zа-яА-ЯёЁ0-9_.]/g, '');
    }

    static alphanumericPattern(value) {
        return value.replace(/[^a-zA-Zа-яА-ЯёЁ0-9\s\-]/g, '');
    }

    static numbersOnly(value) {
        return value.replace(/\D/g, '');
    }
}