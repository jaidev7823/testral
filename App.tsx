
import React, { useState, useCallback, useRef, useEffect } from 'react';
import { BrowserPane } from './components/BrowserPane';
import { ChatPane } from './components/ChatPane';

const App: React.FC = () => {
  const [currentUrl, setCurrentUrl] = useState('https://www.wikipedia.org');
  const [chatWidth, setChatWidth] = useState(400);
  const [isResizing, setIsResizing] = useState(false);
  const [testPayload, setTestPayload] = useState<{ count: number, prompt?: string }>({ count: 0 });
  const containerRef = useRef<HTMLDivElement>(null);

  const startResizing = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    setIsResizing(true);
  }, []);

  const stopResizing = useCallback(() => {
    setIsResizing(false);
  }, []);

  const resize = useCallback(
    (e: MouseEvent) => {
      if (isResizing && containerRef.current) {
        const containerWidth = containerRef.current.offsetWidth;
        const newChatWidth = containerWidth - e.clientX;
        if (newChatWidth >= 320 && newChatWidth <= containerWidth * 0.7) {
          setChatWidth(newChatWidth);
        }
      }
    },
    [isResizing]
  );

  useEffect(() => {
    if (isResizing) {
      window.addEventListener('mousemove', resize);
      window.addEventListener('mouseup', stopResizing);
    } else {
      window.removeEventListener('mousemove', resize);
      window.removeEventListener('mouseup', stopResizing);
    }
    return () => {
      window.removeEventListener('mousemove', resize);
      window.removeEventListener('mouseup', stopResizing);
    };
  }, [isResizing, resize, stopResizing]);

  const handleUrlChange = (url: string) => {
    let formattedUrl = url;
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      formattedUrl = `https://${url}`;
    }
    setCurrentUrl(formattedUrl);
  };

  const handleTriggerTest = (url: string, customPrompt?: string) => {
    setTestPayload(prev => ({ count: prev.count + 1, prompt: customPrompt }));
  };

  return (
    <div 
      ref={containerRef}
      className={`flex h-screen w-full overflow-hidden bg-[#0a0a0a] text-zinc-300 font-sans selection:bg-zinc-100 selection:text-zinc-900 ${isResizing ? 'cursor-col-resize select-none' : ''}`}
    >
      <div className="flex-1 h-full overflow-hidden flex flex-col">
        <BrowserPane 
          url={currentUrl} 
          onNavigate={handleUrlChange}
          onTestUrl={handleTriggerTest}
        />
      </div>

      <div
        onMouseDown={startResizing}
        className={`w-[1px] h-full cursor-col-resize transition-all duration-300 z-20 ${
          isResizing ? 'bg-zinc-100 scale-x-150' : 'bg-zinc-800 hover:bg-zinc-500'
        }`}
      />

      <div 
        style={{ width: `${chatWidth}px` }}
        className="h-full flex flex-col bg-[#0f0f0f] shrink-0 border-l border-zinc-800/30"
      >
        <ChatPane 
          currentBrowserUrl={currentUrl} 
          externalTrigger={testPayload.count}
          customPrompt={testPayload.prompt}
        />
      </div>
    </div>
  );
};

export default App;
