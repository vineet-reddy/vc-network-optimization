"use client";

import React, { useEffect, useState } from 'react';

interface NodeData {
    id: number;
    weight?: number;
    value?: number;
    days_dormant?: number;
}

interface SentinelResults {
    ip: { sentinels: number[] };
    greedy: { sentinels: number[] };
}

interface MaintenanceResults {
    selected_nodes: NodeData[];
}

export default function ActionPanel({ hoveredNode, onFocusNode }: {
    hoveredNode: any;
    onFocusNode: (id: number | string) => void;
}) {
    const [sentinels, setSentinels] = useState<any[]>([]);
    const [maintenance, setMaintenance] = useState<any>(null);

    useEffect(() => {
        Promise.all([
            fetch('/data/sentinel_results.json').then(r => r.json()),
            fetch('/data/maintenance_results.json').then(r => r.json())
        ]).then(([s, m]) => {
            setSentinels(s);
            setMaintenance(m);
        }).catch(console.error);
    }, []);

    if (!maintenance || sentinels.length === 0) {
        return (
            <aside style={styles.panel}>
                <div style={styles.loadingContainer}>
                    <div style={styles.spinner} />
                    <span style={styles.loadingText}>Loading insights...</span>
                </div>
            </aside>
        );
    }

    const sentinelList = sentinels.slice(0, 5);
    const maintenanceList = maintenance.selected_nodes.slice(0, 5);

    const isSentinelMaintenance = hoveredNode?.group === 'sentinel_maintenance';
    const isSentinel = hoveredNode?.group === 'sentinel_ip';
    const isMaintenance = hoveredNode?.group === 'maintenance';

    const getName = (node: any) => node?.metadata?.name || `Node ${node?.id}`;

    return (
        <aside style={styles.panel}>
            {/* Header */}
            <header style={styles.header}>
                <div style={styles.logoContainer}>
                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" style={styles.logo}>
                        <path d="M12 2L4 7V17L12 22L20 17V7L12 2Z" fill="url(#logoGradient)" />
                        <path d="M12 6L8 8.5V13.5L12 16L16 13.5V8.5L12 6Z" fill="rgba(255,255,255,0.9)" />
                        <defs>
                            <linearGradient id="logoGradient" x1="4" y1="2" x2="20" y2="22">
                                <stop stopColor="#5aaf80" />
                                <stop offset="1" stopColor="#1a4d32" />
                            </linearGradient>
                        </defs>
                    </svg>
                </div>
                <div>
                    <h1 style={styles.title}>Network Intelligence</h1>
                    <p style={styles.subtitle}>Sequoia Relationship Optimizer</p>
                </div>
            </header>

            {/* Legend */}
            <div style={styles.legend}>
                <div style={styles.legendItem}>
                    <span style={{ ...styles.legendDot, background: 'linear-gradient(135deg, #fbbf24, #f59e0b)' }} />
                    <span>Sentinels</span>
                </div>
                <div style={styles.legendItem}>
                    <span style={{ ...styles.legendDot, background: 'linear-gradient(135deg, #f97316, #ea580c)' }} />
                    <span>Both</span>
                </div>
                <div style={styles.legendItem}>
                    <span style={{ ...styles.legendDot, background: 'linear-gradient(135deg, #fb7185, #e11d48)' }} />
                    <span>Maintenance</span>
                </div>
            </div>

            {/* Node Details Card */}
            <div style={styles.detailsCard}>
                {hoveredNode ? (
                    <div style={styles.detailsContent}>
                        <div style={styles.detailsHeader}>
                            <div style={{
                                ...styles.avatar,
                                background: isSentinelMaintenance
                                    ? 'linear-gradient(135deg, rgba(249, 115, 22, 0.2), rgba(234, 88, 12, 0.3))'
                                    : isSentinel
                                        ? 'linear-gradient(135deg, rgba(251, 191, 36, 0.2), rgba(245, 158, 11, 0.3))'
                                        : isMaintenance
                                            ? 'linear-gradient(135deg, rgba(251, 113, 133, 0.2), rgba(225, 29, 72, 0.3))'
                                            : 'linear-gradient(135deg, rgba(90, 175, 128, 0.2), rgba(26, 77, 50, 0.3))',
                                borderColor: isSentinelMaintenance ? '#f97316' : isSentinel ? '#fbbf24' : isMaintenance ? '#fb7185' : '#5aaf80'
                            }}>
                                <span style={{
                                    color: isSentinelMaintenance ? '#f97316' : isSentinel ? '#fbbf24' : isMaintenance ? '#fb7185' : '#5aaf80',
                                    fontWeight: 700,
                                    fontSize: '18px'
                                }}>
                                    {hoveredNode.metadata?.name ? hoveredNode.metadata.name.charAt(0).toUpperCase() : '#'}
                                </span>
                            </div>
                            <div style={{ flex: 1 }}>
                                <h3 style={styles.nodeName}>{getName(hoveredNode)}</h3>
                                <span style={styles.nodeRole}>
                                    {hoveredNode.metadata?.job || (isSentinelMaintenance ? 'Sentinel + Maintenance' : isSentinel ? 'Sentinel' : isMaintenance ? 'Maintenance' : 'Network Member')}
                                </span>
                            </div>
                            {(isSentinelMaintenance || isSentinel || isMaintenance) && (
                                <div style={{
                                    ...styles.badge,
                                    background: isSentinelMaintenance
                                        ? 'linear-gradient(135deg, #f97316, #ea580c)'
                                        : isSentinel
                                            ? 'linear-gradient(135deg, #fbbf24, #f59e0b)'
                                            : 'linear-gradient(135deg, #fb7185, #e11d48)'
                                }}>
                                    {isSentinelMaintenance ? '⚡' : isSentinel ? '★' : '!'}
                                </div>
                            )}
                        </div>

                        {/* Contact Info */}
                        {hoveredNode.metadata && (
                            <div style={styles.contactInfo}>
                                <div style={styles.contactRow}>
                                    <span style={styles.contactIcon}>✉</span>
                                    <span style={styles.contactText}>{hoveredNode.metadata.email}</span>
                                </div>
                                <div style={styles.contactRow}>
                                    <span style={styles.contactIcon}>☎</span>
                                    <span style={styles.contactText}>{hoveredNode.metadata.phone}</span>
                                </div>
                            </div>
                        )}

                        {/* Stats */}
                        <div style={styles.statsGrid}>
                            <div style={styles.statCard}>
                                <span style={styles.statLabel}>Trust Score</span>
                                <span style={styles.statValue}>
                                    {hoveredNode.val ? parseFloat(hoveredNode.val).toFixed(1) : '0.0'}
                                </span>
                            </div>
                            <div style={styles.statCard}>
                                <span style={styles.statLabel}>Connections</span>
                                <span style={styles.statValue}>
                                    {hoveredNode.degree ?? '?'}
                                </span>
                            </div>
                        </div>
                    </div>
                ) : (
                    <div style={styles.emptyState}>
                        <div style={styles.emptyIcon}>
                            <svg width="40" height="40" viewBox="0 0 24 24" fill="none">
                                <circle cx="12" cy="12" r="10" stroke="#334155" strokeWidth="1.5" />
                                <circle cx="12" cy="12" r="4" stroke="#5aaf80" strokeWidth="1.5" />
                                <path d="M12 2V4M12 20V22M2 12H4M20 12H22" stroke="#334155" strokeWidth="1.5" strokeLinecap="round" />
                            </svg>
                        </div>
                        <span style={styles.emptyText}>Hover over a node to explore</span>
                    </div>
                )}
            </div>

            {/* Scrollable Lists */}
            <div style={styles.scrollArea}>
                {/* Sentinels */}
                <section style={styles.section}>
                    <div style={styles.sectionHeader}>
                        <div style={styles.sectionTitleWrapper}>
                            <span style={styles.sectionIcon}>★</span>
                            <h2 style={styles.sectionTitle}>Sentinels</h2>
                        </div>
                        <span style={styles.sectionCount}>{sentinelList.length}</span>
                    </div>
                    <p style={styles.sectionDesc}>Who to reach out to for the most new introductions</p>

                    <div style={styles.list}>
                        {sentinelList.map((node: any, i: number) => (
                            <div
                                key={node.id}
                                style={styles.listItem}
                            >
                                <span style={{ ...styles.rank, color: '#fbbf24' }}>{i + 1}</span>
                                <div style={styles.itemContent}>
                                    <span style={styles.itemName}>{node.metadata?.name || `Node ${node.id}`}</span>
                                    <span style={styles.itemMeta}>{node.metadata?.job || 'Network Node'}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </section>

                {/* Maintenance */}
                <section style={styles.section}>
                    <div style={styles.sectionHeader}>
                        <div style={styles.sectionTitleWrapper}>
                            <span style={{ ...styles.sectionIcon, color: '#fb7185' }}>●</span>
                            <h2 style={{ ...styles.sectionTitle, color: '#fb7185' }}>Maintenance</h2>
                        </div>
                        <span style={{ ...styles.sectionCount, background: 'rgba(251, 113, 133, 0.15)', color: '#fb7185' }}>
                            {maintenanceList.length}
                        </span>
                    </div>
                    <p style={styles.sectionDesc}>Valuable contacts you haven't talked to in a while</p>

                    <div style={styles.list}>
                        {maintenanceList.map((node: any, i: number) => (
                            <div
                                key={node.id}
                                style={styles.listItem}
                            >
                                <span style={{ ...styles.rank, color: '#fb7185' }}>{i + 1}</span>
                                <div style={styles.itemContent}>
                                    <span style={styles.itemName}>{node.metadata?.name || `Node ${node.id}`}</span>
                                    <span style={styles.itemMeta}>{node.days_dormant} days since contact</span>
                                </div>
                                <span style={styles.dormantBadge}>{node.days_dormant}d</span>
                            </div>
                        ))}
                    </div>
                </section>
            </div>

            {/* Footer */}
            <footer style={styles.footer}>
                <span style={styles.footerText}>VC Network Optimization Tool</span>
            </footer>
        </aside>
    );
}

const styles: { [key: string]: React.CSSProperties } = {
    panel: {
        width: 380,
        height: '100%',
        background: 'linear-gradient(180deg, rgba(15, 23, 42, 0.98) 0%, rgba(10, 35, 26, 0.98) 100%)',
        backdropFilter: 'blur(20px)',
        borderLeft: '1px solid rgba(90, 175, 128, 0.15)',
        display: 'flex',
        flexDirection: 'column',
        flexShrink: 0,
        boxShadow: '-8px 0 32px rgba(0, 0, 0, 0.4), inset 1px 0 0 rgba(255, 255, 255, 0.03)',
        zIndex: 10,
        position: 'relative',
        overflow: 'hidden'
    },
    loadingContainer: {
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '16px'
    },
    spinner: {
        width: '40px',
        height: '40px',
        borderRadius: '50%',
        border: '3px solid rgba(90, 175, 128, 0.2)',
        borderTopColor: '#5aaf80',
        animation: 'spin 1s linear infinite'
    },
    loadingText: {
        color: '#94a3b8',
        fontSize: '14px',
        fontWeight: 500
    },
    header: {
        padding: '24px',
        borderBottom: '1px solid rgba(90, 175, 128, 0.1)',
        display: 'flex',
        alignItems: 'center',
        gap: '16px',
        background: 'linear-gradient(180deg, rgba(26, 77, 50, 0.1) 0%, transparent 100%)'
    },
    logoContainer: {
        width: '44px',
        height: '44px',
        borderRadius: '12px',
        background: 'linear-gradient(135deg, rgba(90, 175, 128, 0.15), rgba(26, 77, 50, 0.25))',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        border: '1px solid rgba(90, 175, 128, 0.2)'
    },
    logo: {
        filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.2))'
    },
    title: {
        fontSize: '18px',
        fontWeight: 700,
        color: '#f8fafc',
        margin: 0,
        letterSpacing: '-0.02em',
        fontFamily: 'var(--font-display), Georgia, serif'
    },
    subtitle: {
        fontSize: '12px',
        color: '#5aaf80',
        margin: 0,
        marginTop: '2px',
        fontWeight: 500,
        letterSpacing: '0.05em',
        textTransform: 'uppercase'
    },
    legend: {
        padding: '14px 24px',
        display: 'flex',
        gap: '20px',
        borderBottom: '1px solid rgba(90, 175, 128, 0.08)',
        background: 'rgba(0, 0, 0, 0.15)'
    },
    legendItem: {
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        fontSize: '12px',
        color: '#94a3b8',
        fontWeight: 500
    },
    legendDot: {
        width: '8px',
        height: '8px',
        borderRadius: '50%',
        boxShadow: '0 0 8px rgba(255,255,255,0.2)'
    },
    detailsCard: {
        margin: '20px',
        padding: '20px',
        borderRadius: '16px',
        background: 'linear-gradient(135deg, rgba(26, 77, 50, 0.15), rgba(15, 23, 42, 0.4))',
        border: '1px solid rgba(90, 175, 128, 0.12)',
        minHeight: '180px',
        display: 'flex',
        flexDirection: 'column',
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.03)'
    },
    detailsContent: {
        display: 'flex',
        flexDirection: 'column',
        gap: '16px',
        animation: 'fadeIn 0.3s ease-out'
    },
    detailsHeader: {
        display: 'flex',
        alignItems: 'center',
        gap: '14px'
    },
    avatar: {
        width: '52px',
        height: '52px',
        borderRadius: '14px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        border: '2px solid',
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)'
    },
    nodeName: {
        fontSize: '16px',
        fontWeight: 700,
        color: '#f8fafc',
        margin: 0,
        letterSpacing: '-0.01em'
    },
    nodeRole: {
        fontSize: '13px',
        color: '#64748b',
        marginTop: '2px',
        display: 'block'
    },
    badge: {
        width: '28px',
        height: '28px',
        borderRadius: '8px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: '#fff',
        fontWeight: 700,
        fontSize: '14px',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.3)'
    },
    contactInfo: {
        padding: '12px',
        borderRadius: '10px',
        background: 'rgba(0, 0, 0, 0.2)',
        display: 'flex',
        flexDirection: 'column',
        gap: '8px'
    },
    contactRow: {
        display: 'flex',
        alignItems: 'center',
        gap: '10px'
    },
    contactIcon: {
        fontSize: '14px',
        color: '#5aaf80'
    },
    contactText: {
        fontSize: '13px',
        color: '#cbd5e1'
    },
    statsGrid: {
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '12px'
    },
    statCard: {
        padding: '14px',
        borderRadius: '10px',
        background: 'rgba(0, 0, 0, 0.25)',
        border: '1px solid rgba(90, 175, 128, 0.1)',
        display: 'flex',
        flexDirection: 'column',
        gap: '6px'
    },
    statLabel: {
        fontSize: '11px',
        color: '#64748b',
        textTransform: 'uppercase',
        letterSpacing: '0.06em',
        fontWeight: 600
    },
    statValue: {
        fontSize: '20px',
        fontWeight: 700,
        color: '#5aaf80',
        fontFamily: 'var(--font-display), Georgia, serif'
    },
    emptyState: {
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '16px',
        opacity: 0.7
    },
    emptyIcon: {
        opacity: 0.6
    },
    emptyText: {
        fontSize: '14px',
        color: '#64748b',
        fontWeight: 500
    },
    scrollArea: {
        flex: 1,
        overflowY: 'auto',
        padding: '8px 0'
    },
    section: {
        padding: '20px 20px 24px 20px'
    },
    sectionHeader: {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '6px'
    },
    sectionTitleWrapper: {
        display: 'flex',
        alignItems: 'center',
        gap: '8px'
    },
    sectionIcon: {
        fontSize: '14px',
        color: '#fbbf24'
    },
    sectionTitle: {
        fontSize: '14px',
        fontWeight: 700,
        color: '#fbbf24',
        margin: 0,
        textTransform: 'uppercase',
        letterSpacing: '0.04em'
    },
    sectionCount: {
        fontSize: '11px',
        fontWeight: 700,
        color: '#fbbf24',
        background: 'rgba(251, 191, 36, 0.15)',
        padding: '3px 8px',
        borderRadius: '6px'
    },
    sectionDesc: {
        fontSize: '13px',
        color: '#64748b',
        marginBottom: '16px',
        lineHeight: 1.5
    },
    list: {
        display: 'flex',
        flexDirection: 'column',
        gap: '8px'
    },
    listItem: {
        display: 'flex',
        alignItems: 'center',
        padding: '14px 16px',
        borderRadius: '12px',
        background: 'rgba(255, 255, 255, 0.02)',
        border: '1px solid rgba(255, 255, 255, 0.06)',
        width: '100%'
    },
    rank: {
        width: '28px',
        fontSize: '13px',
        fontWeight: 700,
        fontFamily: 'monospace'
    },
    itemContent: {
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        gap: '2px'
    },
    itemName: {
        fontSize: '14px',
        fontWeight: 600,
        color: '#f1f5f9'
    },
    itemMeta: {
        fontSize: '12px',
        color: '#64748b'
    },
    viewBtn: {
        fontSize: '12px',
        fontWeight: 600,
        opacity: 0.8
    },
    dormantBadge: {
        fontSize: '12px',
        fontWeight: 700,
        color: '#fb7185',
        background: 'rgba(251, 113, 133, 0.15)',
        padding: '4px 10px',
        borderRadius: '6px'
    },
    footer: {
        padding: '16px 24px',
        borderTop: '1px solid rgba(90, 175, 128, 0.08)',
        textAlign: 'center',
        background: 'rgba(0, 0, 0, 0.15)'
    },
    footerText: {
        fontSize: '11px',
        color: '#475569',
        fontWeight: 500,
        letterSpacing: '0.04em'
    }
};
