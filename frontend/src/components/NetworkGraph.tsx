"use client";

import dynamic from 'next/dynamic';
import React, { useEffect, useState, useRef, useCallback } from 'react';

const ForceGraph2D = dynamic(() => import('react-force-graph-2d'), {
    ssr: false,
    loading: () => (
        <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: '100%',
            gap: '16px'
        }}>
            <div style={{
                width: '48px',
                height: '48px',
                borderRadius: '50%',
                border: '3px solid rgba(45, 122, 79, 0.2)',
                borderTopColor: '#2d7a4f',
                animation: 'spin 1s linear infinite'
            }} />
            <span style={{ color: '#94a3b8', fontSize: '14px', fontWeight: 500 }}>
                Loading network...
            </span>
            <style>{`
                @keyframes spin {
                    to { transform: rotate(360deg); }
                }
            `}</style>
        </div>
    )
});

interface GraphProps {
    onHover: (node: any) => void;
    focusNodeId: number | string | null;
    onFocusComplete: () => void;
}

export default function NetworkGraph({ onHover, focusNodeId, onFocusComplete }: GraphProps) {
    const [data, setData] = useState<any>(null);
    const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
    const containerRef = useRef<HTMLDivElement>(null);
    const fgRef = useRef<any>(null);

    // Handle responsive sizing
    useEffect(() => {
        const updateDimensions = () => {
            if (containerRef.current) {
                setDimensions({
                    width: containerRef.current.clientWidth,
                    height: containerRef.current.clientHeight
                });
            }
        };

        updateDimensions();
        window.addEventListener('resize', updateDimensions);
        return () => window.removeEventListener('resize', updateDimensions);
    }, []);

    // Handle focus when focusNodeId changes
    useEffect(() => {
        if (!focusNodeId || !fgRef.current || !data) return;

        // Use loose comparison for ID match
        const node = data.nodes.find((n: any) => String(n.id) === String(focusNodeId));
        if (node && node.x !== undefined && node.y !== undefined) {
            fgRef.current.centerAt(node.x, node.y, 800);
            fgRef.current.zoom(3, 800);

            // Clear the focus after animation
            setTimeout(() => {
                onFocusComplete();
            }, 850);
        }
    }, [focusNodeId, data, onFocusComplete]);

    useEffect(() => {
        fetch('/data/graph_viz.json')
            .then(res => res.json())
            .then(d => setData(d))
            .catch(err => console.error('Failed to load graph data:', err));
    }, []);

    // Helper to get node radius based on group
    const getNodeRadius = useCallback((node: any) => {
        const isSentinelMaintenance = node.group === 'sentinel_maintenance';
        const isSentinel = node.group === 'sentinel_ip';
        const isMaintenance = node.group === 'maintenance';

        if (isSentinelMaintenance) return 10;
        if (isSentinel) return 9;
        if (isMaintenance) return 7;
        return 4;
    }, []);

    // Node painting with Sequoia theme
    const paintNode = useCallback((node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
        // Guard against undefined coordinates
        if (node.x === undefined || node.y === undefined || !isFinite(node.x) || !isFinite(node.y)) {
            return;
        }

        const isSentinelMaintenance = node.group === 'sentinel_maintenance';
        const isSentinel = node.group === 'sentinel_ip';
        const isMaintenance = node.group === 'maintenance';

        // Sequoia Theme Colors
        const SENTINEL_COLOR = '#fbbf24'; // Amber/Gold for key contacts
        const SENTINEL_MAINTENANCE_COLOR = '#f97316'; // Orange for key contacts needing attention
        const MAINTENANCE_COLOR = '#fb7185'; // Rose for attention needed
        const DEFAULT_COLOR = '#5aaf80'; // Sequoia green
        
        let color = DEFAULT_COLOR;
        let radius = 4;
        let glowIntensity = 0;

        if (isSentinelMaintenance) {
            color = SENTINEL_MAINTENANCE_COLOR;
            radius = 10;
            glowIntensity = 28;
        } else if (isSentinel) {
            color = SENTINEL_COLOR;
            radius = 9;
            glowIntensity = 25;
        } else if (isMaintenance) {
            color = MAINTENANCE_COLOR;
            radius = 7;
            glowIntensity = 20;
        }

        // Draw outer glow for highlighted nodes
        if (glowIntensity > 0) {
            ctx.shadowColor = color;
            ctx.shadowBlur = glowIntensity;
            
            // Draw multiple layers for stronger glow effect
            ctx.beginPath();
            ctx.arc(node.x, node.y, radius + 2, 0, 2 * Math.PI);
            ctx.fillStyle = color + '40';
            ctx.fill();
        }

        // Draw main node circle
        ctx.shadowBlur = 0;
        ctx.beginPath();
        ctx.arc(node.x, node.y, radius, 0, 2 * Math.PI);
        ctx.fillStyle = color;
        ctx.fill();

        // Add subtle inner highlight for 3D effect on special nodes
        if (isSentinelMaintenance || isSentinel || isMaintenance) {
            ctx.beginPath();
            ctx.arc(node.x - radius * 0.25, node.y - radius * 0.25, radius * 0.35, 0, 2 * Math.PI);
            ctx.fillStyle = 'rgba(255, 255, 255, 0.4)';
            ctx.fill();
        }

    }, []);

    // Define the pointer/hover hit area for each node
    const paintNodePointerArea = useCallback((node: any, color: string, ctx: CanvasRenderingContext2D) => {
        if (node.x === undefined || node.y === undefined || !isFinite(node.x) || !isFinite(node.y)) {
            return;
        }
        
        const radius = getNodeRadius(node);
        // Make hit area slightly larger than visual for easier hovering
        const hitRadius = radius + 3;
        
        ctx.beginPath();
        ctx.arc(node.x, node.y, hitRadius, 0, 2 * Math.PI);
        ctx.fillStyle = color;
        ctx.fill();
    }, [getNodeRadius]);

    if (!data) {
        return (
            <div ref={containerRef} style={{
                width: '100%',
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '16px'
            }}>
                <div style={{
                    width: '48px',
                    height: '48px',
                    borderRadius: '50%',
                    border: '3px solid rgba(45, 122, 79, 0.2)',
                    borderTopColor: '#2d7a4f',
                    animation: 'spin 1s linear infinite'
                }} />
                <span style={{ color: '#94a3b8', fontSize: '14px', fontWeight: 500 }}>
                    Loading network visualization...
                </span>
                <style>{`
                    @keyframes spin {
                        to { transform: rotate(360deg); }
                    }
                `}</style>
            </div>
        );
    }

    return (
        <div ref={containerRef} style={{ 
            width: '100%', 
            height: '100%', 
            position: 'relative',
            background: 'radial-gradient(ellipse at center, rgba(26, 77, 50, 0.15) 0%, transparent 70%)'
        }}>
            {/* Decorative grid overlay */}
            <div style={{
                position: 'absolute',
                inset: 0,
                backgroundImage: `
                    linear-gradient(rgba(90, 175, 128, 0.03) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(90, 175, 128, 0.03) 1px, transparent 1px)
                `,
                backgroundSize: '50px 50px',
                pointerEvents: 'none'
            }} />
            
            <ForceGraph2D
                ref={fgRef}
                graphData={data}
                width={dimensions.width}
                height={dimensions.height}
                nodeLabel={(node: any) => {
                    const name = node.metadata?.name || `Node ${node.id}`;
                    const job = node.metadata?.job || '';
                    return `${name}\n${job}\nInfluence: ${parseFloat(node.val || 0).toFixed(1)}`;
                }}
                nodeCanvasObject={paintNode}
                nodePointerAreaPaint={paintNodePointerArea}
                onNodeHover={onHover}
                backgroundColor="transparent"
                linkColor={() => 'rgba(90, 175, 128, 0.15)'}
                linkWidth={0.6}
                d3VelocityDecay={0.4}
                cooldownTicks={100}
                onEngineStop={() => {
                    if (fgRef.current) {
                        fgRef.current.zoomToFit(400, 50);
                    }
                }}
                enableZoomInteraction={true}
                enablePanInteraction={true}
            />
        </div>
    );
}
