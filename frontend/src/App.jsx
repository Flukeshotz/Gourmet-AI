import React, { useState, useEffect } from 'react';
import './index.css';
import RecommendationCard from './components/RecommendationCard';
import ComparisonModal from './components/ComparisonModal';

const API_BASE = 'http://localhost:8001/api';

function App() {
  const [theme, setTheme] = useState('dark');
  const [locations, setLocations] = useState([]);
  const [session_id] = useState(() => {
    let sid = localStorage.getItem('session_id');
    if (!sid) {
      sid = 'session_' + Math.random().toString(36).substr(2, 9);
      localStorage.setItem('session_id', sid);
    }
    return sid;
  });

  const [form, setForm] = useState({
    location: '',
    cuisine: 'Any',
    budget: 'Any',
    min_rating: 4.0,
    qualitative: ''
  });
  
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [sortBy, setSortBy] = useState('llm_rank');
  
  // Comparison State
  const [compareSelection, setCompareSelection] = useState([]);
  const [isCompareModalOpen, setIsCompareModalOpen] = useState(false);
  const [compareData, setCompareData] = useState(null);
  const [compareLoading, setCompareLoading] = useState(false);
  const [compareError, setCompareError] = useState('');

  const cuisinesList = ["Any", "Italian", "North Indian", "South Indian", "Chinese", "Continental", "Street Food", "Cafe", "Desserts", "American"];

  useEffect(() => {
    fetch(`${API_BASE}/locations`)
      .then(res => res.json())
      .then(data => {
        setLocations(data.locations);
        if (data.locations.length > 0) {
          let def = data.locations[0];
          if (data.locations.includes('delhi')) def = 'delhi';
          else if (data.locations.includes('bangalore')) def = 'bangalore';
          setForm(prev => ({ ...prev, location: def }));
        }
      })
      .catch(err => {
        console.error('Failed to load locations', err);
        setError('Failed to connect to backend server. Is it running?');
      });
  }, []);

  useEffect(() => {
    const root = document.documentElement;
    root.setAttribute('data-theme', theme);
    if (theme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: name === 'min_rating' ? parseFloat(value) : value }));
  };

  const handleSearch = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${API_BASE}/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...form, session_id })
      });
      if (!res.ok) throw new Error('API request failed');
      const data = await res.json();
      
      // Add unique IDs to handle duplicate restaurant names in UI selection
      if (data.recommendations) {
        data.recommendations.forEach((rec, i) => {
          rec._uid = `${rec.restaurant_name}_${i}`;
        });
      }
      
      setResults(data);
      setCompareSelection([]);
    } catch (err) {
      setError(err.message || 'An error occurred during search.');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleCompare = (rec) => {
    setCompareSelection(prev => {
      if (prev.includes(rec._uid)) return prev.filter(uid => uid !== rec._uid);
      if (prev.length >= 2) {
        alert("You can only compare up to 2 restaurants at a time.");
        return prev;
      }
      return [...prev, rec._uid];
    });
  };

  const handleRunComparison = async () => {
    if (compareSelection.length < 2) {
      alert("Please select exactly 2 restaurants to compare.");
      return;
    }
    
    setIsCompareModalOpen(true);
    setCompareLoading(true);
    setCompareError('');
    
    const selectedRecs = getSortedRecommendations().filter(rec => compareSelection.includes(rec._uid));
    const restaurant_names = selectedRecs.map(rec => rec.restaurant_name);
    
    try {
      const res = await fetch(`${API_BASE}/compare`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          restaurant_names: restaurant_names,
          qualitative: form.qualitative
        })
      });
      if (!res.ok) throw new Error('Comparison API request failed');
      const data = await res.json();
      setCompareData(data);
    } catch (err) {
      setCompareError(err.message || 'Error running comparison.');
    } finally {
      setCompareLoading(false);
    }
  };

  // Sort Logic
  const getSortedRecommendations = () => {
    if (!results || !results.recommendations) return [];
    return [...results.recommendations].sort((a, b) => {
      if (sortBy === 'rating_high_low') return b.rating - a.rating;
      if (sortBy === 'rating_low_high') return a.rating - b.rating;
      return a.rank - b.rank; // default llm_rank
    });
  };

  return (
    <div className="text-on-surface font-body-main antialiased min-h-screen flex">
      <div className="bg-radial-gradients"></div>
      
      {/* SideNavBar */}
      <nav className="glass-panel fixed left-0 top-0 h-full w-[320px] border-r border-black/5 dark:border-white/10 shadow-2xl flex flex-col py-gutter z-40 hidden md:flex overflow-y-auto">
        <div className="px-6 mb-8 flex items-center justify-between shrink-0">
          <div>
            <h1 className="font-display-hero text-display-hero-mobile text-primary tracking-tighter">Gourmet AI</h1>
            <p className="font-label-caps text-label-caps uppercase tracking-widest text-on-surface-variant mt-1">Digital Sommelier</p>
          </div>
          <button className="text-on-surface-variant hover:text-primary transition-colors dark:text-on-surface-variant text-slate-500" onClick={toggleTheme}>
            <span className={`material-symbols-outlined ${theme === 'light' ? '' : 'hidden'}`} style={{fontVariationSettings: "'FILL' 0"}}>light_mode</span>
            <span className={`material-symbols-outlined ${theme === 'dark' ? '' : 'hidden'}`} style={{fontVariationSettings: "'FILL' 0"}}>dark_mode</span>
          </button>
        </div>

        <div className="px-6 flex-1">
          <h3 className="font-label-caps text-label-caps uppercase tracking-widest text-on-surface-variant mb-4">Search Criteria</h3>
          <div className="space-y-4">
            <div className="relative">
              <span className="material-symbols-outlined absolute left-3 top-3 text-on-surface-variant text-sm">location_on</span>
              <select name="location" value={form.location} onChange={handleChange} className="ghost-input w-full rounded-lg py-2 pl-9 pr-4 text-sm font-body-main appearance-none">
                {locations.map(loc => <option key={loc} value={loc}>{loc.charAt(0).toUpperCase() + loc.slice(1)}</option>)}
              </select>
            </div>
            
            <div className="relative">
              <span className="material-symbols-outlined absolute left-3 top-3 text-on-surface-variant text-sm">restaurant</span>
              <select name="cuisine" value={form.cuisine} onChange={handleChange} className="ghost-input w-full rounded-lg py-2 pl-9 pr-4 text-sm font-body-main appearance-none">
                {cuisinesList.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            
            <div className="relative">
              <span className="material-symbols-outlined absolute left-3 top-3 text-on-surface-variant text-sm">payments</span>
              <select name="budget" value={form.budget} onChange={handleChange} className="ghost-input w-full rounded-lg py-2 pl-9 pr-4 text-sm font-body-main appearance-none">
                {["Any", "Low", "Medium", "High"].map(b => <option key={b} value={b}>{b === 'Any' ? 'Any Budget' : `${b} Budget`}</option>)}
              </select>
            </div>
            
            <div>
              <label className="flex justify-between text-xs text-on-surface-variant mb-2">
                <span>Min Rating</span>
                <span className="text-primary font-bold">{form.min_rating}</span>
              </label>
              <input 
                name="min_rating"
                type="range" 
                min="1" max="5" step="0.1" 
                value={form.min_rating} 
                onChange={handleChange}
                className="w-full accent-primary h-1 bg-surface-variant dark:bg-surface-variant bg-slate-200 rounded-full appearance-none" 
              />
            </div>
            
            <div>
              <label className="block text-[10px] font-label-caps uppercase tracking-widest text-on-surface-variant mb-2 ml-1">Qualitative Preferences</label>
              <textarea 
                name="qualitative"
                value={form.qualitative}
                onChange={handleChange}
                placeholder="Qualitative Preferences (e.g. quiet corner table, good for anniversaries...)"
                className="ghost-input w-full rounded-lg p-3 text-sm font-body-main h-24 resize-none"
              ></textarea>
            </div>
            
            <button 
              onClick={handleSearch}
              disabled={loading || !form.location}
              className="w-full bg-gradient-to-r from-primary to-primary-container text-on-primary font-label-caps text-label-caps uppercase tracking-widest py-3 rounded-lg hover:shadow-[0_0_15px_rgba(78,222,163,0.4)] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Searching...' : 'Search Restaurants'}
            </button>
          </div>
        </div>

        <div className="px-6 mt-8 pb-6 shrink-0 border-t border-black/10 dark:border-white/10 pt-6">
          <h3 className="font-label-caps text-label-caps uppercase tracking-widest text-on-surface-variant mb-4">Agent Pipeline</h3>
          <div className="space-y-3">
            <div className="flex items-center gap-3 text-sm text-on-surface-variant">
              <div className="pulse-dot" style={{width: '7px', height: '7px', animation: 'breathe 3s infinite ease-in-out'}}></div>
              <span>Ranker — SemanticRanker</span>
            </div>
            <div className="flex items-center gap-3 text-sm text-on-surface-variant">
              <div className="pulse-dot" style={{width: '7px', height: '7px', animation: 'breathe 3s infinite ease-in-out'}}></div>
              <span>Critic — ValidationCritic</span>
            </div>
            <div className="flex items-center gap-3 text-sm text-on-surface-variant">
              <div className="pulse-dot" style={{width: '7px', height: '7px', animation: 'breathe 3s infinite ease-in-out'}}></div>
              <span>Synth — SynthesisTrustAgent</span>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content Area */}
      <main className="flex-1 ml-0 md:ml-[320px] flex flex-col min-h-screen relative z-10">
        <header className="bg-transparent full-width top-0 flex justify-between items-center px-container-padding py-stack-lg z-30">
          <div>
            <h2 className="font-display-hero text-display-hero text-transparent bg-clip-text bg-gradient-to-r from-primary to-tertiary">Gourmet AI Recommender</h2>
            <p className="text-on-surface-variant font-status-telemetry tracking-widest uppercase mt-2 opacity-80">Powered by a 3-Agent AI Pipeline</p>
          </div>
        </header>

        <div className="px-container-padding flex-1 flex flex-col gap-6 pb-24">
          
          {error && (
            <div className="bg-red-500/10 border-l-4 border-red-500 rounded-r-lg p-4 flex items-start gap-3 fade-in-up">
              <span className="material-symbols-outlined text-error mt-0.5">error</span>
              <p className="font-body-main text-on-surface text-sm">{error}</p>
            </div>
          )}

          {!results && !loading && !error && (
            <div className="flex flex-col items-center justify-center flex-1 py-20 text-center fade-in-up">
              <div className="w-24 h-24 rounded-full bg-surface-container flex items-center justify-center mb-6">
                <span className="material-symbols-outlined text-4xl text-on-surface-variant" style={{fontVariationSettings: "'FILL' 0"}}>restaurant</span>
              </div>
              <h3 className="font-display-hero-mobile text-2xl text-on-surface mb-2">Ready to Discover</h3>
              <p className="text-on-surface-variant max-w-md">Adjust your search criteria on the left and our AI agent pipeline will curate the perfect dining options for you.</p>
            </div>
          )}

          {results && (
            <>
              {/* System Status Bar */}
              <div className="glass-panel rounded-lg p-3 flex flex-wrap items-center gap-4 md:gap-6 text-status-telemetry font-status-telemetry uppercase tracking-widest text-on-surface-variant fade-in-up">
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-sm text-tertiary">bolt</span>
                  <span className="text-on-surface">{results.candidates_filtered} candidates filtered</span>
                </div>
                <div className="hidden md:block h-3 w-px bg-black/10 dark:bg-white/10"></div>
                <div className="flex items-center gap-2">
                  <span>Source:</span>
                  <span className="bg-primary/20 text-primary px-2 py-0.5 rounded border border-primary/30 flex items-center gap-1">
                    🟢 {results.source.includes('LIVE') ? 'Live Pipeline' : results.source}
                  </span>
                </div>
                <div className="hidden md:block h-3 w-px bg-black/10 dark:bg-white/10"></div>
                <div className="flex items-center gap-2">
                  <span>RQS:</span>
                  <span><span className="text-[#F59E0B]">★★★★☆</span> (4/5)</span>
                </div>
                <div className="hidden md:block h-3 w-px bg-black/10 dark:bg-white/10"></div>
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-sm">timer</span>
                  <span className="text-amber-500">{results.latency_seconds}s</span>
                </div>
                <div className="hidden md:block h-3 w-px bg-black/10 dark:bg-white/10"></div>
                
                <div className="flex items-center gap-2 ml-auto">
                  <span>Sort:</span>
                  <select 
                    value={sortBy} 
                    onChange={(e) => setSortBy(e.target.value)}
                    className="bg-white/5 dark:bg-white/5 border border-white/10 rounded-full px-3 py-1 flex items-center gap-1.5 cursor-pointer hover:bg-white/10 transition-colors text-primary font-status-telemetry uppercase tracking-widest outline-none appearance-none pr-8 relative"
                    style={{ backgroundImage: "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%234edea3'%3E%3Cpath d='M7 10l5 5 5-5z'/%3E%3C/svg%3E\")", backgroundRepeat: "no-repeat", backgroundPosition: "right 8px center" }}
                  >
                    <option value="llm_rank" className="bg-surface text-on-surface">AI RECOMMENDED RANK</option>
                    <option value="rating_high_low" className="bg-surface text-on-surface">RATING: HIGH TO LOW</option>
                    <option value="rating_low_high" className="bg-surface text-on-surface">RATING: LOW TO HIGH</option>
                  </select>
                </div>
              </div>

              {/* Alert Banner */}
              {results.widened_message && (
                <div className="bg-orange-500/10 border-l-4 border-orange-500 rounded-r-lg p-4 flex items-start gap-3 fade-in-up">
                  <span className="material-symbols-outlined text-error mt-0.5">warning</span>
                  <p className="font-body-main text-on-surface text-sm">{results.widened_message}</p>
                </div>
              )}

              {/* Restaurant List */}
              <div className="flex flex-col gap-6 mt-4">
                {results.recommendations.length === 0 ? (
                  <div className="bg-red-500/10 border-l-4 border-red-500 rounded-r-lg p-4 flex items-start gap-3 fade-in-up">
                    <span className="material-symbols-outlined text-error mt-0.5">error</span>
                    <p className="font-body-main text-on-surface text-sm">No recommendations could be generated. Please try broadening your search.</p>
                  </div>
                ) : (
                  getSortedRecommendations().map((rec, idx) => (
                    <RecommendationCard 
                      key={idx} 
                      recommendation={rec} 
                      index={idx}
                      isSelected={compareSelection.includes(rec._uid)}
                      onToggleCompare={() => handleToggleCompare(rec)}
                      sessionId={session_id}
                    />
                  ))
                )}
              </div>
            </>
          )}
        </div>

        {/* Floating Comparison Bar */}
        <div className={`fixed bottom-8 left-1/2 -translate-x-1/2 glass-panel rounded-full px-6 py-3 flex items-center gap-6 z-50 shadow-[0_10px_40px_rgba(0,0,0,0.6)] border-t border-black/10 dark:border-white/10 min-w-[400px] justify-between transition-all duration-400 ease-out ${compareSelection.length >= 2 ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-20 pointer-events-none'}`}>
          <div className="flex items-center gap-3">
            <span className="text-xl">🆚</span>
            <span className="text-on-surface font-body-main text-sm font-semibold">
              {compareSelection.length} restaurants selected
            </span>
          </div>
          <div className="h-6 w-px bg-black/20 dark:bg-white/20"></div>
          <button 
            onClick={handleRunComparison}
            className="bg-gradient-to-r from-rose-500 to-red-600 text-white font-label-caps text-xs uppercase tracking-widest px-6 py-2 rounded-full hover:scale-105 transition-transform flex items-center gap-2"
          >
            <span>Compare Now</span>
            <span className="material-symbols-outlined text-sm">arrow_forward</span>
          </button>
        </div>

      </main>

      <ComparisonModal 
        isOpen={isCompareModalOpen}
        onClose={() => setIsCompareModalOpen(false)}
        comparisonData={compareData}
        isLoading={compareLoading}
        error={compareError}
      />
    </div>
  );
}

export default App;
