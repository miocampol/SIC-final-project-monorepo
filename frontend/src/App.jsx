import React, { useState } from 'react';
import Header from './components/UI/Header';
import ChatContainer from './components/Chat/ChatContainer';
import InputArea from './components/Chat/InputArea';
import { sendMessageStream } from './services/api';

function App() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  // Default to dark mode
  const [theme, setTheme] = useState('dark');

  React.useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  const handleSend = async (text) => {
    if (!text.trim()) return;

    // Add user message
    setMessages((prev) => [...prev, { role: 'user', content: text }]);

    // Add empty bot message that will be updated with streaming content
    const botMessageIndex = messages.length + 1;
    setMessages((prev) => [...prev, { role: 'bot', content: '' }]);

    try {
      const response = await sendMessageStream(text, (chunk) => {
        // Update the bot message with each chunk
        setMessages((prev) => {
          const newMessages = [...prev];
          if (newMessages[botMessageIndex]) {
            newMessages[botMessageIndex] = {
              role: 'bot',
              content: newMessages[botMessageIndex].content + chunk,
            };
          }
          return newMessages;
        });
      });

      if (response.error) {
        setMessages((prev) => {
          const newMessages = [...prev];
          if (newMessages[botMessageIndex]) {
            newMessages[botMessageIndex] = {
              role: 'bot',
              content: `❌ **Error**: ${response.mensaje}`,
            };
          }
          return newMessages;
        });
      }
    } catch (error) {
      setMessages((prev) => {
        const newMessages = [...prev];
        if (newMessages[botMessageIndex]) {
          newMessages[botMessageIndex] = {
            role: 'bot',
            content: '❌ **Error de conexión**: No se pudo conectar con el servidor. Por favor intenta más tarde.',
          };
        }
        return newMessages;
      });
    }
  };

  return (
    <div className="flex flex-col h-screen bg-white dark:bg-prisma-bg text-gray-900 dark:text-prisma-text transition-colors duration-300 font-sans">
      <Header theme={theme} toggleTheme={toggleTheme} />

      <main className="flex-1 flex flex-col relative overflow-hidden pt-16">
        {messages.length > 0 ? (
          <>
            <ChatContainer messages={messages} isLoading={isLoading} />
            <div className="w-full max-w-4xl mx-auto p-4 sticky bottom-0 z-20">
              <InputArea onSend={handleSend} disabled={isLoading} hasMessages={true} />
            </div>
          </>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center p-4 w-full max-w-3xl mx-auto z-20">
            <div className="mb-8 text-center">
              <h1 className="text-4xl md:text-5xl font-medium mb-2 inline-block cursor-default group">
                <span className="bg-gradient-to-r from-purple-400 via-violet-500 to-fuchsia-500 bg-clip-text text-transparent bg-[length:200%_auto] animate-gradient hover:bg-right transition-all duration-500">
                  Hola
                </span>
              </h1>
              <h2 className="text-2xl md:text-3xl text-gray-400 font-normal">
                ¿En qué te puedo ayudar?
              </h2>
            </div>
            <InputArea onSend={handleSend} disabled={isLoading} hasMessages={false} />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
