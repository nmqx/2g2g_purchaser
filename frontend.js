import React, { useState, useEffect, useMemo } from 'react';

const formatPrice = (priceObj) => {
    if (!priceObj) return "N/A";
    const value = priceObj.minorUnits / Math.pow(10, priceObj.decimals);
    return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: priceObj.code }).format(value);
};

const formatTime = (dateString) => {
    if (!dateString) return "";
    const date = new Date(dateString);
    return date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
};

const OfferCard = ({ offer }) => {
    const { item, store, itemsAvailable, pickupInterval } = offer;
    const isAvailable = itemsAvailable > 0;

    return (
        <div className="flex flex-col bg-white rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 overflow-hidden border border-gray-100 relative">
            <div className="absolute top-4 left-4 z-10 bg-black text-white text-sm font-mono font-bold px-4 py-2 rounded-lg shadow-md flex items-center gap-2">
                <span className="text-gray-400">ID:</span>
                <span className="tracking-wider">{item.itemId}</span>
            </div>

            <div className="h-64 w-full bg-gray-200 relative overflow-hidden group">
                <img
                    src={item.coverPicture?.currentUrl || '/api/placeholder/400/300'}
                    alt={item.name}
                    className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                />
                <div className={`absolute top-4 right-4 px-4 py-2 rounded-full text-sm font-bold shadow-lg ${isAvailable ? 'bg-green-500 text-white' : 'bg-red-500 text-white'}`}>
                    {isAvailable ? `${itemsAvailable} disponibles` : 'Épuisé'}
                </div>
            </div>

            <div className="p-6 flex flex-col flex-grow">
                <div className="flex items-center gap-4 mb-5">
                    <img
                        src={store.logoPicture?.currentUrl || '/api/placeholder/40/40'}
                        alt={store.storeName}
                        className="w-14 h-14 rounded-full border shadow-sm object-cover"
                    />
                    <div>
                        <h3 className="text-base font-bold text-gray-800 line-clamp-1">{store.storeName}</h3>
                        <p className="text-sm text-gray-500 line-clamp-1">{store.storeLocation.address.addressLine}</p>
                    </div>
                </div>

                <h2 className="text-2xl font-black text-gray-900 mb-3">{item.name}</h2>

                <div className="text-sm text-gray-700 mb-5 bg-gray-50 p-3 rounded-lg border border-gray-100 flex items-center gap-2 shadow-inner">
                    <span className="font-bold text-gray-900">Collecte: </span>
                    {pickupInterval ? `${formatTime(pickupInterval.start)} - ${formatTime(pickupInterval.end)}` : 'Non spécifié'}
                </div>

                <div className="mt-auto pt-5 border-t border-gray-100 flex items-center justify-between">
                    <div className="flex flex-col">
                        <span className="text-sm text-gray-400 line-through font-medium">
                            {formatPrice(item.itemValue)}
                        </span>
                        <span className="text-3xl font-black text-green-600 tracking-tight">
                            {formatPrice(item.itemPrice)}
                        </span>
                    </div>

                    <button
                        disabled={!isAvailable}
                        className={`px-8 py-3 rounded-xl font-bold text-lg transition-colors shadow-md ${isAvailable ? 'bg-blue-600 text-white hover:bg-blue-700 hover:shadow-lg' : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                            }`}
                    >
                        {isAvailable ? 'Réserver' : 'Indisponible'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default function OffersDashboard() {
    const [items, setItems] = useState([]);
    const [page, setPage] = useState(0);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [canLoadMore, setCanLoadMore] = useState(true);
    const [searchQuery, setSearchQuery] = useState("");

    const fetchSinglePage = async (pageNumber) => {
        const proxyUrl = `http://localhost:3001/api/tgtg?lat=47.1064143&lng=-1.5318723&language=en&page=${pageNumber}&withStockOnly=0`;
        const response = await fetch(proxyUrl);
        if (!response.ok) throw new Error('Failed to fetch data from proxy');
        const data = await response.json();
        return data;
    };


    const loadSequentialPages = async (startPage, count) => {
        setIsLoading(true);
        setError(null);
        let allNewItems = [];
        let finalCanLoadMore = true;

        try {

            const promises = Array.from({ length: count }, (_, i) => fetchSinglePage(startPage + i));
            const results = await Promise.all(promises);

            for (const data of results) {
                if (data.success && data.payload?.items) {
                    allNewItems = [...allNewItems, ...data.payload.items];
                    finalCanLoadMore = data.canLoadMore;
                }
            }


            setItems(prevItems => {
                const map = new Map();
                [...prevItems, ...allNewItems].forEach(item => map.set(item.item.itemId, item));
                return Array.from(map.values());
            });

            setCanLoadMore(finalCanLoadMore);
            setPage(startPage + count - 1);
        } catch (err) {
            console.error(err);
            setError("Erreur lors du chargement des paniers. Vérifiez votre backend.");
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        // Initial fetch: Load first 10 pages in one shot
        loadSequentialPages(0, 10);
    }, []);

    const handleLoadMore = () => {
        if (!isLoading) {

            loadSequentialPages(page + 1, 5);
        }
    };


    const filteredItems = useMemo(() => {
        if (!searchQuery.trim()) return items;
        const lowQuery = searchQuery.toLowerCase();
        return items.filter(offer => {
            const storeName = offer.store?.storeName?.toLowerCase() || '';
            const itemName = offer.item?.name?.toLowerCase() || '';
            return storeName.includes(lowQuery) || itemName.includes(lowQuery);
        });
    }, [items, searchQuery]);

    return (
        <div className="min-h-screen bg-gray-50 p-8 font-sans">
            <div className="max-w-7xl mx-auto">

                <header className="mb-10 antialiased flex flex-col md:flex-row md:items-center justify-between gap-6">
                    <div>
                        <h1 className="text-4xl font-black text-gray-900 tracking-tight mb-2">Paniers Surprises</h1>
                        <p className="text-lg text-gray-500 font-medium">Affichage de {filteredItems.length} paniers <span className="text-sm">(Pages 0-{page})</span>.</p>
                    </div>

                    {/* Search Bar */}
                    <div className="relative w-full md:w-96 shadow-sm">
                        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                            <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
                        </div>
                        <input
                            type="text"
                            className="w-full pl-12 pr-4 py-3 bg-white border-none rounded-xl text-lg font-medium text-gray-900 shadow-md focus:ring-4 focus:ring-blue-100 transition-shadow outline-none placeholder-gray-400"
                            placeholder="Rechercher par nom ou magasin..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                        />
                    </div>
                </header>

                {error && (
                    <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded-r-lg mb-8 shadow-sm font-medium">
                        {error}
                    </div>
                )}

                {/* Using a smaller column count layout to make elements bigger */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3 gap-8 mb-12">
                    {filteredItems.map((offer, index) => (
                        <OfferCard key={`${offer.item.itemId}-${index}`} offer={offer} />
                    ))}
                </div>

                {!isLoading && filteredItems.length === 0 && (
                    <div className="text-center py-20 text-gray-400 font-bold text-2xl">
                        Aucun panier trouvé :(
                    </div>
                )}

                <div className="flex justify-center mt-4 pb-16">
                    {canLoadMore ? (
                        <button
                            onClick={handleLoadMore}
                            disabled={isLoading}
                            className={`px-10 py-4 rounded-full font-black text-xl shadow-xl transition-all ${isLoading
                                ? 'bg-gray-300 text-gray-500 cursor-wait'
                                : 'bg-indigo-600 text-white hover:bg-indigo-700 hover:shadow-2xl transform hover:-translate-y-1'
                                }`}
                        >
                            {isLoading ? 'Chargement...' : 'Afficher plus (Pages suivantes)'}
                        </button>
                    ) : (
                        <p className="text-gray-400 font-bold text-lg bg-gray-100 px-6 py-3 rounded-full">Vous avez atteint la fin.</p>
                    )}
                </div>

            </div>
        </div>
    );
}