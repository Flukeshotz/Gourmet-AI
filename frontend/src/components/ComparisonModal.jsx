import React from 'react';

const ComparisonModal = ({ isOpen, onClose, comparisonData, isLoading, error }) => {
  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 z-[60] flex items-center justify-center backdrop-blur-[12px]" 
      style={{ backgroundColor: 'rgba(0, 0, 0, 0.45)' }}
    >
      <div className="w-full max-w-[960px] max-h-[90vh] overflow-y-auto rounded-2xl border border-black/10 dark:border-white/10 shadow-2xl bg-surface/95 backdrop-blur-2xl p-8 relative animate-fadeIn">
        
        {/* Close Button */}
        <button 
          onClick={onClose} 
          className="absolute top-6 right-6 text-on-surface-variant hover:text-on-surface transition-colors"
        >
          <span className="material-symbols-outlined">close</span>
        </button>

        {/* Content */}
        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-20 gap-4">
            <div className="w-12 h-12 border-4 border-primary/30 border-t-primary rounded-full animate-spin"></div>
            <p className="text-primary font-label-caps uppercase tracking-widest text-sm">Generating Comparison...</p>
          </div>
        ) : error ? (
          <div className="bg-red-500/10 border border-red-500/20 text-red-500 p-4 rounded-lg flex items-start gap-3">
            <span className="material-symbols-outlined mt-0.5">error</span>
            <p className="font-body-main text-sm">{error}</p>
          </div>
        ) : comparisonData ? (
          <>
            {/* Header */}
            <div className="mb-8">
              <h2 className="text-primary font-display-hero text-3xl font-extrabold flex items-center gap-3">
                <span>🆚</span> AI Decision Support Analysis
              </h2>
              <p className="font-label-caps text-label-caps tracking-widest text-on-surface-variant opacity-80 mt-1 uppercase">
                POWERED BY LLAMA 3.3 70B — REASONING MODEL
              </p>
            </div>

            <div className="flex flex-col gap-8">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {comparisonData.comparisons && comparisonData.comparisons.map((c, idx) => {
                  const percentage = (c.fit_score / 10) * 100;
                  // Color bar based on score
                  const barGradient = percentage >= 80 ? 'from-emerald-600 to-green-400' : percentage >= 60 ? 'from-emerald-600 to-amber-400' : 'from-amber-500 to-red-400';
                  const scoreColor = percentage >= 80 ? 'text-emerald-500' : percentage >= 60 ? 'text-amber-500' : 'text-red-500';

                  return (
                    <div key={idx} className="border border-black/10 dark:border-white/10 bg-surface-container rounded-xl p-6 flex flex-col gap-6 shadow-sm">
                      <h3 className="font-headline-card text-on-surface">{c.restaurant_name}</h3>
                      
                      {/* Fit Score Bar */}
                      <div className="space-y-1">
                        <div className="flex justify-between items-end font-label-caps text-xs uppercase tracking-widest">
                          <span className="text-on-surface-variant">FIT SCORE</span>
                          <span className={`font-bold ${scoreColor}`}>{c.fit_score}/10</span>
                        </div>
                        <div className="h-1.5 w-full bg-black/10 dark:bg-white/10 rounded-full overflow-hidden">
                          <div className={`h-full bg-gradient-to-r ${barGradient} transition-all duration-1000 ease-out`} style={{ width: `${percentage}%` }}></div>
                        </div>
                      </div>

                      <div className="space-y-4">
                        {/* Pros */}
                        <div>
                          <p className="font-label-caps text-[10px] uppercase tracking-tighter text-emerald-600 mb-2">PROS</p>
                          <ul className="flex flex-col gap-2">
                            {c.pros.map((p, i) => (
                              <li key={i} className="flex items-start gap-2 text-sm text-on-surface">
                                <span className="text-emerald-500">✅</span>
                                <span>{p}</span>
                              </li>
                            ))}
                          </ul>
                        </div>

                        {/* Cons */}
                        <div>
                          <p className="font-label-caps text-[10px] uppercase tracking-tighter text-rose-600 mb-2">CONS</p>
                          <ul className="flex flex-col gap-2">
                            {c.cons.map((con, i) => (
                              <li key={i} className="flex items-start gap-2 text-sm text-on-surface">
                                <span className="text-rose-500">❌</span>
                                <span>{con}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
              
              {/* Verdict Box */}
              <div className="bg-primary/10 border-l-4 border-primary p-5 rounded-r-xl">
                <div className="flex items-center gap-2 mb-2">
                  <span className="material-symbols-outlined text-primary text-lg" style={{fontVariationSettings: "'FILL' 1"}}>military_tech</span>
                  <span className="font-label-caps text-xs uppercase tracking-widest text-primary">🏆 AI FINAL RECOMMENDATION</span>
                </div>
                <p className="text-sm text-on-surface italic leading-relaxed">
                  {comparisonData.verdict}
                </p>
              </div>
            </div>
          </>
        ) : null}
      </div>
    </div>
  );
};

export default ComparisonModal;
