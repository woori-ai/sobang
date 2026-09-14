import { useState } from 'react';
import { HomeScreen } from './components/HomeScreen';
import { GameScreen } from './components/GameScreen';
import { NumberGameScreen } from './components/NumberGameScreen';
import { FireFacilityGameScreen } from './components/FireFacilityGameScreen';

export function App() {
  const [currentScreen, setCurrentScreen] = useState<
    'home' | 'color-game' | 'number-game' | 'facility-game'
  >('home');

  return (
    <div style={{ width: '100%', minHeight: '100vh', position: 'relative', overflowY: 'auto' }}>
      {currentScreen === 'home' && (
        <HomeScreen
          onStartColorGame={() => setCurrentScreen('color-game')}
          onStartNumberGame={() => setCurrentScreen('number-game')}
          onStartFacilityGame={() => setCurrentScreen('facility-game')}
        />
      )}
      {currentScreen === 'color-game' && (
        <GameScreen onGoHome={() => setCurrentScreen('home')} />
      )}
      {currentScreen === 'number-game' && (
        <NumberGameScreen onBackToHome={() => setCurrentScreen('home')} />
      )}
      {currentScreen === 'facility-game' && (
        <FireFacilityGameScreen onBackToHome={() => setCurrentScreen('home')} />
      )}
    </div>
  );
}

export default App;
