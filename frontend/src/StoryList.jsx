import { useState, useEffect } from 'react';
import { fetchStories, deleteStory } from './api';

export default function StoryList({ onSelect, onNew }) {
  const [stories, setStories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadStories();
  }, []);

  async function loadStories() {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchStories();
      setStories(data.stories);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(id, title) {
    if (!confirm(`Haluatko poistaa iltasadan "${title}"?`)) return;
    try {
      await deleteStory(id);
      setStories((prev) => prev.filter((s) => s.id !== id));
    } catch (e) {
      alert(e.message);
    }
  }

  if (loading) return <p>Ladataan iltasatuja…</p>;
  if (error) return <p className="error">Virhe: {error}</p>;

  return (
    <div className="story-list">
      <h2>Iltasatuja</h2>
      {stories.length === 0 ? (
        <p>Ei vielä iltasatuja. Luo uusi!</p>
      ) : (
        <ul>
          {stories.map((story) => (
            <li key={story.id}>
              <div className="story-item">
                <button
                  className="story-title"
                  onClick={() => onSelect(story.id)}
                >
                  {story.title}
                </button>
                <span className="story-date">{story.created_at}</span>
                {story.has_audio && (
                  <span className="badge audio">🔊 Ääni</span>
                )}
                <button
                  className="btn-delete"
                  onClick={() => handleDelete(story.id, story.title)}
                >
                  Poista
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
      <button className="btn-new" onClick={onNew}>
        + Uusi iltasatu
      </button>
    </div>
  );
}