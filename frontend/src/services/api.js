/**
 * API service for the Academic Chatbot
 */

const API_URL = 'http://localhost:8000';

/**
 * Sends a question to the chatbot API with streaming support.
 * @param {string} pregunta - The question to ask.
 * @param {function} onChunk - Callback function called for each chunk of the response.
 * @returns {Promise<{error: boolean, mensaje?: string}>}
 */
export async function sendMessageStream(pregunta, onChunk) {
    try {
        const response = await fetch(`${API_URL}/chat/stream`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ pregunta }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();

            if (done) break;

            // Decode the chunk
            buffer += decoder.decode(value, { stream: true });

            // Process complete SSE messages
            const lines = buffer.split('\n');
            buffer = lines.pop() || ''; // Keep incomplete line in buffer

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = line.slice(6); // Remove 'data: ' prefix

                    try {
                        const parsed = JSON.parse(data);

                        // Check if streaming is done
                        if (parsed.done) {
                            return { error: false };
                        }

                        // Get the content chunk (backend sends "content" not "chunk")
                        if (parsed.content !== undefined) {
                            onChunk(parsed.content);
                        }
                    } catch (e) {
                        console.error('Error parsing SSE data:', e, 'Line:', line);
                    }
                }
            }
        }

        return { error: false };
    } catch (error) {
        console.error('API Error:', error);
        return {
            error: true,
            mensaje: 'Error de conexión con el servidor',
        };
    }
}

/**
 * Sends a question to the chatbot API (non-streaming version).
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
