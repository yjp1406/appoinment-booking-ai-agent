import React from 'react';
import { motion } from 'framer-motion';
import { Mic } from 'lucide-react';

interface AvatarProps {
    replicaId?: string;
    isCalling: boolean;
    participantAudioTrack?: any; // Placeholder for real audio data
}

export const Avatar: React.FC<AvatarProps> = ({ replicaId, isCalling }) => {
    if (!isCalling) {
        return (
            <div className="w-full h-full flex items-center justify-center bg-gray-900 rounded-3xl overflow-hidden border-4 border-gray-800 shadow-2xl group">
                <div className="text-gray-500 text-center p-8 transition-transform group-hover:scale-105 duration-500">
                    <div className="w-24 h-24 bg-gradient-to-tr from-gray-800 to-gray-700 rounded-full mx-auto mb-6 flex items-center justify-center shadow-inner">
                        <Mic size={40} className="text-gray-600" />
                    </div>
                    <p className="text-2xl font-bold text-white mb-2">Assistant Ready</p>
                    <p className="text-sm text-gray-400">Step into the future of booking</p>
                </div>
            </div>
        );
    }

    return (
        <div className="w-full h-full bg-black rounded-3xl overflow-hidden shadow-2xl relative border-4 border-indigo-500/30 group">
            {/* Background Portrait */}
            <img
                src="/avatar.png"
                alt="AI Assistant"
                className="w-full h-full object-cover opacity-80 group-hover:scale-105 transition-transform duration-[10s] ease-linear"
            />

            {/* Overlay Visualizer */}
            <div className="absolute inset-x-0 bottom-0 h-1/2 bg-gradient-to-t from-black/80 to-transparent flex flex-col items-center justify-end pb-12">

                {/* Pulsing Aura */}
                <motion.div
                    animate={{
                        scale: [1, 1.2, 1],
                        opacity: [0.3, 0.6, 0.3]
                    }}
                    transition={{
                        duration: 2,
                        repeat: Infinity,
                        ease: "easeInOut"
                    }}
                    className="absolute w-64 h-64 bg-indigo-500/20 rounded-full blur-3xl -z-10"
                />

                <div className="flex items-center gap-2 mb-4">
                    {[...Array(5)].map((_, i) => (
                        <motion.div
                            key={i}
                            animate={{
                                height: [10, 40, 10],
                            }}
                            transition={{
                                duration: 0.5 + Math.random(),
                                repeat: Infinity,
                                ease: "easeInOut"
                            }}
                            className="w-1.5 bg-indigo-400 rounded-full"
                        />
                    ))}
                </div>
                <p className="text-white text-lg font-bold tracking-widest uppercase text-xs opacity-70">
                    AI Assistant Listening...
                </p>
            </div>

            {/* Fallback for Tavus integration (Hidden if Tavus is not used) */}
            {replicaId && (
                <div className="absolute inset-0 z-20 pointer-events-none opacity-0 hover:opacity-100 transition-opacity">
                    <iframe
                        src={`https://tavus.io/replica/${replicaId}/embed?view=minimal`}
                        className="w-full h-full border-none pointer-events-auto"
                        allow="camera; microphone; autoplay; display-capture; fullscreen"
                    />
                </div>
            )}
        </div>
    );
};
