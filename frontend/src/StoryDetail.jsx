import { useState, useEffect, useRef } from 'react';
import { fetchStory, generateAudio, audioUrl } from './api';

export default function StoryDetail({ storyId, onBack, onRefresh }) {
  const [story, setStory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [genError, setGenError] = useState(null);
  const audioRef = useRef(null);

  useEffect(() => {
    loadStory();
  }, [storyId]);

  async function loadStory() {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchStory(storyId);
      setStory(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleGenerate() {
    setGenerating(true);
    setGenError(null);
    try {
      await generateAudio(storyId);
      // Päivitä tarina jotta has_audio on tosi
      await loadStory();
      onRefresh();
    } catch (e) {
      setGenError(e.message);
    } finally {
      setGenerating(false);
    }
  }

  if (loading) return <p>Ladataan iltasatu…</p>;
  if (error) return (
    <div>
      <p className="error">Virhe: {error}</p>
      <button className="btn-secondary" onClick={onBack}>Takaisin</button>
    </div>
  );

  return (
    <div className="story-detail">
      <h2>{story.title}</h2>
      <span className="story-date">{story.created_at}</span>

      <div className="story-content">{story.content}</div>

      <div className="story-actions">
        {story.has_audio ? (
          <div className="audio-player">
            <audio ref={audioRef} controls src={audioUrl(storyId)} />
            <p className="audio-hint">Toista iltasadan ääni</p>
          </div>
        ) : (
          <button
            className="btn-generate"
            onClick={handleGenerate}
            disabled={generating}
          >
            {generating ? 'Generoidaan ääni…' : '🔊 Generoi ääni'}
          </button>
        )}
        {genError && <p className="error">{genError}</p>}
      </div>

      <button className="btn-secondary" onClick={onBack}>
        Takaisin
      </button>
    </div>
  );
}