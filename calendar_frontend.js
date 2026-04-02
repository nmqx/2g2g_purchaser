const { useState, useEffect } = React;

function CalendarApp() {
    const urlParams = new URLSearchParams(window.location.search);
    const type = urlParams.get('type') || 'usual'; // 'usual' or 'special'
    
    // Grid: 7 days, 24 hours
    const [schedule, setSchedule] = useState({});
    
    // Optional: fetch existing config
    useEffect(() => {
        fetch('/api/get_calendar?type=' + type)
            .then(res => res.json())
            .then(data => {
                if(data.schedule) setSchedule(data.schedule);
            })
            .catch(err => console.error(err));
    }, [type]);
    
    const days = [0, 1, 2, 3, 4, 5, 6];
    const hours = Array.from({length: 24}, (_, i) => i);
    
    const getDayName = (offset) => {
        if (type === 'usual') {
            const names = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"];
            return names[offset];
        } else {
            const d = new Date();
            d.setDate(d.getDate() + offset);
            return d.toLocaleDateString('fr-FR', { weekday: 'short', day: 'numeric', month: 'short' });
        }
    };
    
    const toggleSlot = (day, hour) => {
        const key = `${day}-${hour}`;
        setSchedule(prev => ({
            ...prev,
            [key]: !prev[key]
        }));
    };
    
    const toggleDay = (day) => {
        // Toggle the entire day On or Off
        const dayOn = hours.some(h => schedule[`${day}-${h}`]);
        const newState = { ...schedule };
        for(let h of hours) {
            newState[`${day}-${h}`] = !dayOn; 
        }
        setSchedule(newState);
    }
    
    const handleSave = async () => {
        await fetch('/api/save_calendar', {
            method: 'POST',
            body: JSON.stringify({ type, schedule })
        });
        alert('Configuration du calendrier sauvegardée avec succès !\nVous pouvez fermer cette page.');
        window.close();
    };
    
    return (
        <div className="min-h-screen bg-gray-50 p-6 md:p-12 font-sans text-gray-800">
            <div className="max-w-6xl mx-auto bg-white p-8 rounded-3xl shadow-2xl border border-gray-100">
                <div className="flex justify-between items-end mb-8 border-b pb-4">
                    <div>
                        <h1 className="text-4xl font-black text-indigo-700 tracking-tight">
                            {type === 'usual' ? "Calendrier Classique" : "Calendrier Spécial"}
                        </h1>
                        <p className="text-gray-500 text-lg mt-2 font-medium">
                            {type === 'usual' 
                            ? "Définissez vos horaires hebdomadaires récurrents de disponibilité." 
                            : "Définissez un emploi du temps ciblé exclusif aux 7 prochains jours."}
                        </p>
                    </div>
                </div>
                
                <div className="overflow-x-auto rounded-xl border border-gray-200 shadow-sm">
                    <table className="w-full border-collapse">
                        <thead>
                            <tr className="bg-gray-100 text-gray-600">
                                <th className="p-3 border-r font-bold text-left w-32">Jour</th>
                                {hours.map(h => <th key={h} className="p-2 border-r text-center text-xs font-bold w-12">{h}h</th>)}
                            </tr>
                        </thead>
                        <tbody>
                            {days.map(d => (
                                <tr key={d} className="group">
                                    <td 
                                        className="p-3 border-r border-t font-semibold text-gray-700 bg-gray-50 cursor-pointer hover:bg-indigo-50 transition-colors"
                                        onClick={() => toggleDay(d)}
                                        title="Cliquez pour sélectionner tout le jour"
                                    >
                                        {getDayName(d)}
                                    </td>
                                    {hours.map(h => {
                                        const isSelected = !!schedule[`${d}-${h}`];
                                        return (
                                            <td 
                                                key={h}
                                                onMouseDown={() => toggleSlot(d, h)}
                                                onMouseEnter={(e) => {
                                                    // hold mouse to draw
                                                    if(e.buttons === 1) toggleSlot(d, h);
                                                }}
                                                className={`border-r border-t cursor-pointer transition-all duration-150 select-none ${isSelected ? 'bg-indigo-500 hover:bg-indigo-600 shadow-[inset_0_3px_5px_rgba(0,0,0,0.2)]' : 'bg-white hover:bg-gray-100'}`}
                                            ></td>
                                        );
                                    })}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
                
                <div className="mt-10 flex justify-end">
                    <button 
                        onClick={handleSave} 
                        className="bg-indigo-600 text-white px-10 py-4 rounded-xl font-black text-xl shadow-xl hover:bg-indigo-700 transform hover:-translate-y-1 transition-all"
                    >
                        Sauvegarder le calendrier
                    </button>
                </div>
            </div>
        </div>
    );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<CalendarApp />);
