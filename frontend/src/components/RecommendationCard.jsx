import React, { useState, useEffect } from 'react';

const API_BASE = 'http://localhost:8001/api';

const RecommendationCard = ({ recommendation, index, onToggleCompare, isSelected, sessionId, traceId }) => {
  const [feedback, setFeedback] = useState(null); // 'up' | 'down' | null
  const [showFeedbackStatus, setShowFeedbackStatus] = useState(false);

  const {
    restaurant_name,
    cuisine,
    rating,
    average_cost,
    location,
    estimated_cost_tier,
    justification,
    highlighted_features,
    confidence_score
  } = recommendation;

  // Use the confidence score from the recommendation if available, else derive from rank
  const confScore = confidence_score ? parseInt(confidence_score) : Math.max(60, 95 - (index * 5));
  
  // Choose stroke color based on score
  const getStrokeColor = (score) => {
    if (score >= 80) return '#10b981'; // emerald
    if (score >= 60) return '#f59e0b'; // amber
    return '#ef4444'; // red
  };
  const strokeColor = getStrokeColor(confScore);

  const getBadgeColor = (tier) => {
    if (tier === 'High') return 'bg-rose-500/10 text-rose-400 border-rose-500/20';
    if (tier === 'Medium') return 'bg-[#F59E0B]/10 text-[#F59E0B] border-[#F59E0B]/20';
    return 'bg-blue-500/10 text-blue-400 border-blue-500/20';
  };

  const handleFeedback = async (type) => {
    if (feedback) return; // already voted
    setFeedback(type);
    setShowFeedbackStatus(true);
    setTimeout(() => setShowFeedbackStatus(false), 3000);
    
    try {
      await fetch(`${API_BASE}/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          trace_id: traceId || 'unknown',
          restaurant_name,
          cuisine,
          budget_tier: estimated_cost_tier,
          is_positive: type === 'up'
        })
      });
    } catch (err) {
      console.error('Feedback failed:', err);
    }
  };

  return (
    <div 
      className={`glass-card rounded-xl p-6 flex flex-col gap-4 fade-in-up ${isSelected ? 'is-compared' : ''}`}
      style={{ animationDelay: `${(index + 1) * 0.1}s` }}
    >
      <div className="flex justify-between items-start relative w-full">
        <div className="flex items-start gap-4">
          <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-sm shadow-lg ${index === 0 ? 'bg-[#F59E0B]' : 'bg-[#94A3B8]'}`}>
            {index + 1}
          </div>
          <div>
            <div className="flex items-center gap-3">
              <h3 className="font-headline-card text-headline-card text-on-surface">{restaurant_name}</h3>
            </div>
            <p className="text-on-surface-variant text-sm mt-1">
              📍 {location} • 💰 ₹{average_cost} for two
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          <button 
            onClick={() => onToggleCompare(restaurant_name)}
            className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-label-caps uppercase tracking-wider transition-all shadow-lg border ${
              isSelected 
                ? 'bg-emerald-500 text-white border-emerald-500' 
                : 'border-outline/30 text-on-surface-variant hover:text-primary hover:border-primary/50'
            }`}
          >
            {isSelected ? (
              <><span className="material-symbols-outlined text-xs">check</span><span>Comparing</span></>
            ) : (
              <><span className="text-lg leading-none">+</span><span>Compare</span></>
            )}
          </button>
          
          {/* AI Confidence Ring */}
          <div className="relative w-12 h-12 flex items-center justify-center">
            <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
              <path className="text-surface-variant" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeWidth="3"></path>
              <path className="confidence-ring" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke={strokeColor} strokeDasharray={`${confScore}, 100`} strokeWidth="3"></path>
            </svg>
            <span className="absolute text-xs font-bold" style={{ color: strokeColor }}>{confScore}%</span>
          </div>
        </div>
      </div>

      {/* Badges */}
      <div className="flex flex-wrap gap-2 ml-12">
        <span className="bg-black/5 dark:bg-white/5 text-on-surface text-xs px-2 py-1 rounded-md border border-black/10 dark:border-white/10 flex items-center gap-1">
          ★ {rating}
        </span>
        <span className={`text-xs px-2 py-1 rounded-md border ${getBadgeColor(estimated_cost_tier)}`}>
          {estimated_cost_tier} Budget
        </span>
        <span className="bg-black/5 dark:bg-white/5 text-on-surface-variant text-xs px-2 py-1 rounded-md border border-black/10 dark:border-white/10">
          {cuisine}
        </span>
        {highlighted_features && highlighted_features.map((feature, idx) => (
          <span key={idx} className="bg-violet-500/10 text-violet-400 text-xs px-2 py-1 rounded-md border border-violet-500/20">
            {feature.replace(/['"]/g, '')}
          </span>
        ))}
      </div>

      {/* AI Justification Box */}
      <div className="ai-justification-box p-3 rounded-r-lg mt-2 ml-12">
        <div className="flex items-center gap-2 mb-1">
          <span className="material-symbols-outlined text-primary text-sm" style={{fontVariationSettings: "'FILL' 1"}}>psychology</span>
          <span className="font-label-caps text-[10px] uppercase tracking-widest text-primary">AI Ranker Justification</span>
        </div>
        <p className="text-sm text-on-surface-variant italic">"{justification}"</p>
      </div>

      {/* Footer Actions */}
      <div className="flex justify-between items-center mt-2 pt-4 border-t border-black/5 dark:border-white/5 ml-12">
        <div className="flex flex-wrap gap-2">
          <button 
            onClick={() => handleFeedback('up')}
            disabled={feedback !== null}
            className={`flex items-center gap-2 px-4 py-1.5 rounded-full border text-sm transition-all ${
              feedback === 'up' 
                ? 'text-primary border-primary bg-primary/10 opacity-100' 
                : feedback === 'down'
                  ? 'border-black/10 dark:border-white/10 text-slate-400 opacity-50'
                  : 'border-black/10 dark:border-white/10 text-on-surface-variant hover:text-primary hover:border-primary/50'
            }`}
          >
            <span>👍 Good match</span>
          </button>
          
          <button 
            onClick={() => handleFeedback('down')}
            disabled={feedback !== null}
            className={`flex items-center gap-2 px-4 py-1.5 rounded-full border text-sm transition-all ${
              feedback === 'down' 
                ? 'text-secondary border-secondary bg-secondary/10 opacity-100' 
                : feedback === 'up'
                  ? 'border-black/10 dark:border-white/10 text-slate-400 opacity-50'
                  : 'border-black/10 dark:border-white/10 text-on-surface-variant hover:text-secondary hover:border-secondary/50'
            }`}
          >
            <span>👎 Not for me</span>
          </button>
          
          {showFeedbackStatus && (
            <span className="text-xs text-primary flex items-center ml-2 animate-pulse">✓ Feedback saved</span>
          )}
        </div>
        
        <div className="flex items-center gap-2 text-xs text-on-surface-variant">
          Session Memory Active 
          <div className="pulse-dot" style={{width: '7px', height: '7px', animation: 'breathe 3s infinite ease-in-out'}}></div>
        </div>
      </div>
    </div>
  );
};

export default RecommendationCard;
