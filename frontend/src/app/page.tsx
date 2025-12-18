"use client";

import { useState } from 'react';
import NetworkGraph from '../components/NetworkGraph';
import ActionPanel from '../components/ActionPanel';

export default function Home() {
  const [hoveredNode, setHoveredNode] = useState<any>(null);
  const [focusedNodeId, setFocusedNodeId] = useState<number | string | null>(null);

  const handleFocus = (nodeId: number | string) => {
    setFocusedNodeId(nodeId);
  };

  return (
    <main style={{
      display: 'flex',
      height: '100vh',
      width: '100vw',
      overflow: 'hidden',
      background: 'linear-gradient(135deg, #0a231a 0%, #0f172a 50%, #173f2e 100%)',
      position: 'relative'
    }}>
      {/* Ambient background effects */}
      <div style={{
        position: 'absolute',
        inset: 0,
        background: 'radial-gradient(ellipse 80% 50% at 50% -20%, rgba(90, 175, 128, 0.15) 0%, transparent 50%)',
        pointerEvents: 'none'
      }} />
      <div style={{
        position: 'absolute',
        inset: 0,
        background: 'radial-gradient(ellipse 60% 40% at 80% 100%, rgba(26, 77, 50, 0.2) 0%, transparent 50%)',
        pointerEvents: 'none'
      }} />
      
      {/* Graph Area */}
      <div style={{
        flex: 1,
        minWidth: 0,
        position: 'relative',
        overflow: 'hidden',
      }}>
        {/* Decorative corner accents */}
        <div style={{
          position: 'absolute',
          top: '24px',
          left: '24px',
          zIndex: 5,
          display: 'flex',
          alignItems: 'center',
          gap: '12px'
        }}>
          <div style={{
            width: '40px',
            height: '40px',
            borderRadius: '10px',
            background: 'linear-gradient(135deg, rgba(90, 175, 128, 0.2), rgba(26, 77, 50, 0.3))',
            border: '1px solid rgba(90, 175, 128, 0.2)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backdropFilter: 'blur(8px)'
          }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <circle cx="6" cy="6" r="2" fill="#5aaf80" />
              <circle cx="18" cy="6" r="2" fill="#5aaf80" />
              <circle cx="12" cy="18" r="2" fill="#5aaf80" />
              <path d="M6 6L12 18M18 6L12 18M6 6L18 6" stroke="#5aaf80" strokeWidth="1.5" strokeOpacity="0.5" />
            </svg>
          </div>
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '2px'
          }}>
            <span style={{
              fontSize: '13px',
              fontWeight: 600,
              color: '#f8fafc',
              letterSpacing: '-0.01em'
            }}>Network Visualization</span>
            <span style={{
              fontSize: '11px',
              color: '#64748b',
              fontWeight: 500
            }}>Interactive relationship mapping</span>
          </div>
        </div>

        {/* Zoom hint */}
        <div style={{
          position: 'absolute',
          bottom: '24px',
          left: '24px',
          zIndex: 5,
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '10px 16px',
          borderRadius: '8px',
          background: 'rgba(15, 23, 42, 0.6)',
          backdropFilter: 'blur(8px)',
          border: '1px solid rgba(90, 175, 128, 0.1)'
        }}>
          <span style={{ fontSize: '12px', color: '#64748b' }}>Scroll to zoom • Drag to pan</span>
        </div>

        <NetworkGraph
          onHover={setHoveredNode}
          focusNodeId={focusedNodeId}
          onFocusComplete={() => setFocusedNodeId(null)}
        />
      </div>

      {/* Sidebar */}
      <ActionPanel hoveredNode={hoveredNode} onFocusNode={handleFocus} />
    </main>
  );
}
