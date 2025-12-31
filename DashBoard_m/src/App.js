// App.jsx
import { BrowserRouter as Router } from 'react-router-dom';
import RoutesApp from './RoutesApp';
import { MemberProvider } from './components/Auth/MemberContext'
import './App.css';
import { SBE } from './SBE';
import React from 'react';
function App() {
  const [sbe, setSBE] = React.useState({
    tb:5000,
    te:3400,
    s:1600
  })

  return (
    <SBE.Provider value={{ sbe, setSBE }}>
      <MemberProvider>
      <Router>
        <RoutesApp />
      </Router>
      </MemberProvider>
    </SBE.Provider>
  );
}

export default App;