import React, { useState } from 'react';
import { Send } from 'lucide-react';

const InputArea = ({ onSend, disabled, hasMessages }) => {
    const [input, setInput] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (input.trim() && !disabled) {
            onSend(input.trim());
            setInput('');
        }
    };

    return (
        <div className={`transition-all duration-500 ease-in-out w-full ${hasMessages ? '' : 'transform scale-100'}`}>
            <form onSubmit={handleSubmit} className="relative flex items-center w-full">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Preguntarle a PrismaUNAL"
                    disabled={disabled}
                    className={`w-full pl-6 pr-14 py-4 rounded-full border-none 
                    bg-gray-100 dark:bg-prisma-input 
                    text-gray-900 dark:text-prisma-text 
                    placeholder-gray-500 dark:placeholder-gray-400 
                    focus:ring-2 focus:ring-prisma-accent/20 outline-none 
                    transition-all shadow-sm hover:shadow-md
                    disabled:opacity-50 disabled:cursor-not-allowed
                    text-lg`}
                />
                <button
                    type="submit"
                    disabled={!input.trim() || disabled}
                    className={`absolute right-3 p-2 rounded-full transition-colors
                    ${input.trim() && !disabled
                            ? 'bg-white dark:bg-prisma-text text-black hover:bg-gray-200'
                            : 'bg-transparent text-gray-400 cursor-not-allowed'}`}
                >
                    <Send className="w-5 h-5" />
                </button>
            </form>
            {!hasMessages && (
                <div className="flex justify-center gap-4 mt-8 flex-wrap">
                    <button className="flex items-center gap-2 px-4 py-2 rounded-full bg-gray-100 dark:bg-prisma-surface text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-prisma-hover transition-colors">
                        <span className="w-4 h-4 bg-purple-400 rounded-full opacity-50"></span>
                        Consultar materias
                    </button>
                    <button className="flex items-center gap-2 px-4 py-2 rounded-full bg-gray-100 dark:bg-prisma-surface text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-prisma-hover transition-colors">
                        <span className="w-4 h-4 bg-violet-400 rounded-full opacity-50"></span>
                        Ver créditos
                    </button>
                    <button className="flex items-center gap-2 px-4 py-2 rounded-full bg-gray-100 dark:bg-prisma-surface text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-prisma-hover transition-colors">
                        <span className="w-4 h-4 bg-fuchsia-400 rounded-full opacity-50"></span>
                        Prerrequisitos
                    </button>
                </div>
            )}
        </div>
    );
};

export default InputArea;
