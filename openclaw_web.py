#!/usr/bin/env python3
"""
APEX Super Pro OpenClaw — Web Studio & Interactive Mobile Interface v20.0
Self-contained single-page dashboard & streaming chat interface on http://127.0.0.1:18800.
Operator: Casey Barton / GlacierEQ | Holographic Mesh Engine
Features: Real-Time SSE Token Streaming, Markdown + Code Highlighting, Copy Controls, Agent Presets
"""

import sys
import os
import json
import time
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
from openclaw_core import SuperProOpenClaw, PROVIDERS, CASES

PORT = 18800
claw = SuperProOpenClaw()

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>OpenClaw Pro — Holographic Mesh Studio</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/marked/12.0.1/marked.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
  <style>
    :root {
      --bg-base: #0a0f1d;
      --bg-panel: #10192e;
      --bg-card: #15223e;
      --border: #1e3a5f;
      --accent: #00ffcc;
      --accent-glow: rgba(0, 255, 204, 0.25);
      --accent-magenta: #ff007f;
      --text: #e2e8f0;
      --text-dim: #94a3b8;
      --success: #10b981;
      --warning: #f59e0b;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace; }
    body { background: var(--bg-base); color: var(--text); display: flex; height: 100vh; overflow: hidden; }
    
    /* Sidebar */
    .sidebar { width: 320px; background: var(--bg-panel); border-right: 1px solid var(--border); display: flex; flex-direction: column; }
    .sidebar-header { padding: 18px; border-bottom: 1px solid var(--border); display: flex; align-items: center; gap: 12px; }
    .brand-icon { font-size: 24px; color: var(--accent); text-shadow: 0 0 10px var(--accent); }
    .brand-title { font-weight: 700; font-size: 16px; letter-spacing: 0.5px; }
    .brand-subtitle { font-size: 11px; color: var(--text-dim); }
    
    .nav-tabs { display: flex; flex-direction: column; padding: 12px; gap: 6px; }
    .tab-btn { background: transparent; border: 1px solid transparent; color: var(--text-dim); padding: 10px 14px; border-radius: 8px; cursor: pointer; text-align: left; display: flex; align-items: center; gap: 10px; font-size: 13px; font-weight: 600; transition: all 0.2s; }
    .tab-btn:hover { background: var(--bg-card); color: var(--text); }
    .tab-btn.active { background: var(--bg-card); border-color: var(--accent); color: var(--accent); box-shadow: 0 0 10px var(--accent-glow); }
    
    .status-panel { margin-top: auto; padding: 16px; border-top: 1px solid var(--border); font-size: 12px; }
    .stat-badge { display: inline-flex; align-items: center; gap: 6px; background: rgba(16, 185, 129, 0.15); color: var(--success); padding: 4px 8px; border-radius: 6px; font-weight: bold; margin-bottom: 8px; }
    
    /* Main Content Area */
    .main { flex: 1; display: flex; flex-direction: column; overflow: hidden; background: var(--bg-base); }
    .tab-content { display: none; flex: 1; flex-direction: column; overflow: hidden; }
    .tab-content.active { display: flex; }
    
    /* Top Bar */
    .topbar { padding: 12px 20px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; background: var(--bg-panel); }
    .model-selector { display: flex; align-items: center; gap: 10px; font-size: 13px; }
    select { background: var(--bg-card); color: var(--text); border: 1px solid var(--border); padding: 6px 12px; border-radius: 6px; outline: none; }
    
    /* Chat Container */
    .chat-container { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
    .chat-messages { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 16px; scroll-behavior: smooth; }
    .message { display: flex; gap: 12px; max-width: 88%; }
    .message.user { align-self: flex-end; flex-direction: row-reverse; }
    .message-avatar { width: 34px; height: 34px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 14px; flex-shrink: 0; }
    .message.user .message-avatar { background: #3b82f6; color: #fff; }
    .message.assistant .message-avatar { background: var(--accent); color: #000; box-shadow: 0 0 10px var(--accent-glow); }
    .message-content { display: flex; flex-direction: column; max-width: 100%; }
    .message-body { background: var(--bg-panel); border: 1px solid var(--border); border-radius: 10px; padding: 14px 18px; font-size: 14px; line-height: 1.6; word-break: break-word; }
    .message.user .message-body { background: #1e3a8a; border-color: #3b82f6; }
    
    /* Markdown inside messages */
    .message-body pre { background: #070c18; padding: 12px; border-radius: 8px; overflow-x: auto; margin: 10px 0; border: 1px solid var(--border); position: relative; }
    .message-body code { font-family: "JetBrains Mono", Consolas, monospace; font-size: 13px; }
    .message-body p { margin-bottom: 8px; }
    .message-body p:last-child { margin-bottom: 0; }
    .message-body ul, .message-body ol { margin-left: 20px; margin-bottom: 8px; }
    .message-body table { border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 13px; }
    .message-body th, .message-body td { border: 1px solid var(--border); padding: 6px 10px; text-align: left; }
    .message-body th { background: var(--bg-card); color: var(--accent); }
    .message-body blockquote { border-left: 3px solid var(--accent); padding-left: 12px; color: var(--text-dim); margin: 8px 0; }
    
    .message-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; font-size: 11px; }
    .message-tag { font-weight: bold; color: var(--accent); }
    .copy-btn { background: transparent; border: none; color: var(--text-dim); cursor: pointer; font-size: 12px; padding: 2px 6px; border-radius: 4px; }
    .copy-btn:hover { color: var(--accent); background: var(--bg-card); }
    
    /* Input Area */
    .chat-input-area { padding: 16px 20px; background: var(--bg-panel); border-top: 1px solid var(--border); display: flex; gap: 12px; align-items: center; }
    .chat-input { flex: 1; background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; color: #fff; padding: 12px 16px; font-size: 14px; outline: none; }
    .chat-input:focus { border-color: var(--accent); box-shadow: 0 0 8px var(--accent-glow); }
    .btn { background: var(--accent); color: #000; font-weight: bold; border: none; border-radius: 8px; padding: 12px 20px; cursor: pointer; display: flex; align-items: center; gap: 8px; transition: all 0.2s; white-space: nowrap; }
    .btn:hover { opacity: 0.9; transform: translateY(-1px); }
    .btn-secondary { background: var(--bg-card); color: var(--text); border: 1px solid var(--border); }
    .btn-secondary:hover { border-color: var(--accent); color: var(--accent); }
    
    /* Cards & Grids */
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; padding: 20px; overflow-y: auto; }
    .card { background: var(--bg-panel); border: 1px solid var(--border); border-radius: 10px; padding: 18px; }
    .card-title { font-size: 14px; font-weight: 700; color: var(--accent); margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }
    .card-body { font-size: 13px; line-height: 1.6; }
    
    /* Action Buttons */
    .action-btn { background: var(--bg-card); border: 1px solid var(--border); color: #fff; padding: 10px 14px; border-radius: 6px; cursor: pointer; text-align: left; width: 100%; margin-bottom: 8px; font-size: 12px; display: flex; align-items: center; gap: 8px; transition: all 0.2s; }
    .action-btn:hover { border-color: var(--accent); color: var(--accent); }
    
    /* Search Box */
    .search-bar { width: 100%; padding: 12px; background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; color: #fff; margin-bottom: 16px; font-size: 14px; outline: none; }
    .search-bar:focus { border-color: var(--accent); box-shadow: 0 0 8px var(--accent-glow); }
    
    /* Notification Toast */
    #ui-toast { position: fixed; bottom: 20px; right: 20px; background: var(--bg-card); border: 1px solid var(--accent); color: #fff; padding: 12px 20px; border-radius: 8px; display: none; z-index: 9999; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }

    /* Collapsible Autonomous Tool Cards */
    .tool-card { background: #0c1628; border: 1px solid #1e3a5f; border-radius: 8px; margin: 8px 0; overflow: hidden; font-size: 13px; transition: all 0.2s ease; }
    .tool-card.running { border-color: var(--accent); box-shadow: 0 0 10px var(--accent-glow); }
    .tool-card.complete { border-color: #10b981; }
    .tool-card.error { border-color: #ef4444; }
    .tool-header { display: flex; align-items: center; gap: 10px; padding: 8px 12px; background: rgba(30, 58, 95, 0.4); cursor: pointer; user-select: none; }
    .tool-header:hover { background: rgba(30, 58, 95, 0.7); }
    .tool-icon { font-size: 13px; color: var(--accent); width: 16px; text-align: center; }
    .tool-name { font-weight: 700; color: var(--accent); font-family: monospace; font-size: 12px; }
    .tool-thought { color: var(--text-dim); font-size: 11px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 320px; }
    .tool-badge { padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: bold; text-transform: uppercase; margin-left: auto; display: flex; align-items: center; gap: 4px; }
    .tool-badge.running { background: rgba(0, 255, 204, 0.2); color: var(--accent); }
    .tool-badge.complete { background: rgba(16, 185, 129, 0.2); color: #10b981; }
    .tool-badge.failed { background: rgba(239, 68, 68, 0.2); color: #ef4444; }
    .tool-body { padding: 10px 12px; background: #080d1a; border-top: 1px solid #1e3a5f; }
    .tool-args { font-size: 11px; color: var(--text-dim); margin-bottom: 6px; }
    .tool-args code { color: #38bdf8; background: #0f172a; padding: 2px 6px; border-radius: 4px; font-family: monospace; }
    .tool-output { font-family: "JetBrains Mono", Consolas, monospace; font-size: 11px; color: #cbd5e1; max-height: 220px; overflow-y: auto; white-space: pre-wrap; word-break: break-all; background: #050811; padding: 8px; border-radius: 6px; border: 1px solid #1e293b; margin: 0; }
    
    /* Quick Action Pills */
    .quick-pills-bar { padding: 8px 20px 0 20px; display: flex; gap: 8px; flex-wrap: wrap; background: var(--bg-panel); border-top: 1px solid var(--border); }
    .quick-pill { background: var(--bg-card); border: 1px solid var(--border); color: var(--text-dim); padding: 5px 12px; border-radius: 14px; font-size: 11px; cursor: pointer; transition: all 0.2s; display: inline-flex; align-items: center; gap: 6px; }
    .quick-pill:hover { border-color: var(--accent); color: var(--accent); background: rgba(0, 255, 204, 0.05); }

    /* Modal Overlay */
    .modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.75); display: none; align-items: center; justify-content: center; z-index: 10000; backdrop-filter: blur(4px); }
    .modal-content { background: var(--bg-panel); border: 1px solid var(--border); border-radius: 12px; width: 90%; max-width: 650px; max-height: 85vh; display: flex; flex-direction: column; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.8); }
    .modal-header { padding: 16px 20px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; font-weight: 700; font-size: 15px; }
    .modal-body { padding: 20px; overflow-y: auto; font-size: 13px; line-height: 1.6; }
  </style>
</head>
<body>
  <!-- Sidebar -->
  <div class="sidebar">
    <div class="sidebar-header">
      <i class="fa-solid fa-bolt brand-icon"></i>
      <div>
        <div class="brand-title">OPENCLAW PRO</div>
        <div class="brand-subtitle">APEX Holographic Mesh v20.0</div>
      </div>
    </div>
    
    <div class="nav-tabs">
      <button class="tab-btn active" onclick="switchTab('chat', this)"><i class="fa-solid fa-message"></i> Interactive Chat</button>
      <button class="tab-btn" onclick="switchTab('agent', this)"><i class="fa-solid fa-robot"></i> Autonomous Agent</button>
      <button class="tab-btn" onclick="switchTab('device', this)"><i class="fa-solid fa-mobile-screen"></i> Native Hardware</button>
      <button class="tab-btn" onclick="switchTab('forensics', this)"><i class="fa-solid fa-magnifying-glass"></i> FTS5 Chat Forensics</button>
      <button class="tab-btn" onclick="switchTab('legal', this)"><i class="fa-solid fa-scale-balanced"></i> Casebuilder 4000</button>
    </div>
    
    <div class="status-panel">
      <div class="stat-badge"><i class="fa-solid fa-circle-check"></i> MESH ONLINE</div>
      <div style="color: var(--text-dim); font-size: 11px;">
        <div><b>Node:</b> Android ARM64 PRoot</div>
        <div><b>Operator:</b> Casey Barton</div>
        <div><b>Doctrine:</b> Holographic Mesh</div>
        <div style="margin-top: 4px; color: var(--accent);"><b>Latency:</b> ~150ms FTS / Sub-Second LPU</div>
      </div>
    </div>
  </div>
  
  <!-- Main Content -->
  <div class="main">
    <div class="topbar">
      <div style="font-weight: 600; font-size: 14px;" id="current-view-title"><i class="fa-solid fa-message"></i> Interactive Chat Workspace</div>
      <div class="model-selector">
        <label style="color: var(--text-dim);">Mesh Route:</label>
        <select id="provider-select" onchange="updateProvider()">
          <option value="groq" selected>Groq (qwen3.8-27b - Sub-Second LPU)</option>
          <option value="google">Google (gemini-2.5-flash - 1M Context)</option>
          <option value="mistral">Mistral (codestral-latest - Elite Code)</option>
          <option value="openrouter">OpenRouter (Nemotron/Gemma Free)</option>
          <option value="cerebras">Cerebras (qwen-3.8-27b Ultra-Fast)</option>
        </select>
        <button id="auto-tools-btn" class="btn btn-secondary" onclick="toggleAutoTools()" style="padding: 6px 12px; font-size: 12px;" title="Toggle Autonomous Substrate Tools"><i class="fa-solid fa-wand-magic-sparkles" style="color: var(--accent);"></i> Tools: <span id="auto-tools-label" style="color: var(--accent); font-weight: bold;">ON</span></button>
        <button class="btn btn-secondary" onclick="openConnectorsModal()" style="padding: 6px 12px; font-size: 12px;" title="View Active Mesh Connectors"><i class="fa-solid fa-network-wired" style="color: var(--accent);"></i> Connectors</button>
        <button class="btn btn-secondary" style="padding: 6px 12px; font-size: 12px;" onclick="clearChat()"><i class="fa-solid fa-trash-can"></i> Clear</button>
      </div>
    </div>
    
    <!-- Tab 1: Chat -->
    <div id="tab-chat" class="tab-content active">
      <div class="chat-container">
        <div class="chat-messages" id="chat-msgs">
          <div class="message assistant">
            <div class="message-avatar"><i class="fa-solid fa-bolt"></i></div>
            <div class="message-content">
              <div class="message-header">
                <span class="message-tag">OPENCLAW PRO ONLINE</span>
              </div>
              <div class="message-body">Welcome, Operator Casey Barton. All 5 inference providers, hardware bridges, FTS5 forensics across 140,688 records, and Aspen-Grove quantum memory are online and synchronized. Real-time streaming is active. How can I assist you?</div>
            </div>
          </div>
        </div>
        <div class="quick-pills-bar">
          <button class="quick-pill" onclick="quickSend('What is my device hardware and battery status?')"><i class="fa-solid fa-battery-half"></i> Battery & Telemetry</button>
          <button class="quick-pill" onclick="quickSend('Search chat forensics for Natasha Shaw or Brower and summarize')"><i class="fa-solid fa-magnifying-glass"></i> Forensics: Shaw/Brower</button>
          <button class="quick-pill" onclick="quickSend('Search the web for latest Hawaii Supreme Court oral arguments')"><i class="fa-solid fa-globe"></i> Web: Hawaii Court</button>
          <button class="quick-pill" onclick="quickSend('List the python files in /root/antigravity-cli')"><i class="fa-solid fa-folder-tree"></i> Workspace Files</button>
          <button class="quick-pill" onclick="quickSend('Inspect 1FDV legal dossier, damages, and verified facts')"><i class="fa-solid fa-scale-balanced"></i> 1FDV Dossier</button>
        </div>
        <div class="chat-input-area">
          <input type="text" class="chat-input" id="chat-input" placeholder="Ask questions or type instructions (Autonomous Tools will execute automatically)..." onkeydown="if(event.key==='Enter') sendChat()">
          <button class="btn" id="send-btn" onclick="sendChat()"><i class="fa-solid fa-paper-plane"></i> Send</button>
        </div>
      </div>
    </div>

    <!-- Tab 2: Agent -->
    <div id="tab-agent" class="tab-content">
      <div class="grid" style="grid-template-columns: 1fr;">
        <div class="card">
          <div class="card-title"><i class="fa-solid fa-robot"></i> Multi-Step Autonomous Agent Loop</div>
          <p style="color: var(--text-dim); margin-bottom: 12px; font-size: 13px;">Execute complex goals autonomously across tools: Bash execution, File Read/Write, FTS5 Search, Device Hardware, and Aspen Memory.</p>
          
          <div style="display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap;">
            <button class="btn btn-secondary" style="font-size: 11px; padding: 6px 10px;" onclick="setAgentGoal('Check disk space and list active database processes')">💾 Disk & Databases</button>
            <button class="btn btn-secondary" style="font-size: 11px; padding: 6px 10px;" onclick="setAgentGoal('Search FTS5 chat records for ex parte communications and summarize')">🔍 FTS Ex Parte Audit</button>
            <button class="btn btn-secondary" style="font-size: 11px; padding: 6px 10px;" onclick="setAgentGoal('Inspect /root/LEGAL_WARFARE_PACKAGE_1FDV build receipt and count verified facts')">⚖️ 1FDV Facts Count</button>
            <button class="btn btn-secondary" style="font-size: 11px; padding: 6px 10px;" onclick="setAgentGoal('Query Aspen-Grove memory substrate for active indexed pointers')">🌲 Aspen Memory Check</button>
          </div>

          <div style="display: flex; gap: 10px;">
            <input type="text" class="search-bar" id="agent-task-input" placeholder="Enter autonomous mission goal..." style="margin-bottom: 0;">
            <button class="btn" id="agent-exec-btn" onclick="runAgentTask()"><i class="fa-solid fa-play"></i> Execute</button>
          </div>
        </div>
        
        <div class="card" id="agent-results-card" style="display: none;">
          <div class="card-title" style="justify-content: space-between;">
            <span><i class="fa-solid fa-list-check"></i> Execution Trace</span>
            <span id="agent-turns-badge" style="font-size: 12px; color: var(--accent);"></span>
          </div>
          <div id="agent-trace" style="font-size: 13px; line-height: 1.5; margin-bottom: 16px;"></div>
          <div id="agent-conclusion" style="padding: 14px; background: rgba(16, 185, 129, 0.15); border: 1px solid #10b981; border-radius: 8px; font-size: 14px;"></div>
        </div>
      </div>
    </div>

    <!-- Tab 3: Native Hardware -->
    <div id="tab-device" class="tab-content">
      <div class="grid">
        <div class="card">
          <div class="card-title"><i class="fa-solid fa-battery-half"></i> Hardware Telemetry</div>
          <div class="card-body" id="hw-telemetry" style="background: var(--bg-base); padding: 12px; border-radius: 8px; border: 1px solid var(--border);">Click "Refresh Telemetry" to pull real-time Android battery and CPU stats.</div>
          <button class="action-btn" onclick="fetchTelemetry()" style="margin-top: 12px;"><i class="fa-solid fa-rotate"></i> Refresh Telemetry</button>
        </div>
        <div class="card">
          <div class="card-title"><i class="fa-solid fa-bell"></i> Android Physical Controls</div>
          <button class="action-btn" onclick="triggerDevice('toast', 'OpenClaw Pro Web Studio Active')"><i class="fa-solid fa-comment-dots"></i> Display Android Toast</button>
          <button class="action-btn" onclick="triggerDevice('notify', 'APEX OpenClaw', 'Mission command executed successfully')"><i class="fa-solid fa-bell"></i> Send System Notification</button>
          <button class="action-btn" onclick="triggerDevice('vibrate', '400')"><i class="fa-solid fa-mobile"></i> Trigger Haptic Vibration (400ms)</button>
          <button class="action-btn" onclick="triggerDevice('speak', 'OpenClaw system operational')"><i class="fa-solid fa-volume-high"></i> Voice Speech Synthesis (TTS)</button>
          <button class="action-btn" onclick="triggerDevice('clipboard', 'status')"><i class="fa-solid fa-clipboard"></i> Inspect Android Clipboard</button>
        </div>
      </div>
    </div>

    <!-- Tab 4: FTS5 Forensics -->
    <div id="tab-forensics" class="tab-content">
      <div style="padding: 20px; overflow-y: auto; flex: 1;">
        <div style="display: flex; gap: 10px;">
          <input type="text" class="search-bar" id="fts-query" placeholder="Instant sub-second search across 140,688 chat records (~150ms)..." onkeydown="if(event.key==='Enter') searchFts()">
          <button class="btn" onclick="searchFts()" style="margin-bottom: 16px;"><i class="fa-solid fa-magnifying-glass"></i> Search</button>
        </div>
        <div id="fts-results"></div>
      </div>
    </div>

    <!-- Tab 5: Casebuilder 4000 -->
    <div id="tab-legal" class="tab-content">
      <div class="grid">
        <div class="card">
          <div class="card-title"><i class="fa-solid fa-folder-open"></i> 1FDV-23-0001009</div>
          <div class="card-body">
            <div><b>Title:</b> Barton Custody & Due Process Enforcement</div>
            <div><b>Damages:</b> $2,989,847.00</div>
            <div><b>Verified Facts:</b> 125</div>
            <div><b>Proof Score:</b> 75.0/100</div>
            <button class="action-btn" onclick="draftMotion('rule60b')" style="margin-top: 10px;"><i class="fa-solid fa-file-contract"></i> Draft Rule 60(b)(4) Motion</button>
          </div>
        </div>
        <div class="card">
          <div class="card-title"><i class="fa-solid fa-folder-open"></i> RICO & CFAA Dockets</div>
          <div class="card-body">
            <div><b>RICO Damages:</b> $56,386,460.00 (81 Facts)</div>
            <div><b>CFAA Damages:</b> $2,450,000.00 (60 Facts)</div>
            <div><b>Status:</b> Ready for filing assembly</div>
            <button class="action-btn" onclick="draftMotion('spoliation')" style="margin-top: 10px;"><i class="fa-solid fa-file-contract"></i> Draft Spoliation Sanctions Motion</button>
            <button class="action-btn" onclick="draftMotion('recusal')" style="margin-top: 6px;"><i class="fa-solid fa-gavel"></i> Draft Judicial Recusal Motion</button>
          </div>
        </div>
      </div>
      <div id="motion-preview-container" style="display: none; padding: 0 20px 20px 20px;">
        <div class="card">
          <div class="card-title" style="justify-content: space-between;">
            <span id="motion-preview-title"><i class="fa-solid fa-file-lines"></i> Motion Preview</span>
            <button class="btn btn-secondary" style="font-size: 11px; padding: 4px 8px;" onclick="copyMotionText()"><i class="fa-solid fa-copy"></i> Copy JSON</button>
          </div>
          <pre id="motion-preview-body" style="background: var(--bg-base); padding: 12px; border-radius: 8px; overflow-x: auto; font-size: 12px;"></pre>
        </div>
      </div>
    </div>
  </div>

  <div id="ui-toast">Notification</div>

  <!-- Connectors Status Modal -->
  <div class="modal-overlay" id="connectors-modal" onclick="if(event.target===this) closeConnectorsModal()">
    <div class="modal-content">
      <div class="modal-header">
        <span><i class="fa-solid fa-network-wired" style="color: var(--accent);"></i> Holographic Mesh Connectors & Substrate Nodes</span>
        <button class="copy-btn" onclick="closeConnectorsModal()"><i class="fa-solid fa-xmark"></i></button>
      </div>
      <div class="modal-body" id="connectors-modal-body">
        <div style="display: flex; flex-direction: column; gap: 12px;">
          <div style="background: var(--bg-card); padding: 12px; border-radius: 8px; border: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between;">
            <div>
              <div style="font-weight: bold; color: var(--accent);"><i class="fa-solid fa-bolt"></i> Groq LPU Engine</div>
              <div style="color: var(--text-dim); font-size: 11px;">Primary Sub-Second Inference | Model: <code>qwen/qwen3.8-27b</code></div>
            </div>
            <span class="tool-badge complete"><i class="fa-solid fa-circle-check"></i> ONLINE</span>
          </div>

          <div style="background: var(--bg-card); padding: 12px; border-radius: 8px; border: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between;">
            <div>
              <div style="font-weight: bold; color: #60a5fa;"><i class="fa-solid fa-brain"></i> Google Gemini</div>
              <div style="color: var(--text-dim); font-size: 11px;">1M Token Context Cascade | Model: <code>gemini-2.5-flash</code></div>
            </div>
            <span class="tool-badge complete"><i class="fa-solid fa-circle-check"></i> ONLINE</span>
          </div>

          <div style="background: var(--bg-card); padding: 12px; border-radius: 8px; border: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between;">
            <div>
              <div style="font-weight: bold; color: #f59e0b;"><i class="fa-solid fa-code"></i> Mistral AI</div>
              <div style="color: var(--text-dim); font-size: 11px;">Elite Code Reasoning | Model: <code>codestral-latest</code></div>
            </div>
            <span class="tool-badge complete"><i class="fa-solid fa-circle-check"></i> ONLINE</span>
          </div>

          <div style="background: var(--bg-card); padding: 12px; border-radius: 8px; border: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between;">
            <div>
              <div style="font-weight: bold; color: #a855f7;"><i class="fa-solid fa-share-nodes"></i> OpenRouter Free Mesh</div>
              <div style="color: var(--text-dim); font-size: 11px;">Decentralized Fallback | Model: <code>nvidia/nemotron-3-nano</code></div>
            </div>
            <span class="tool-badge complete"><i class="fa-solid fa-circle-check"></i> ONLINE</span>
          </div>

          <div style="background: var(--bg-card); padding: 12px; border-radius: 8px; border: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between;">
            <div>
              <div style="font-weight: bold; color: #10b981;"><i class="fa-solid fa-database"></i> SQLite Chat Forensics</div>
              <div style="color: var(--text-dim); font-size: 11px;">140,688 Messages | FTS5 Indexing (~150ms Speed)</div>
            </div>
            <span class="tool-badge complete"><i class="fa-solid fa-circle-check"></i> 140,688 ROWS</span>
          </div>

          <div style="background: var(--bg-card); padding: 12px; border-radius: 8px; border: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between;">
            <div>
              <div style="font-weight: bold; color: #34d399;"><i class="fa-solid fa-tree"></i> Aspen-Grove Quantum Memory</div>
              <div style="color: var(--text-dim); font-size: 11px;">Daemon Port 8787 | Pointer-Indexed Substrate Persistence</div>
            </div>
            <span class="tool-badge complete"><i class="fa-solid fa-circle-check"></i> 407 POINTERS</span>
          </div>

          <div style="background: var(--bg-card); padding: 12px; border-radius: 8px; border: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between;">
            <div>
              <div style="font-weight: bold; color: #f43f5e;"><i class="fa-solid fa-mobile-screen"></i> Android Native Hardware API</div>
              <div style="color: var(--text-dim); font-size: 11px;">Termux API Bridge | Battery, Toast, Notifications, TTS, Vibration</div>
            </div>
            <span class="tool-badge complete"><i class="fa-solid fa-circle-check"></i> CONNECTED</span>
          </div>

          <div style="background: var(--bg-card); padding: 12px; border-radius: 8px; border: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between;">
            <div>
              <div style="font-weight: bold; color: #38bdf8;"><i class="fa-solid fa-globe"></i> Live Web Search Connector</div>
              <div style="color: var(--text-dim); font-size: 11px;">DuckDuckGo Lite Extractor | Real-Time Web Intelligence</div>
            </div>
            <span class="tool-badge complete"><i class="fa-solid fa-circle-check"></i> ACTIVE</span>
          </div>
        </div>
      </div>
    </div>
  </div>

  <script>
    let activeTab = 'chat';
    let currentProvider = 'groq';
    let lastMotionData = null;
    let autoTools = true;
    window.forensicSnippets = [];

    function toggleAutoTools() {
      autoTools = !autoTools;
      const label = document.getElementById('auto-tools-label');
      if (autoTools) {
        if (label) { label.innerText = 'ON'; label.style.color = 'var(--accent)'; }
        showToast('Autonomous Tools: ENABLED');
      } else {
        if (label) { label.innerText = 'OFF'; label.style.color = 'var(--text-dim)'; }
        showToast('Autonomous Tools: DISABLED (Direct LLM)');
      }
    }

    function openConnectorsModal() {
      const m = document.getElementById('connectors-modal');
      if (m) m.style.display = 'flex';
    }

    function closeConnectorsModal() {
      const m = document.getElementById('connectors-modal');
      if (m) m.style.display = 'none';
    }

    function quickSend(promptText) {
      const input = document.getElementById('chat-input');
      if (input) {
        input.value = promptText;
        sendChat();
      }
    }

    function toggleToolCard(toolId) {
      const body = document.getElementById(toolId + '-body');
      const card = document.getElementById(toolId);
      if (body) {
        const isHidden = body.style.display === 'none';
        body.style.display = isHidden ? 'block' : 'none';
        const toggleIcon = card ? card.querySelector('.tool-toggle') : null;
        if (toggleIcon) {
          toggleIcon.className = isHidden ? 'fa-solid fa-chevron-up tool-toggle' : 'fa-solid fa-chevron-down tool-toggle';
        }
      }
    }

    // Safe Markdown setup with fallbacks
    if (typeof marked !== 'undefined' && typeof marked.setOptions === 'function') {
      try {
        marked.setOptions({
          highlight: function(code, lang) {
            if (typeof hljs !== 'undefined' && lang && hljs.getLanguage && hljs.getLanguage(lang)) {
              try { return hljs.highlight(code, { language: lang }).value; } catch (__) {}
            }
            if (typeof hljs !== 'undefined' && typeof hljs.highlightAuto === 'function') {
              try { return hljs.highlightAuto(code).value; } catch (__) {}
            }
            return code;
          },
          breaks: true
        });
      } catch (e) {
        console.warn('Marked options setup error:', e);
      }
    }

    function renderMarkdown(text) {
      if (typeof marked !== 'undefined' && typeof marked.parse === 'function') {
        try {
          return marked.parse(text);
        } catch (e) {
          console.warn('Markdown parse error:', e);
        }
      }
      return '<p>' + escapeHtml(text).split(String.fromCharCode(10)).join('<br>') + '</p>';
    }

    function showToast(msg) {
      const t = document.getElementById('ui-toast');
      if (!t) return;
      t.innerText = msg;
      t.style.display = 'block';
      setTimeout(() => { t.style.display = 'none'; }, 3000);
    }

    function switchTab(tabId, el) {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      if (el) {
        el.classList.add('active');
        const titleElem = document.getElementById('current-view-title');
        if (titleElem) titleElem.innerHTML = el.innerHTML;
      }
      const target = document.getElementById('tab-' + tabId);
      if (target) target.classList.add('active');
      activeTab = tabId;
      if (tabId === 'device') fetchTelemetry();
    }

    function updateProvider() {
      const sel = document.getElementById('provider-select');
      if (sel) {
        currentProvider = sel.value;
        showToast('Mesh provider switched to: ' + currentProvider.toUpperCase());
      }
    }

    function clearChat() {
      const container = document.getElementById('chat-msgs');
      if (container) container.innerHTML = '';
      showToast('Chat history cleared');
    }

    function copyToClipboard(text) {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(() => {
          showToast('Copied to clipboard!');
        }).catch(err => {
          fallbackCopy(text);
        });
      } else {
        fallbackCopy(text);
      }
    }

    function fallbackCopy(text) {
      const ta = document.createElement('textarea');
      ta.value = text;
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.focus();
      ta.select();
      try {
        document.execCommand('copy');
        showToast('Copied to clipboard!');
      } catch (err) {
        showToast('Copy failed: ' + err);
      }
      document.body.removeChild(ta);
    }

    function escapeHtml(str) {
      if (!str) return '';
      return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
    }

    async function sendChat() {
      const input = document.getElementById('chat-input');
      const sendBtn = document.getElementById('send-btn');
      const text = input ? input.value.trim() : '';
      if (!text) return;
      if (input) input.value = '';

      if (sendBtn) {
        sendBtn.disabled = true;
        sendBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Thinking...';
      }

      const container = document.getElementById('chat-msgs');
      const userDiv = document.createElement('div');
      userDiv.className = 'message user';
      userDiv.innerHTML = `
        <div class="message-avatar"><i class="fa-solid fa-user"></i></div>
        <div class="message-content">
          <div class="message-body">${escapeHtml(text)}</div>
        </div>
      `;
      container.appendChild(userDiv);

      const msgId = 'msg-' + Date.now();
      const asstDiv = document.createElement('div');
      asstDiv.className = 'message assistant';
      asstDiv.id = msgId;
      asstDiv.innerHTML = `
        <div class="message-avatar"><i class="fa-solid fa-bolt"></i></div>
        <div class="message-content">
          <div class="message-header">
            <span class="message-tag" id="${msgId}-tag">[${currentProvider.toUpperCase()} / INITIALIZING...]</span>
            <button class="copy-btn" onclick="copyMessage('${msgId}')"><i class="fa-solid fa-copy"></i> Copy</button>
          </div>
          <div class="message-body" id="${msgId}-body">
            <div id="${msgId}-tools"></div>
            <div id="${msgId}-text"><i class="fa-solid fa-spinner fa-spin"></i> Routing query through holographic mesh...</div>
          </div>
        </div>
      `;
      container.appendChild(asstDiv);
      container.scrollTop = container.scrollHeight;

      const bodyElem = document.getElementById(msgId + '-body');
      const toolsElem = document.getElementById(msgId + '-tools');
      const textElem = document.getElementById(msgId + '-text');
      const tagElem = document.getElementById(msgId + '-tag');
      let rawAccumulated = '';
      let streamWorked = false;
      const activeToolCards = {};

      try {
        const resp = await fetch('/api/chat/stream', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({prompt: text, provider: currentProvider, enable_tools: autoTools})
        });

        if (resp.body && resp.status === 200) {
          const reader = resp.body.getReader();
          const decoder = new TextDecoder();
          let buffer = '';

          while (true) {
            const {done, value} = await reader.read();
            if (done) break;
            buffer += decoder.decode(value, {stream: true});
            const lines = buffer.split(String.fromCharCode(10));
            buffer = lines.pop() || '';

            for (let i = 0; i < lines.length; i++) {
              const trimmed = lines[i].trim();
              if (trimmed.startsWith('data: ')) {
                const jsonStr = trimmed.slice(6);
                try {
                  const data = JSON.parse(jsonStr);

                  if (data.type === 'tool_start') {
                    streamWorked = true;
                    if (textElem) textElem.innerHTML = '';
                    const toolId = 'tool-' + Date.now() + '-' + Math.floor(Math.random() * 1000);
                    const toolCard = document.createElement('div');
                    toolCard.className = 'tool-card running';
                    toolCard.id = toolId;
                    const argsStr = data.args ? JSON.stringify(data.args) : '';
                    toolCard.innerHTML = `
                      <div class="tool-header" onclick="toggleToolCard('${toolId}')">
                        <i class="fa-solid fa-gear fa-spin tool-icon"></i>
                        <span class="tool-name">${escapeHtml(data.tool)}</span>
                        ${data.thought ? `<span class="tool-thought">${escapeHtml(data.thought)}</span>` : ''}
                        <span class="tool-badge running"><i class="fa-solid fa-circle-notch fa-spin"></i> Running</span>
                        <i class="fa-solid fa-chevron-down tool-toggle" style="margin-left: 8px;"></i>
                      </div>
                      <div class="tool-body" id="${toolId}-body" style="display: none;">
                        ${argsStr ? `<div class="tool-args"><b>Params:</b> <code>${escapeHtml(argsStr)}</code></div>` : ''}
                        <pre class="tool-output">Executing tool on substrate...</pre>
                      </div>
                    `;
                    toolsElem.appendChild(toolCard);
                    activeToolCards[data.tool + '_' + (data.turn || 1)] = toolId;
                    container.scrollTop = container.scrollHeight;
                  }

                  else if (data.type === 'tool_end') {
                    const toolId = activeToolCards[data.tool + '_' + (data.turn || 1)] || Object.values(activeToolCards).pop();
                    const card = toolId ? document.getElementById(toolId) : null;
                    if (card) {
                      card.classList.remove('running');
                      card.classList.add(data.success ? 'complete' : 'error');
                      const icon = card.querySelector('.tool-icon');
                      if (icon) {
                        icon.className = data.success ? 'fa-solid fa-circle-check tool-icon' : 'fa-solid fa-triangle-exclamation tool-icon';
                        icon.style.color = data.success ? '#10b981' : '#ef4444';
                      }
                      const badge = card.querySelector('.tool-badge');
                      if (badge) {
                        badge.className = 'tool-badge ' + (data.success ? 'complete' : 'failed');
                        badge.innerHTML = data.success ? '<i class="fa-solid fa-check"></i> Complete' : '<i class="fa-solid fa-xmark"></i> Failed';
                      }
                      const outElem = card.querySelector('.tool-output');
                      if (outElem) {
                        outElem.innerText = data.full_output || data.output || '(No output)';
                      }
                    }
                    container.scrollTop = container.scrollHeight;
                  }

                  else if (data.type === 'token' || data.token !== undefined) {
                    if (!streamWorked) {
                      if (textElem) textElem.innerHTML = '';
                      streamWorked = true;
                    }
                    rawAccumulated += data.token;
                    if (textElem) textElem.innerHTML = renderMarkdown(rawAccumulated);
                    if (data.tag && tagElem) tagElem.innerText = data.tag;
                    container.scrollTop = container.scrollHeight;
                  }

                  else if (data.type === 'done' || data.done) {
                    const elSec = data.elapsed ? Number(data.elapsed).toFixed(2) : '0.00';
                    const toolCount = data.tools_count !== undefined ? data.tools_count : (data.tools_used || 0);
                    if (tagElem) {
                      const baseTag = data.tag || `[${currentProvider.toUpperCase()}]`;
                      tagElem.innerText = `${baseTag} (${elSec}s | ${toolCount} tools)`;
                    }
                  }
                } catch(e) {}
              }
            }
          }
        }
      } catch (err) {
        console.warn('Streaming error, falling back to sync API:', err);
      }

      if (!streamWorked) {
        try {
          const fallbackResp = await fetch('/api/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({prompt: text, provider: currentProvider, enable_tools: autoTools})
          });
          const data = await fallbackResp.json();
          if (data.trace && data.trace.length > 0) {
            toolsElem.innerHTML = '';
            data.trace.forEach(t => {
              if (t.status === 'completed') {
                const toolCard = document.createElement('div');
                toolCard.className = 'tool-card complete';
                const toolId = 'tool-fb-' + Math.floor(Math.random() * 1000);
                toolCard.innerHTML = `
                  <div class="tool-header" onclick="toggleToolCard('${toolId}')">
                    <i class="fa-solid fa-circle-check tool-icon" style="color: #10b981;"></i>
                    <span class="tool-name">${escapeHtml(t.tool)}</span>
                    <span class="tool-badge complete"><i class="fa-solid fa-check"></i> Complete</span>
                    <i class="fa-solid fa-chevron-down tool-toggle" style="margin-left: 8px;"></i>
                  </div>
                  <div class="tool-body" id="${toolId}-body" style="display: none;">
                    <pre class="tool-output">${escapeHtml(t.output || '')}</pre>
                  </div>
                `;
                toolsElem.appendChild(toolCard);
              }
            });
          }
          if (tagElem) tagElem.innerText = `${data.tag} (${Number(data.elapsed).toFixed(2)}s | ${data.tools_used || 0} tools)`;
          textElem.innerHTML = renderMarkdown(data.answer);
          rawAccumulated = data.answer;
          container.scrollTop = container.scrollHeight;
        } catch (syncErr) {
          textElem.innerHTML = '<span style="color: #ef4444;">Error communicating with OpenClaw backend: ' + escapeHtml(String(syncErr)) + '</span>';
        }
      }

      window[msgId + '_raw'] = rawAccumulated;
      if (sendBtn) {
        sendBtn.disabled = false;
        sendBtn.innerHTML = '<i class="fa-solid fa-paper-plane"></i> Send';
      if (input) input.focus();
    }

    function copyMessage(msgId) {
      const raw = window[msgId + '_raw'] || (document.getElementById(`${msgId}-body`) ? document.getElementById(`${msgId}-body`).innerText : '');
      copyToClipboard(raw);
    }

    function setAgentGoal(goal) {
      const input = document.getElementById('agent-task-input');
      if (input) input.value = goal;
    }

    async function runAgentTask() {
      const input = document.getElementById('agent-task-input');
      const goal = input ? input.value.trim() : '';
      if (!goal) return;
      
      const card = document.getElementById('agent-results-card');
      const traceDiv = document.getElementById('agent-trace');
      const conclDiv = document.getElementById('agent-conclusion');
      const turnsBadge = document.getElementById('agent-turns-badge');
      const btn = document.getElementById('agent-exec-btn');

      if (card) card.style.display = 'block';
      if (traceDiv) traceDiv.innerHTML = '<div style="color: var(--warning);"><i class="fa-solid fa-spinner fa-spin"></i> Agent running autonomous reasoning loop across mesh tools...</div>';
      if (conclDiv) conclDiv.innerHTML = '<i>Processing...</i>';
      if (turnsBadge) turnsBadge.innerText = '';
      if (btn) btn.disabled = true;

      try {
        const resp = await fetch('/api/agent', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({goal: goal})
        });
        const data = await resp.json();

        let html = '';
        (data.trace || []).forEach(step => {
          html += `<div style="margin-bottom: 10px; padding: 10px; background: rgba(0,0,0,0.3); border-radius: 8px; border-left: 3px solid var(--accent);">
            <div style="font-weight: bold; color: var(--accent); margin-bottom: 4px;">Turn ${step.turn}: Tool [${step.tool.toUpperCase()}]</div>
            ${step.thought ? '<div style="color: var(--text-dim); font-style: italic; margin-bottom: 4px;">' + escapeHtml(step.thought) + '</div>' : ''}
            <pre style="background: #080d1a; padding: 6px 10px; border-radius: 4px; font-size: 11px;">${escapeHtml(JSON.stringify(step.action || {}, null, 2))}</pre>
          </div>`;
        });
        if (traceDiv) traceDiv.innerHTML = html || '<i>No tool trace recorded.</i>';
        if (turnsBadge) turnsBadge.innerText = `${data.turns_used || 0} turns used`;
        if (conclDiv) conclDiv.innerHTML = '<b>Conclusion:</b><br>' + renderMarkdown(data.result || 'Task completed.');
      } catch (e) {
        if (conclDiv) conclDiv.innerHTML = `<span style="color: #ef4444;">Error executing agent loop: ${escapeHtml(String(e))}</span>`;
      } finally {
        if (btn) btn.disabled = false;
      }
    }

    async function fetchTelemetry() {
      const elem = document.getElementById('hw-telemetry');
      if (!elem) return;
      elem.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Loading telemetry...';
      try {
        const resp = await fetch('/api/device', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({action: 'status'})
        });
        const data = await resp.json();
        elem.innerHTML = `<pre style="font-size: 12px; line-height: 1.4;">${escapeHtml(JSON.stringify(data, null, 2))}</pre>`;
      } catch (err) {
        elem.innerHTML = `<span style="color: #ef4444;">Failed to load telemetry: ${escapeHtml(String(err))}</span>`;
      }
    }

    async function triggerDevice(act, arg1, arg2) {
      const args = [];
      if (arg1) args.push(arg1);
      if (arg2) args.push(arg2);
      try {
        const resp = await fetch('/api/device', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({action: act, args: args})
        });
        const data = await resp.json();
        showToast(`Hardware Action '${act}' executed.`);
      } catch (err) {
        showToast(`Hardware Action failed: ${err}`);
      }
    }

    async function searchFts() {
      const input = document.getElementById('fts-query');
      const q = input ? input.value.trim() : '';
      if (!q) return;
      const resDiv = document.getElementById('fts-results');
      if (resDiv) resDiv.innerHTML = '<div style="color: var(--accent);"><i class="fa-solid fa-spinner fa-spin"></i> Searching 140,688 chat records...</div>';

      try {
        const resp = await fetch('/api/fts?q=' + encodeURIComponent(q));
        const results = await resp.json();

        if (!results.length) {
          if (resDiv) resDiv.innerHTML = '<p style="color: var(--text-dim); margin-top: 10px;">No matching forensic records found.</p>';
          return;
        }

        window.forensicSnippets = [];
        let html = `<div style="color: var(--text-dim); margin-bottom: 12px; font-size: 12px;">Found ${results.length} matching forensic records:</div>`;
        results.forEach((r, idx) => {
          window.forensicSnippets.push(r.snippet || '');
          html += `<div class="card" style="margin-bottom: 12px;">
            <div style="display:flex; justify-content: space-between; font-size: 12px; color: var(--accent); margin-bottom: 6px;">
              <span><b>Msg #${escapeHtml(String(r.msg_id))}</b> · ${escapeHtml(r.role || '')} (${escapeHtml(r.conv_title || '')})</span>
              <span style="color: var(--text-dim);">${escapeHtml(r.category || '')}</span>
            </div>
            <div style="font-size: 13px; color: #fff; margin-bottom: 8px;">${escapeHtml(r.snippet || '')}</div>
            <button class="copy-btn" onclick="copyForensicSnippet(${idx})"><i class="fa-solid fa-copy"></i> Copy Snippet</button>
          </div>`;
        });
        if (resDiv) resDiv.innerHTML = html;
      } catch (err) {
        if (resDiv) resDiv.innerHTML = `<p style="color: #ef4444;">FTS Search error: ${escapeHtml(String(err))}</p>`;
      }
    }

    function copyForensicSnippet(idx) {
      if (window.forensicSnippets && window.forensicSnippets[idx] !== undefined) {
        copyToClipboard(window.forensicSnippets[idx]);
      }
    }

    async function draftMotion(type) {
      const container = document.getElementById('motion-preview-container');
      const body = document.getElementById('motion-preview-body');
      const title = document.getElementById('motion-preview-title');
      if (container) container.style.display = 'block';
      if (body) body.innerHTML = 'Generating motion draft...';
      if (title) title.innerHTML = `<i class="fa-solid fa-file-contract"></i> Draft Motion: ${type.toUpperCase()}`;

      try {
        const resp = await fetch('/api/motion?type=' + type);
        const data = await resp.json();
        lastMotionData = data;
        if (body) body.innerHTML = escapeHtml(JSON.stringify(data, null, 2));
        if (container) container.scrollIntoView({ behavior: 'smooth' });
      } catch (err) {
        if (body) body.innerHTML = `<span style="color: #ef4444;">Error drafting motion: ${escapeHtml(String(err))}</span>`;
      }
    }

    function copyMotionText() {
      if (lastMotionData) {
        copyToClipboard(JSON.stringify(lastMotionData, null, 2));
      }
    }
  </script>
</body>
</html>
"""

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

class OpenClawHandler(BaseHTTPRequestHandler):
    def _set_headers(self, content_type="application/json"):
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path in ["/health", "/api/ping"]:
            self._set_headers()
            try:
                self.wfile.write(json.dumps({"status": "ok", "service": "openclaw-web", "version": "20.0"}).encode("utf-8"))
            except (BrokenPipeError, ConnectionResetError):
                pass
            return

        if path in ["/", "/index.html", "/studio"]:
            self._set_headers("text/html; charset=utf-8")
            try:
                self.wfile.write(HTML_PAGE.encode("utf-8"))
            except (BrokenPipeError, ConnectionResetError):
                pass
            return

        if path == "/api/status":
            st = claw.system_status()
            self._set_headers()
            try:
                self.wfile.write(json.dumps(st).encode("utf-8"))
            except (BrokenPipeError, ConnectionResetError):
                pass
            return

        if path in ["/api/chat/stream", "/api/stream"]:
            prompt = query.get("prompt", [""])[0]
            provider = query.get("provider", ["groq"])[0]
            tools_flag = query.get("tools", ["true"])[0].lower() in ["true", "1", "yes"]
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "close")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()

            try:
                for event in claw.stream_chat_with_tools(prompt, target_provider=provider, enable_tools=tools_flag):
                    self.wfile.write(f"data: {json.dumps(event)}\n\n".encode("utf-8"))
                    self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                pass
            self.close_connection = True
            return

        if path in ["/api/connectors", "/api/connectors/status"]:
            st = claw.system_status()
            self._set_headers()
            try:
                self.wfile.write(json.dumps(st).encode("utf-8"))
            except (BrokenPipeError, ConnectionResetError):
                pass
            return

        if path == "/api/fts":
            q = query.get("q", [""])[0]
            res = claw.fts_search(q, limit=10)
            self._set_headers()
            try:
                self.wfile.write(json.dumps(res).encode("utf-8"))
            except (BrokenPipeError, ConnectionResetError):
                pass
            return

        if path == "/api/motion":
            m_type = query.get("type", ["rule60b"])[0]
            res = claw.draft_motion(m_type)
            self._set_headers()
            try:
                self.wfile.write(json.dumps(res).encode("utf-8"))
            except (BrokenPipeError, ConnectionResetError):
                pass
            return

        if path == "/api/case":
            ck = query.get("key", ["1FDV"])[0]
            res = claw.get_case_dossier(ck)
            self._set_headers()
            try:
                self.wfile.write(json.dumps(res).encode("utf-8"))
            except (BrokenPipeError, ConnectionResetError):
                pass
            return

        if path == "/api/memory":
            act = query.get("action", ["list"])[0]
            k = query.get("key", [""])[0]
            v = query.get("val", [""])[0]
            res = claw.memory_action(act, k, v)
            self._set_headers()
            try:
                self.wfile.write(json.dumps(res).encode("utf-8"))
            except (BrokenPipeError, ConnectionResetError):
                pass
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            data = json.loads(body)
        except Exception:
            data = {}

        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path in ["/api/chat/stream", "/api/stream"]:
            prompt = data.get("prompt", "")
            provider = data.get("provider", "groq")
            tools_flag = bool(data.get("enable_tools", True))
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "close")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()

            try:
                for event in claw.stream_chat_with_tools(prompt, target_provider=provider, enable_tools=tools_flag):
                    self.wfile.write(f"data: {json.dumps(event)}\n\n".encode("utf-8"))
                    self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                pass
            self.close_connection = True
            return

        if path == "/api/chat":
            prompt = data.get("prompt", "")
            provider = data.get("provider", "groq")
            tools_flag = bool(data.get("enable_tools", True))
            res = claw.chat_with_tools(prompt, target_provider=provider, enable_tools=tools_flag)
            self._set_headers()
            try:
                self.wfile.write(json.dumps(res).encode("utf-8"))
            except (BrokenPipeError, ConnectionResetError):
                pass
            return

        if path in ["/api/connectors", "/api/connectors/status"]:
            st = claw.system_status()
            self._set_headers()
            try:
                self.wfile.write(json.dumps(st).encode("utf-8"))
            except (BrokenPipeError, ConnectionResetError):
                pass
            return

        if path == "/api/agent":
            goal = data.get("goal", "")
            res = claw.run_agentic_loop(goal)
            self._set_headers()
            try:
                self.wfile.write(json.dumps(res).encode("utf-8"))
            except (BrokenPipeError, ConnectionResetError):
                pass
            return

        if path == "/api/device":
            act = data.get("action", "status")
            args = data.get("args", [])
            res = claw.device_control(act, *args)
            self._set_headers()
            try:
                self.wfile.write(json.dumps(res).encode("utf-8"))
            except (BrokenPipeError, ConnectionResetError):
                pass
            return

        self.send_response(404)
        self.end_headers()

import socket

def run_server():
    server = None
    try:
        class V6Server(ThreadingMixIn, HTTPServer):
            address_family = socket.AF_INET6
            daemon_threads = True
            def server_bind(self):
                self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
                super().server_bind()
        server = V6Server(("::", PORT), OpenClawHandler)
    except Exception:
        class V4Server(ThreadingMixIn, HTTPServer):
            daemon_threads = True
        server = V4Server(("0.0.0.0", PORT), OpenClawHandler)

    print(f"⚡ OpenClaw Web Studio active on http://127.0.0.1:{PORT} and http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping OpenClaw Web Studio.")

if __name__ == "__main__":
    run_server()
