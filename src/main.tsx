import {StrictMode} from 'react';
import {createRoot} from 'react-dom/client';
import App from './App.tsx';
import ErrorBoundary from './components/ErrorBoundary';
import { initPwa } from './utils/pwa';
import './index.css';

let rendered = false;
function renderApp() {
  if (rendered) return;
  rendered = true;
  createRoot(document.getElementById('root')!).render(
    <StrictMode>
      <ErrorBoundary name="root">
        <App />
      </ErrorBoundary>
    </StrictMode>,
  );
}

// PWA setup must never block the app: render as soon as it settles,
// or after 2s if the service worker APIs hang.
const pwaTimeout = window.setTimeout(renderApp, 2000);
void initPwa()
  .catch(() => {})
  .finally(() => {
    window.clearTimeout(pwaTimeout);
    renderApp();
  });
