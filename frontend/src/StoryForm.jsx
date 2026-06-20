import { useState } from 'react';
import { createStory } from './api';

export default function StoryForm({ onSaved, onBack }) {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setSaving(true);
    try {
      const story = await createStory(title, content);
      onSaved(story);
    } catch (e) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <form className="story-form" onSubmit={handleSubmit}>
      <h2>Uusi iltasatu</h2>
      {error && <p className="error">{error}</p>}

      <label>
        <span>Otsikko</span>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Kun kerran oli…"
          required
        />
      </label>

      <label>
        <span>Sisältö</span>
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Kirjoita iltasatu tähän…"
          rows={12}
          required
        />
      </label>

      <div className="form-actions">
        <button type="submit" disabled={saving || !title.trim() || !content.trim()}>
          {saving ? 'Tallennetaan…' : 'Tallenna'}
        </button>
        <button type="button" className="btn-secondary" onClick={onBack}>
          Peruuta
        </button>
      </div>
    </form>
  );
}