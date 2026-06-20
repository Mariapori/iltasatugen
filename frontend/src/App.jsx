import { useState } from 'react';
import StoryList from './StoryList.jsx';
import StoryForm from './StoryForm.jsx';
import StoryDetail from './StoryDetail.jsx';
import './App.css';

// Näkymät
const VIEW = {
  LIST: 'list',
  FORM: 'form',
  DETAIL: 'detail',
};

export default function App() {
  const [view, setView] = useState(VIEW.LIST);
  const [selectedStoryId, setSelectedStoryId] = useState(null);

  // Kun StoryList valitsee tarinan
  function handleSelectStory(id) {
    setSelectedStoryId(id);
    setView(VIEW.DETAIL);
  }

  // Kun StoryList haluaa uuden tarinan
  function handleNewStory() {
    setView(VIEW.FORM);
  }

  // Kun StoryForm tallentaa tarinan
  function handleStorySaved(story) {
    // Siirry tarinan näkymään
    setSelectedStoryId(story.id);
    setView(VIEW.DETAIL);
  }

  // Takaisin listaan
  function handleBack() {
    setView(VIEW.LIST);
    setSelectedStoryId(null);
  }

  // Refresh-kutsu StoryDetail:ltä (esim. ääni generoitu)
  function handleRefresh() {
    // StoryList hakee uudestaan automaattisesti, kun palaamme listaan
  }

  return (
    <div className="app">
      <header>
        <h1>🌙 Iltasatugen</h1>
        <p className="subtitle">Kirjoita iltasatuja ja kuuntele ne ääneen</p>
      </header>

      <main>
        {view === VIEW.LIST && (
          <StoryList
            onSelect={handleSelectStory}
            onNew={handleNewStory}
          />
        )}

        {view === VIEW.FORM && (
          <StoryForm
            onSaved={handleStorySaved}
            onBack={handleBack}
          />
        )}

        {view === VIEW.DETAIL && selectedStoryId && (
          <StoryDetail
            storyId={selectedStoryId}
            onBack={handleBack}
            onRefresh={handleRefresh}
          />
        )}
      </main>
    </div>
  );
}
