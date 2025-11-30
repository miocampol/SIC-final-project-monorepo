import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Bot, User } from 'lucide-react';
import { motion } from 'framer-motion';

const MessageBubble = ({ message }) => {
    const isBot = message.role === 'bot';

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`flex gap-3 ${isBot ? 'justify-start' : 'justify-end'}`}
        >
            {isBot && (
                <div className="w-8 h-8 rounded-full bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center flex-shrink-0">
                    <Bot className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                </div>
            )}

            <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 shadow-sm ${isBot
                    ? 'bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-100 border border-gray-100 dark:border-gray-700'
                    : 'bg-purple-600 text-white'
                    }`}
            >
                {isBot ? (
                    <div className="prose prose-sm max-w-none text-gray-800 dark:text-gray-200 dark:prose-invert">
                        <ReactMarkdown>{message.content}</ReactMarkdown>
                    </div>
                ) : (
                    <p className="text-sm">{message.content}</p>
                )}
            </div>

            {!isBot && (
                <div className="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center flex-shrink-0">
                    <User className="w-5 h-5 text-gray-600 dark:text-gray-300" />
                </div>
            )}
        </motion.div>
    );
};

export default MessageBubble;
