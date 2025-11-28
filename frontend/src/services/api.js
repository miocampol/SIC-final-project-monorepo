/**
 * API service for the Academic Chatbot
 */

const API_URL = 'http://localhost:8000';

/**
 * Sends a question to the chatbot API.
 * @param {string} pregunta - The question to ask.
 * @returns {Promise<{error: boolean, pregunta?: string, respuesta?: string, mensaje?: string, errorDetalle?: string}>}
 */
export async function sendMessage(pregunta) {
    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ pregunta }),
        });

        const data = await response.json();

        if (data.error) {
            return {
                error: true,
                mensaje: data.mensaje || 'Error procesando la pregunta',
                errorDetalle: data.error,
            };
        }

        return {
            error: false,
            pregunta: data.pregunta,
            respuesta: data.respuesta,
        };
    } catch (error) {
        console.error('API Error:', error);
        return {
            error: true,
            mensaje: 'Error de conexión con el servidor',
            errorDetalle: error.message,
        };
    }
}
