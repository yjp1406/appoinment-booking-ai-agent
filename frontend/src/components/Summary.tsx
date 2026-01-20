import React from 'react';
import { CheckCircle2, Calendar } from 'lucide-react';
import { motion } from 'framer-motion';

interface SummaryProps {
    summary: {
        text: string;
        appointments: any[];
        preferences?: string;
        timestamp: string;
    };
    onClose: () => void;
}

const formatSlot = (slotStr: string) => {
    try {
        // slotStr is like "2026-01-20T10:00:00"
        if (!slotStr) return "";

        // If it's the ISO format we saved, just parse it manually to avoid TZ shifts
        if (slotStr.includes('T') && !slotStr.endsWith('Z')) {
            const [datePart, timePart] = slotStr.split('T');
            const [y, m, d] = datePart.split('-');
            const [h, min] = timePart.split(':');

            const hours = parseInt(h);
            const ampm = hours >= 12 ? 'PM' : 'AM';
            const h12 = hours % 12 || 12;

            const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
            return `${months[parseInt(m) - 1]} ${parseInt(d)}, ${y} at ${h12}:${min} ${ampm}`;
        }

        const date = new Date(slotStr);
        return date.toLocaleString(undefined, {
            dateStyle: 'medium',
            timeStyle: 'short',
        });
    } catch (e) {
        return slotStr;
    }
};

export const Summary: React.FC<SummaryProps> = ({ summary, onClose }) => {
    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
        >
            <div className="bg-white rounded-3xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-8 border border-gray-100">
                <div className="flex items-center justify-between mb-8">
                    <h2 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                        <CheckCircle2 className="text-green-500 w-8 h-8" />
                        Call Summary
                    </h2>
                    <span className="text-sm text-gray-500 bg-gray-50 px-4 py-1.5 rounded-full font-medium">
                        {new Date(summary.timestamp).toLocaleString(undefined, {
                            dateStyle: 'medium',
                            timeStyle: 'short'
                        })}
                    </span>
                </div>

                <section className="mb-8">
                    <h3 className="text-lg font-semibold text-gray-700 mb-3 uppercase tracking-wider text-sm flex items-center gap-2">
                        <span className="w-1.5 h-1.5 bg-indigo-500 rounded-full"></span>
                        Conversation Overview
                    </h3>
                    <p className="text-gray-600 leading-relaxed bg-indigo-50/30 p-4 rounded-2xl border border-indigo-100/50">
                        {summary.text}
                    </p>
                </section>

                {summary.appointments.length > 0 && (
                    <section className="mb-8">
                        <h3 className="text-lg font-semibold text-gray-700 mb-4 uppercase tracking-wider text-sm flex items-center gap-2">
                            <span className="w-1.5 h-1.5 bg-green-500 rounded-full"></span>
                            Booked Appointments
                        </h3>
                        <div className="space-y-3">
                            {summary.appointments.map((app, i) => (
                                <div key={i} className="flex items-center gap-4 p-4 bg-green-50 border border-green-100 rounded-2xl">
                                    <div className="p-3 bg-white rounded-xl shadow-sm">
                                        <Calendar className="w-6 h-6 text-green-600" />
                                    </div>
                                    <div>
                                        <p className="font-bold text-gray-800">
                                            {formatSlot(app.slot)}
                                        </p>
                                        <p className="text-sm text-green-700 flex items-center gap-1">
                                            <CheckCircle2 size={14} /> Confirmed
                                        </p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </section>
                )}

                {summary.preferences && (
                    <section className="mb-8">
                        <h3 className="text-lg font-semibold text-gray-700 mb-3 uppercase tracking-wider text-sm flex items-center gap-2">
                            <span className="w-1.5 h-1.5 bg-yellow-500 rounded-full"></span>
                            Notes & Preferences
                        </h3>
                        <div className="bg-yellow-50/50 p-4 rounded-2xl border border-yellow-100/50 border-dashed">
                            <p className="text-gray-600 italic">" {summary.preferences} "</p>
                        </div>
                    </section>
                )}

                <button
                    onClick={onClose}
                    className="w-full py-4 bg-gray-900 text-white font-bold rounded-2xl hover:bg-gray-800 transition-colors shadow-lg shadow-gray-200"
                >
                    Finish & Close
                </button>
            </div>
        </motion.div>
    );
};
