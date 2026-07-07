#!/usr/bin/env python3
"""VIDZDOWNLOAD one-file local app.

Run:
  python3 VIDZDOWNLOAD.py

Optional dependency for real downloads:
  python3 -m pip install yt-dlp imageio-ffmpeg

By default, videos are written next to this file in:
  VIDZ IMPORTS
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
import unicodedata
import uuid
import webbrowser
from colorsys import rgb_to_hsv
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


BASE_DIR = Path(__file__).resolve().parent
APP_BUNDLE_DIR = next((parent for parent in BASE_DIR.parents if parent.suffix == ".app"), None)
DEFAULT_IMPORTS_DIR = (Path.home() / "Movies" / "VIDZDOWNLOAD") if APP_BUNDLE_DIR else (BASE_DIR / "VIDZ IMPORTS")
CONFIG_FILE = BASE_DIR / "VIDZDOWNLOAD_CONFIG.json"
COOKIES_FILE = BASE_DIR / "VIDZ_COOKIES.txt"
LOGO_PATHS = [
    BASE_DIR / "VIDZDOWNLOAD_LOGO.png",
    BASE_DIR / "VIDZDOWNLOAD.app" / "Contents" / "Resources" / "VIDZDOWNLOAD_LOGO.png",
    Path.home() / "Downloads" / "VIDZDOWNLOAD_LOGO.png",
]
VIDEO_EXTS = {".mp4", ".mov", ".m4v", ".avi", ".mkv", ".webm"}
JOBS: dict[str, dict] = {}


HTML = r"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>VIDZDOWNLOAD</title>
<style>
:root{color-scheme:dark;--text:#eee5d0;--muted:#8c8372;--amber:#ff9f2f;--amber2:#bd6a1f;--screen:#160702;--faint:#4c270b}
*{box-sizing:border-box}body{margin:0;min-height:100vh;overflow:hidden;background:radial-gradient(circle at 50% 38%,rgba(255,159,47,.13),transparent 30%),linear-gradient(180deg,#2a2925,#11100e 54%,#020202);color:var(--text);font-family:"Courier New",ui-monospace,monospace}button,input,textarea{font:inherit}.bench{width:min(1180px,100vw);min-height:100vh;margin:0 auto;padding:8px 22px;display:grid;place-items:center}.machine{position:relative;width:min(1040px,calc(100vw - 44px));padding:14px 24px 13px;border:1px solid #464134;border-radius:18px;background:linear-gradient(90deg,rgba(255,159,47,.05),transparent 7% 93%,rgba(255,159,47,.035)),linear-gradient(145deg,rgba(255,255,255,.105),transparent 12% 78%,rgba(0,0,0,.58)),repeating-linear-gradient(90deg,rgba(255,255,255,.018) 0 1px,transparent 1px 9px),repeating-linear-gradient(0deg,rgba(255,159,47,.018) 0 1px,transparent 1px 21px),linear-gradient(180deg,#171612,#0a0a08);box-shadow:inset 0 2px 0 rgba(255,255,255,.11),inset 0 -3px 0 rgba(0,0,0,.72),inset 0 0 0 5px rgba(255,255,255,.025),0 22px 54px rgba(0,0,0,.68),0 7px 0 #030303}.machine:before{content:"";position:absolute;inset:12px;border:1px solid rgba(255,159,47,.08);border-radius:13px;pointer-events:none}.top{position:absolute;left:50%;top:-14px;width:270px;height:28px;transform:translateX(-50%);border:1px solid #332f27;border-bottom:0;border-radius:17px 17px 0 0;background:repeating-linear-gradient(90deg,rgba(255,255,255,.045) 0 1px,transparent 1px 8px),linear-gradient(180deg,#1b1915,#070706)}.screw{position:absolute;width:17px;height:17px;border-radius:50%;background:radial-gradient(circle at 35% 26%,#b3a486,#6a5b3e 36%,#16130e 76%);z-index:2}.screw:after{content:"";position:absolute;width:10px;height:2px;left:3px;top:7px;background:#21180f;transform:rotate(32deg)}.tl{left:18px;top:18px}.tr{right:18px;top:18px}.bl{left:18px;bottom:18px}.br{right:18px;bottom:18px}.brand{display:grid;justify-items:center;gap:3px;padding-bottom:6px}.plate{position:relative;width:230px;min-height:54px;display:grid;place-items:center;align-content:center;gap:2px;border:1px solid #343027;border-radius:5px;background:radial-gradient(circle at 50% -20%,rgba(255,255,255,.16),transparent 38%),linear-gradient(145deg,rgba(255,255,255,.08),transparent 38%,rgba(0,0,0,.52)),#050505;color:#8b826f;box-shadow:inset 0 1px 0 rgba(255,255,255,.09),inset 0 -2px 0 #000,0 9px 16px rgba(0,0,0,.44);text-transform:uppercase}.plate strong{color:#b1a893;font-size:16px;letter-spacing:3px}.plate span{color:#8f8673;font-size:9px;font-weight:700;letter-spacing:5px}.title{display:grid;justify-items:center;text-transform:uppercase}.title span{color:var(--muted);font-size:10px;font-weight:700;letter-spacing:4px}.title strong{font-size:22px;letter-spacing:5px;text-shadow:0 2px 0 #000}.deck{display:grid;grid-template-columns:1fr 1fr;gap:14px}.screen,.oled{border:8px solid #0e0c09;border-radius:9px;background:#0e0c09;box-shadow:inset 0 4px 9px rgba(0,0,0,.88),0 1px 0 rgba(255,255,255,.16),0 7px 12px rgba(0,0,0,.34)}.inner,.oled{position:relative;overflow:hidden;background:repeating-linear-gradient(0deg,rgba(255,159,47,.055) 0 1px,transparent 1px 3px),radial-gradient(circle at 50% 0%,rgba(255,159,47,.12),transparent 45%),var(--screen);color:var(--amber);text-shadow:0 0 7px rgba(255,159,47,.38)}.inner{min-height:86px;padding:8px 14px 7px;border-radius:3px}.inner h2,.oled-title{margin:0 0 5px;padding-bottom:4px;border-bottom:1px dashed var(--faint);color:var(--amber2);font-size:11px;letter-spacing:3px;text-align:center}.inner p{display:grid;grid-template-columns:12px 92px 1fr;gap:8px;margin:3px 0;font-size:13px;font-weight:800;letter-spacing:1px}.dot,.ready-dot{width:8px;height:8px;border-radius:50%;background:#70400d;box-shadow:inset 0 1px 1px #000}.dot.on,.ready-dot.on{background:#6fe272;box-shadow:0 0 8px rgba(111,226,114,.75)}.inner b{justify-self:end;color:var(--amber);font-size:12px}.selector{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:8px}.bank,.input-module,.controls{border-radius:9px;background:linear-gradient(180deg,rgba(255,255,255,.08),rgba(0,0,0,.22)),#2a251c;border:1px solid #48402f;box-shadow:inset 0 1px 0 rgba(255,255,255,.12),inset 0 -2px 0 rgba(0,0,0,.45);position:relative}.bank{padding:7px}label{display:block;margin-bottom:8px;color:var(--amber);font-size:11px;font-weight:900;letter-spacing:2px;text-transform:uppercase}.url-module label:after{content:"  MULTI DROP";color:#675d4b;font-size:8px;letter-spacing:2px}.buttons{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}button{min-height:38px;border:0;border-radius:7px;color:var(--text);text-transform:uppercase;cursor:pointer;font-weight:900;letter-spacing:1.5px}.source,.mode{position:relative;background:linear-gradient(180deg,#26231d,#11100d);box-shadow:inset 0 2px 0 rgba(255,255,255,.12),inset 0 -3px 0 rgba(0,0,0,.42),0 4px 0 rgba(0,0,0,.52)}.source.active,.mode.active,#startBtn{color:#1c1308;background:linear-gradient(180deg,#ffb448,#e78319)}.source[data-source=Instagram].active{background:linear-gradient(180deg,#a978d9,#6f45a7);color:#fff6e3}.source[data-source=Vimeo].active{background:linear-gradient(180deg,#65c2d6,#2c7d91);color:#051014}.mode[data-mode=playlist].active{background:linear-gradient(180deg,#f0d36a,#b99c28);color:#171207}.mode[data-mode=account].active{background:linear-gradient(180deg,#d36b6b,#9a3434);color:#fff4e2}.inputs{display:grid;grid-template-columns:1fr 1fr 1fr 92px;gap:9px 12px;margin-top:8px}.url-module{grid-column:1/-1}.input-module{padding:7px 10px 8px}input,textarea{width:100%;border:0;border-radius:5px;outline:none;background:repeating-linear-gradient(0deg,rgba(255,159,47,.04) 0 1px,transparent 1px 3px),#050302;color:var(--amber);padding:0 12px;font-weight:900;letter-spacing:1px;box-shadow:inset 0 0 22px rgba(0,0,0,.86),0 1px 0 rgba(255,255,255,.08)}input{height:32px}textarea{display:block;height:54px;padding:8px 12px;line-height:1.35;resize:none}.limit input{text-align:center}.oled{display:grid;grid-template-columns:170px 1fr 58px;align-items:center;gap:14px;min-height:68px;margin-top:8px;padding:7px 14px}.oled-title{margin:0;padding:0;border:0;text-align:left}.oled-main{min-width:0;color:var(--amber);font-size:20px;font-weight:900;letter-spacing:2px;text-transform:uppercase;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.bar{grid-column:1/3;height:12px;border:1px solid #76420d;background:#080302;overflow:hidden}.bar span{display:block;width:0%;height:100%;background:repeating-linear-gradient(90deg,var(--amber) 0 9px,transparent 9px 12px);transition:width .2s linear}.percent{grid-column:3;grid-row:1/3;justify-self:end;color:var(--amber);font-size:17px;font-weight:900}.controls{display:grid;grid-template-columns:repeat(3,1fr);gap:11px;margin-top:8px;padding:7px}.controls button{min-height:42px;color:#15100a;background:linear-gradient(180deg,#d4c7a9,#9f8f70);box-shadow:inset 0 2px 0 rgba(255,255,255,.45),inset 0 -4px 0 rgba(0,0,0,.24),0 4px 0 rgba(0,0,0,.45)}#stopBtn{background:linear-gradient(180deg,#d45248,#90231f);color:#fff0db}.ready{display:grid;grid-template-columns:14px 120px 1fr;align-items:center;gap:10px;margin-top:6px;color:var(--muted);text-transform:uppercase}.ready small{color:var(--amber2);font-size:12px;font-weight:900;letter-spacing:2px}.ready strong{justify-self:end;max-width:100%;font-size:12px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}@media(max-width:780px){body{overflow:auto}.bench{padding:12px;align-items:start}.machine{width:100%;padding:22px 16px 18px}.deck,.selector,.buttons,.inputs,.controls{grid-template-columns:1fr}.oled{grid-template-columns:1fr 58px}.oled-title{grid-column:1/3}.bar{grid-column:1/2}.percent{grid-column:2;grid-row:2/4}.ready{grid-template-columns:14px 1fr}}
.plate{width:126px;min-height:100%;height:100%;padding:7px;background:#050505}.plate img{display:block;width:108px;height:92px;object-fit:contain;border-radius:4px;filter:drop-shadow(0 7px 9px rgba(0,0,0,.65))}.plate strong,.plate span{display:none}.deck{grid-template-columns:126px 1fr 1fr;align-items:stretch}.brand.status-logo{padding:0;align-self:stretch}.selector{grid-template-columns:1fr 180px}.source{pointer-events:none}.bookmark-module{grid-column:1/3}.output-module{grid-column:3/5}.path-row{display:grid;grid-template-columns:1fr 52px 58px;gap:6px}.mini{min-height:32px;border-radius:5px;background:linear-gradient(180deg,#d4c7a9,#9f8f70);color:#15100a;font-size:11px}.analyze-bank .buttons{grid-template-columns:1fr}.toggle{background:linear-gradient(180deg,#26231d,#11100d)}.toggle.active{background:linear-gradient(180deg,#7ac96b,#3e8b34);color:#061406}.leds{grid-column:1/4;display:grid;grid-template-columns:repeat(24,1fr);gap:4px;margin-top:2px}.leds span{height:7px;border-radius:2px;background:#231508;box-shadow:inset 0 1px 1px #000}.leds span.on{background:var(--amber);box-shadow:0 0 8px rgba(255,159,47,.75)}@media(max-width:780px){.deck{grid-template-columns:1fr}.brand.status-logo .plate{width:100%;height:auto;min-height:118px}.brand.status-logo .plate img{width:164px;height:96px}.bookmark-module,.output-module{grid-column:auto}.path-row{grid-template-columns:1fr}}
</style>
</head>
<body>
<main class="bench"><section class="machine">
<div class="top"></div><div class="screw tl"></div><div class="screw tr"></div><div class="screw bl"></div><div class="screw br"></div>
<section class="deck"><div class="brand status-logo"><div class="plate"><img src="/logo.png" alt="VIDZDOWNLOAD"></div></div><article class="screen"><div class="inner"><h2>SOURCE STATUS</h2><p><span class="dot on"></span>[ SOURCE ]<b id="selectedSource">AUTO</b></p><p><span class="dot"></span>[ FOLDER ]<b id="sourceFolder">OUTPUT</b></p><p><span class="dot"></span>[ MODE ]<b id="selectedMode">VIDEO</b></p></div></article><article class="screen"><div class="inner"><h2>IMPORT STATUS</h2><p><span class="dot on"></span>[ FILES ]<b id="count">00</b></p><p><span class="dot"></span>[ OUTPUT ]<b id="targetLabel">LOCAL</b></p><p><span class="dot"></span>[ STATE ]<b id="readyLabel">READY</b></p></div></article></section>
<section class="selector"><section class="bank"><label>MODE</label><div class="buttons"><button class="mode active" data-mode="video">Video</button><button class="mode" data-mode="playlist">Playlist</button><button class="mode" data-mode="account">Account</button></div></section><section class="bank analyze-bank"><label>AUTO ANALYZE</label><div class="buttons"><button id="autoAnalyzeBtn" class="toggle" type="button">OFF</button></div></section></section>
<section class="inputs"><div class="input-module url-module"><label for="url">URLS</label><textarea id="url" rows="3" spellcheck="false"></textarea></div><div class="input-module bookmark-module"><label for="bookmarksPath">BOOKMARKS PATH</label><input id="bookmarksPath" placeholder="/path/to/bookmarks.html or folder"></div><div class="input-module output-module"><label for="outputFolder">OUTPUT FOLDER</label><div class="path-row"><input id="outputFolder" placeholder="VIDZ IMPORTS"><button id="setFolderBtn" class="mini" type="button">SET</button><button id="pickFolderBtn" class="mini" type="button">PICK</button></div></div><div class="input-module"><label for="artist">ARTIST</label><input id="artist"></div><div class="input-module"><label for="collection">COLLECTION</label><input id="collection"></div><div class="input-module"><label for="keywords">KEYWORDS</label><input id="keywords"></div><div class="input-module limit"><label for="limit">LIMIT</label><input id="limit" type="number" min="1" max="100" value="25"></div></section>
<section class="oled"><div class="oled-title">STATUS</div><div id="statusText" class="oled-main">READY</div><div class="bar"><span id="barFill"></span></div><div id="percent" class="percent">0%</div></section>
<section class="controls"><button id="folderBtn">FOLDER</button><button id="startBtn">START</button><button id="stopBtn">STOP</button></section>
<footer class="ready"><span id="readyLight" class="ready-dot"></span><small id="folderLabel">VIDZ IMPORTS</small><strong id="lastFile">NO FILE</strong></footer>
</section></main>
<script>
const state={source:"AUTO",mode:"video",autoAnalyze:false,jobId:null,timer:null,lastFile:null,beeped:false};
const $=id=>document.getElementById(id);
document.querySelector(".bar").insertAdjacentHTML("afterend",`<div id="leds" class="leds">${"<span></span>".repeat(24)}</div>`);
function detectSource(value){const v=(value||"").toLowerCase();if(v.includes("instagram.com"))return"Instagram";if(v.includes("youtube.com")||v.includes("youtu.be"))return"YouTube";if(v.includes("vimeo.com"))return"Vimeo";if(v.includes("http"))return"Internet";return"AUTO";}
function updateSource(){state.source=detectSource($("url").value);$("selectedSource").textContent=state.source.toUpperCase();document.querySelectorAll(".source").forEach(b=>b.classList.toggle("active",b.dataset.source===state.source));}
function updateLeds(progress=0){const on=Math.round(Math.max(0,Math.min(100,progress))/100*24);document.querySelectorAll("#leds span").forEach((led,i)=>led.classList.toggle("on",i<on));}
function beep(){try{const ctx=new (window.AudioContext||window.webkitAudioContext)();const osc=ctx.createOscillator();const gain=ctx.createGain();osc.type="square";osc.frequency.value=880;gain.gain.setValueAtTime(.0001,ctx.currentTime);gain.gain.exponentialRampToValueAtTime(.18,ctx.currentTime+.02);gain.gain.exponentialRampToValueAtTime(.0001,ctx.currentTime+.22);osc.connect(gain);gain.connect(ctx.destination);osc.start();osc.stop(ctx.currentTime+.24);}catch(e){}}
function setOled(message,progress=0,ready=false){$("statusText").textContent=message;$("percent").textContent=`${Math.max(0,Math.min(100,Math.round(progress)))}%`;$("barFill").style.width=`${Math.max(0,Math.min(100,progress))}%`;updateLeds(progress);$("readyLight").classList.toggle("on",ready);$("readyLabel").textContent=ready?"READY":message.replace(/\.+$/,"");}
function setAutoAnalyze(on){state.autoAnalyze=!!on;$("autoAnalyzeBtn").classList.toggle("active",state.autoAnalyze);$("autoAnalyzeBtn").textContent=state.autoAnalyze?"ON":"OFF";$("readyLabel").textContent=state.autoAnalyze?"AUTO":"READY";}
async function refreshImports(){const path=encodeURIComponent($("outputFolder")?.value.trim()||"");const res=await fetch(`/api/imports?outputFolder=${path}`);if(!res.ok)return;const data=await res.json();$("folderLabel").textContent=(data.folder||"VIDZ IMPORTS").split("/").slice(-1)[0]||"VIDZ IMPORTS";$("count").textContent=String(data.items.length).padStart(2,"0");$("targetLabel").textContent="VIDEOS";if(data.items[0]){state.lastFile=data.items[0].path;$("lastFile").textContent=data.items[0].name;}}
async function saveConfig(silent=false){const payload={outputFolder:$("outputFolder").value.trim(),autoAnalyze:state.autoAnalyze};const res=await fetch("/api/config",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});const data=await res.json().catch(()=>({}));if(res.ok&&data.output_folder){$("outputFolder").value=data.output_folder;$("folderLabel").textContent=data.output_folder.split("/").slice(-1)[0]||"VIDZ IMPORTS";$("sourceFolder").textContent=$("folderLabel").textContent.toUpperCase();await refreshImports();if(!silent)setOled("FOLDER SET",100,true);}else if(!silent){setOled(data.error||"FOLDER ERROR",100,false);}}
async function pickFolder(){setOled("PICK FOLDER",20,false);const res=await fetch("/api/choose-folder",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({outputFolder:$("outputFolder").value.trim(),autoAnalyze:state.autoAnalyze})});const data=await res.json().catch(()=>({}));if(res.ok&&data.output_folder){$("outputFolder").value=data.output_folder;await saveConfig(true);setOled("FOLDER SET",100,true);}else{setOled(data.error||"PICK CANCELLED",100,false);}}
async function loadConfig(){const res=await fetch("/api/config");if(!res.ok)return;const data=await res.json();$("outputFolder").value=data.output_folder||"";setAutoAnalyze(!!data.auto_analyze);$("folderLabel").textContent=(data.output_folder||"VIDZ IMPORTS").split("/").slice(-1)[0]||"VIDZ IMPORTS";$("sourceFolder").textContent=$("folderLabel").textContent.toUpperCase();$("targetLabel").textContent="VIDEOS";}
async function pollJob(){if(!state.jobId)return;const res=await fetch(`/api/jobs/${state.jobId}`);if(!res.ok)return;const job=await res.json();setOled(job.error||job.message||job.status||"WORKING",job.progress||0,job.status==="ready");if(job.metadata?.source){$("selectedSource").textContent=job.metadata.source.toUpperCase();}if(job.status==="ready"){clearInterval(state.timer);state.timer=null;state.lastFile=job.file;$("lastFile").textContent=job.metadata?.filename||job.file||"READY";if(!state.beeped){state.beeped=true;beep();}await refreshImports();}if(job.status==="error"||job.status==="stopped"){clearInterval(state.timer);state.timer=null;setOled(job.error||job.message||"STOPPED",job.status==="stopped"?0:100,false);}}
async function startDownload(){updateSource();await saveConfig(true);const payload={source:"AUTO",mode:state.mode,autoAnalyze:state.autoAnalyze,url:$("url").value.trim(),bookmarksPath:$("bookmarksPath").value.trim(),outputFolder:$("outputFolder").value.trim(),artist:$("artist").value.trim(),collection:$("collection").value.trim(),keywords:$("keywords").value.trim(),limit:Number($("limit").value||25)};if(!payload.url&&!payload.bookmarksPath){setOled("URL OR BOOKMARKS ?",0,false);$("url").focus();return;}state.beeped=false;setOled("QUEUED",1,false);const res=await fetch("/api/download",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});if(!res.ok){setOled(await res.text(),100,false);return;}const data=await res.json();state.jobId=data.job_id;if(state.timer)clearInterval(state.timer);state.timer=setInterval(pollJob,650);pollJob();}
async function stopDownload(){if(!state.jobId){setOled("STOPPED",0,false);return;}await fetch(`/api/jobs/${state.jobId}/stop`,{method:"POST"});setOled("STOPPING...",0,false);}
async function analyzeLast(){if(!state.lastFile){await refreshImports();}if(!state.lastFile){setOled("NO FILE",0,false);return;}setOled("ANALYZING...",35,false);const res=await fetch("/api/analyze-last",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({file:state.lastFile,outputFolder:$("outputFolder").value.trim()})});const data=await res.json().catch(()=>({error:"ANALYSIS ERROR"}));if(!res.ok||!data.ok){setOled(data.error||"ANALYSIS ERROR",100,false);return;}state.lastFile=data.file;$("lastFile").textContent=data.filename||data.file;await refreshImports();setOled((data.tags||[]).slice(0,3).join(" ")||"ANALYZED",100,true);beep();}
async function openFolder(){await fetch("/api/open-folder",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({outputFolder:$("outputFolder").value.trim(),autoAnalyze:state.autoAnalyze})});await refreshImports();setOled("FOLDER",100,true);}
document.querySelectorAll(".mode").forEach(b=>b.addEventListener("click",()=>{document.querySelectorAll(".mode").forEach(x=>x.classList.remove("active"));b.classList.add("active");state.mode=b.dataset.mode;$("selectedMode").textContent=state.mode.toUpperCase();}));
$("folderBtn").addEventListener("click",openFolder);$("startBtn").addEventListener("click",startDownload);$("stopBtn").addEventListener("click",stopDownload);$("setFolderBtn").addEventListener("click",()=>saveConfig(false));$("pickFolderBtn").addEventListener("click",pickFolder);$("autoAnalyzeBtn").addEventListener("click",async()=>{setAutoAnalyze(!state.autoAnalyze);await saveConfig(true);setOled(state.autoAnalyze?"AUTO ANALYZE":"MANUAL",100,true);});$("url").addEventListener("input",updateSource);$("url").addEventListener("keydown",e=>{if(e.key==="Enter"&&(e.metaKey||e.ctrlKey))startDownload();});$("outputFolder").addEventListener("input",()=>{$("folderLabel").textContent=$("outputFolder").value.split("/").slice(-1)[0]||"VIDZ IMPORTS";$("sourceFolder").textContent=$("folderLabel").textContent.toUpperCase();});loadConfig().then(refreshImports).then(()=>{updateSource();setOled("READY",0,true);});
</script>
</body></html>"""


def load_config() -> dict:
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8")) if CONFIG_FILE.exists() else {}
    except Exception:
        return {}


def save_config(config: dict) -> None:
    CONFIG_FILE.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on", "auto"}


def resolve_output_dir(value: str | None = None) -> Path:
    raw = (value or load_config().get("output_folder") or str(DEFAULT_IMPORTS_DIR)).strip()
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = BASE_DIR / path
    return path.resolve()


def videos_dir(output_dir: Path) -> Path:
    return output_dir / "VIDEOS"


def assets_dir(output_dir: Path) -> Path:
    return output_dir / "ASSETS"


def ensure_dirs(output_dir: Path | None = None) -> Path:
    target = output_dir or resolve_output_dir()
    target.mkdir(parents=True, exist_ok=True)
    videos_dir(target).mkdir(parents=True, exist_ok=True)
    assets_dir(target).mkdir(parents=True, exist_ok=True)
    return target


def metadata_path(video_path: Path, output_dir: Path) -> Path:
    return assets_dir(output_dir) / f"{video_path.stem}.json"


def asset_path(video_path: Path, output_dir: Path, suffix: str) -> Path:
    return assets_dir(output_dir) / f"{video_path.stem}{suffix}"


def token(value: str, fallback: str) -> str:
    raw = (value or fallback).strip() or fallback
    raw = unicodedata.normalize("NFKD", raw).encode("ascii", "ignore").decode("ascii")
    raw = raw.upper().replace("&", " AND ")
    raw = re.sub(r"[^A-Z0-9]+", "_", raw).strip("_")
    return (raw or fallback)[:90]


def split_urls(value: str, limit: int = 500) -> list[str]:
    urls = re.findall(r"https?://[^\s,;'\"<>]+", value or "", flags=re.I)
    out: list[str] = []
    seen: set[str] = set()
    for url in urls:
        clean = url.strip().rstrip(".,;)'\"<>")
        if clean and clean not in seen:
            seen.add(clean)
            out.append(clean)
    return out[:limit]


def bookmark_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.is_dir():
        return []
    allowed = {".html", ".htm", ".json", ".txt", ".url", ".webloc"}
    return [
        item for item in sorted(path.rglob("*"))
        if item.is_file() and item.suffix.lower() in allowed
    ][:300]


def urls_from_bookmarks(bookmarks_path: str, limit: int = 500) -> list[str]:
    raw = (bookmarks_path or "").strip()
    if not raw:
        return []
    root = Path(raw).expanduser()
    if not root.is_absolute():
        root = BASE_DIR / root
    urls: list[str] = []
    seen: set[str] = set()
    for path in bookmark_files(root):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for url in split_urls(text, limit=limit):
            if url not in seen:
                seen.add(url)
                urls.append(url)
            if len(urls) >= limit:
                return urls
    return urls


def collect_input_urls(url_text: str, bookmarks_path: str, limit: int = 500) -> list[str]:
    urls: list[str] = []
    seen: set[str] = set()
    for url in split_urls(url_text, limit=limit) + urls_from_bookmarks(bookmarks_path, limit=limit):
        if url not in seen:
            seen.add(url)
            urls.append(url)
        if len(urls) >= limit:
            break
    return urls


def is_instagram(url: str) -> bool:
    return bool(re.search(r"https?://(?:www\.)?instagram\.com/", url, re.I))


def detect_source(url: str) -> str:
    clean = url.lower()
    if "instagram.com" in clean:
        return "Instagram"
    if "youtube.com" in clean or "youtu.be" in clean:
        return "YouTube"
    if "vimeo.com" in clean:
        return "Vimeo"
    return "Internet"


def is_instagram_media_url(url: str) -> bool:
    return bool(re.search(r"instagram\.com/(?:reel|p|tv)/", url, re.I))


def normalize_source_url(url: str) -> tuple[str, str]:
    clean = url.strip()
    reel_grid = re.match(
        r"https?://(?:www\.)?instagram\.com/([^/?#]+)/reels/?(?:[?#].*)?$",
        clean,
        re.I,
    )
    if reel_grid:
        return f"https://www.instagram.com/{reel_grid.group(1)}/", "instagram_reels_grid"
    return clean, ""


def should_expand(mode: str, url: str, normalized_kind: str) -> bool:
    if is_instagram_media_url(url):
        return True
    clean = url.lower()
    if "youtube.com" in clean and "list=" in clean:
        return True
    if "vimeo.com/showcase/" in clean or "vimeo.com/album/" in clean:
        return True
    if normalized_kind:
        return True
    if mode == "playlist":
        return True
    if mode == "account":
        return not is_instagram_media_url(url)
    return False


def entry_url_from(entry: dict) -> str:
    return (
        entry.get("webpage_url")
        or entry.get("original_url")
        or entry.get("url")
        or ""
    )


def readable_error(exc: Exception, url: str) -> str:
    text = str(exc)
    if is_instagram(url) and (
        "Unsupported URL" in text
        or "instagram:user" in text
        or "Unable to extract data" in text
    ):
        return "INSTAGRAM ACCOUNT NEEDS COOKIES - ADD VIDZ_COOKIES.txt OR USE ONE REEL URL"
    return text


def ytdlp_opts(extra: dict | None = None) -> dict:
    opts = {"quiet": True, "no_warnings": True}
    if COOKIES_FILE.exists():
        opts["cookiefile"] = str(COOKIES_FILE)
    if extra:
        opts.update(extra)
    return opts


def unique_path(output_dir: Path, stem: str) -> Path:
    target = output_dir / f"{stem}.mp4"
    index = 2
    while target.exists():
        target = output_dir / f"{stem}_{index:02d}.mp4"
        index += 1
    return target


def find_download(no_ext: Path) -> Path | None:
    if no_ext.with_suffix(".mp4").exists():
        return no_ext.with_suffix(".mp4")
    matches = sorted(no_ext.parent.glob(f"{no_ext.name}.*"))
    media = [p for p in matches if p.suffix.lower() in VIDEO_EXTS]
    return media[0] if media else None


def find_thumb(no_ext: Path) -> Path | None:
    matches = sorted(no_ext.parent.glob(f"{no_ext.name}.*"))
    thumbs = [p for p in matches if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}]
    return thumbs[0] if thumbs else None


def move_thumb_to_assets(no_ext: Path, video_path: Path, output_dir: Path) -> Path | None:
    thumb = find_thumb(no_ext)
    if not thumb:
        return None
    target = asset_path(video_path, output_dir, thumb.suffix.lower())
    if thumb != target:
        if target.exists():
            target.unlink()
        thumb.replace(target)
    return target


def ffmpeg_exe() -> str | None:
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        pass
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, timeout=5)
        return "ffmpeg"
    except Exception:
        return None


def video_probe(path: Path, ffmpeg_location: str | None = None) -> dict:
    ffmpeg = ffmpeg_location or ffmpeg_exe()
    info: dict = {}
    if not ffmpeg:
        return info
    try:
        proc = subprocess.run(
            [ffmpeg, "-hide_banner", "-i", str(path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=12,
        )
    except Exception:
        return info
    text = (proc.stderr or "") + "\n" + (proc.stdout or "")
    duration = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", text)
    if duration:
        hours, minutes, seconds = duration.groups()
        info["duration_seconds"] = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    resolution = re.search(r"Video:.*?(\d{2,5})x(\d{2,5})", text)
    if resolution:
        info["width"] = int(resolution.group(1))
        info["height"] = int(resolution.group(2))
    fps = re.search(r"(\d+(?:\.\d+)?)\s*fps", text)
    if fps:
        info["fps"] = float(fps.group(1))
    return info


def dominant_color_tag(red: float, green: float, blue: float) -> str:
    hue, saturation, value = rgb_to_hsv(red / 255, green / 255, blue / 255)
    if value < 0.18:
        return "COLOR_BLACK"
    if saturation < 0.16:
        return "COLOR_WHITE" if value > 0.78 else "COLOR_GREY"
    degrees = hue * 360
    if degrees < 18 or degrees >= 345:
        return "COLOR_RED"
    if degrees < 45:
        return "COLOR_ORANGE"
    if degrees < 72:
        return "COLOR_YELLOW"
    if degrees < 160:
        return "COLOR_GREEN"
    if degrees < 205:
        return "COLOR_CYAN"
    if degrees < 255:
        return "COLOR_BLUE"
    if degrees < 300:
        return "COLOR_PURPLE"
    return "COLOR_PINK"


def frame_analysis(path: Path, ffmpeg_location: str | None = None) -> dict:
    ffmpeg = ffmpeg_location or ffmpeg_exe()
    if not ffmpeg:
        return {"available": False, "reason": "ffmpeg missing"}
    width, height, frames = 32, 18, 8
    frame_size = width * height * 3
    try:
        proc = subprocess.run(
            [
                ffmpeg, "-hide_banner", "-loglevel", "error", "-i", str(path),
                "-vf", f"fps=1,scale={width}:{height}", "-frames:v", str(frames),
                "-an", "-sn", "-f", "rawvideo", "-pix_fmt", "rgb24", "-",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=35,
        )
    except Exception as exc:  # noqa: BLE001
        return {"available": False, "reason": str(exc)}
    raw = proc.stdout or b""
    frame_count = len(raw) // frame_size
    if frame_count < 1:
        return {"available": False, "reason": "no frames"}
    raw = raw[:frame_count * frame_size]
    pixels = len(raw) // 3
    red = sum(raw[0::3]) / pixels
    green = sum(raw[1::3]) / pixels
    blue = sum(raw[2::3]) / pixels
    brightness = (red + green + blue) / 3
    motion = 0.0
    if frame_count > 1:
        diffs = []
        for index in range(1, frame_count):
            previous = raw[(index - 1) * frame_size:index * frame_size]
            current = raw[index * frame_size:(index + 1) * frame_size]
            diffs.append(sum(abs(a - b) for a, b in zip(previous, current)) / frame_size)
        motion = sum(diffs) / len(diffs)
    return {
        "available": True,
        "frames": frame_count,
        "average_rgb": [round(red), round(green), round(blue)],
        "brightness": round(brightness, 2),
        "motion": round(motion, 2),
        "color_tag": dominant_color_tag(red, green, blue),
    }


def face_tag(path: Path, ffmpeg_location: str | None = None) -> tuple[str | None, str]:
    try:
        import cv2
    except Exception:
        return None, "opencv missing"
    ffmpeg = ffmpeg_location or ffmpeg_exe()
    if not ffmpeg:
        return None, "ffmpeg missing"
    try:
        with tempfile.TemporaryDirectory() as tmp:
            frame = Path(tmp) / "frame.jpg"
            subprocess.run(
                [
                    ffmpeg, "-hide_banner", "-loglevel", "error", "-ss", "00:00:01",
                    "-i", str(path), "-frames:v", "1", "-vf", "scale=640:-1", str(frame),
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=20,
                check=False,
            )
            image = cv2.imread(str(frame))
            if image is None:
                return None, "no frame"
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            cascade_path = str(Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml")
            cascade = cv2.CascadeClassifier(cascade_path)
            faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(42, 42))
            if len(faces):
                return "FACE", f"{len(faces)} face(s)"
            return "NO_FACE", "no face"
    except Exception as exc:  # noqa: BLE001
        return None, str(exc)


def analysis_tags(path: Path, ffmpeg_location: str | None = None) -> tuple[list[str], dict]:
    probe = video_probe(path, ffmpeg_location)
    frames = frame_analysis(path, ffmpeg_location)
    tags: list[str] = []
    details = {"probe": probe, "frames": frames}
    if frames.get("available"):
        tags.append(str(frames.get("color_tag")))
        brightness = float(frames.get("brightness") or 0)
        motion = float(frames.get("motion") or 0)
        if brightness < 65:
            tags.append("DARK")
        elif brightness > 185:
            tags.append("BRIGHT")
        if motion >= 34:
            tags.append("FAST_MOTION")
        elif motion >= 16:
            tags.append("MOVING")
        else:
            tags.append("STILL")
    width = int(probe.get("width") or 0)
    height = int(probe.get("height") or 0)
    if width and height:
        if height > width * 1.15:
            tags.append("VERTICAL")
        elif width > height * 1.15:
            tags.append("WIDE")
        else:
            tags.append("SQUARE")
        if width >= 1920 or height >= 1920:
            tags.append("HD")
    duration = float(probe.get("duration_seconds") or 0)
    if duration:
        if duration < 20:
            tags.append("SHORT")
        elif duration > 180:
            tags.append("LONG")
    fps = float(probe.get("fps") or 0)
    if fps >= 50:
        tags.append("HIGH_FPS")
    face, face_reason = face_tag(path, ffmpeg_location)
    details["face_detection"] = face_reason
    if face == "FACE":
        tags.append("FACE")
    clean: list[str] = []
    for tag in tags:
        tag = token(tag, "")
        if tag and tag not in clean:
            clean.append(tag)
    return clean[:8], details


def sidecars_for(path: Path, output_dir: Path) -> list[Path]:
    candidates = [metadata_path(path, output_dir), path.with_suffix(".json")]
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        candidates.extend([asset_path(path, output_dir, ext), path.with_suffix(ext)])
    return [item for item in candidates if item.exists()]


def unique_analysis_path(path: Path, tags: list[str], output_dir: Path) -> Path:
    stem = path.stem
    old_tags = []
    meta_path = metadata_path(path, output_dir)
    if not meta_path.exists():
        meta_path = path.with_suffix(".json")
    try:
        metadata = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
        old_tags = [token(tag, "") for tag in metadata.get("analysis_tags", [])]
    except Exception:
        old_tags = []
    for tag in old_tags:
        suffix = f"__{tag}"
        if stem.endswith(suffix):
            stem = stem[:-len(suffix)]
    new_stem = "__".join([stem] + tags)
    target = path.with_name(f"{new_stem}{path.suffix}")
    index = 2
    while target.exists() and target != path:
        target = path.with_name(f"{new_stem}_{index:02d}{path.suffix}")
        index += 1
    return target


def latest_video(output_dir: Path) -> Path | None:
    roots = [videos_dir(output_dir), output_dir]
    videos = [p for root in roots for p in root.glob("*") if p.suffix.lower() in VIDEO_EXTS]
    return max(videos, key=lambda p: p.stat().st_mtime) if videos else None


def analyze_and_rename(path: Path, output_dir: Path) -> dict:
    if not path.exists() or path.suffix.lower() not in VIDEO_EXTS:
        raise RuntimeError("No video file to analyze")
    ffmpeg_location = ffmpeg_exe()
    if not ffmpeg_location:
        raise RuntimeError("Analysis needs ffmpeg. Run: python3 -m pip install -r requirements.txt")
    tags, details = analysis_tags(path, ffmpeg_location)
    if not tags:
        raise RuntimeError("Analysis produced no tags")
    target = unique_analysis_path(path, tags, output_dir)
    old_sidecars = sidecars_for(path, output_dir)
    if target != path:
        path.replace(target)
        for sidecar in old_sidecars:
            new_sidecar = asset_path(target, output_dir, sidecar.suffix)
            if sidecar.exists() and sidecar != new_sidecar:
                sidecar.replace(new_sidecar)
    meta_path = metadata_path(target, output_dir)
    if not meta_path.exists() and target.with_suffix(".json").exists():
        target.with_suffix(".json").replace(meta_path)
    try:
        metadata = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    except Exception:
        metadata = {}
    metadata.update({
        "file": str(target),
        "filename": target.name,
        "ready_for": str(output_dir),
        "analysis_tags": tags,
        "analysis": {
            "tags": tags,
            "details": details,
            "analyzed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        },
    })
    thumb = find_thumb(target.with_suffix("")) or next(
        (asset_path(target, output_dir, ext) for ext in (".jpg", ".jpeg", ".png", ".webp")
         if asset_path(target, output_dir, ext).exists()),
        None,
    )
    if thumb:
        metadata["thumbnail"] = str(thumb)
    meta_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"ok": True, "file": str(target), "filename": target.name, "tags": tags, "analysis": metadata["analysis"]}


def download_one(yt_dlp, ffmpeg_location: str | None, job: dict, body: dict,
                 output_dir: Path,
                 url: str, index: int, total_items: int) -> dict:
    base = 5 + ((index - 1) / total_items) * 90
    span = 90 / total_items
    job.update(status="analyzing", progress=round(base, 1),
               message=f"ANALYZING {index}/{total_items}")
    try:
        with yt_dlp.YoutubeDL(ytdlp_opts({"noplaylist": True})) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(readable_error(exc, url)) from exc

    title = info.get("title") or "UNTITLED"
    source = detect_source(url)
    artist_token = token(body.get("artist") or info.get("artist") or info.get("uploader"), "UNKNOWN_ARTIST")
    collection_token = token(body.get("collection") or info.get("playlist") or source, "COLLECTION")
    keywords_token = token(body.get("keywords"), "")
    title_token = token(title, "UNTITLED")
    stem_parts = [artist_token, collection_token]
    if keywords_token:
        stem_parts.append(keywords_token)
    stem_parts.append(title_token)
    target = unique_path(videos_dir(output_dir), "__".join(stem_parts))
    no_ext = target.with_suffix("")

    def hook(event: dict) -> None:
        if job.get("cancel"):
            raise RuntimeError("STOPPED")
        if event.get("status") == "downloading":
            total = event.get("total_bytes") or event.get("total_bytes_estimate") or 0
            done = event.get("downloaded_bytes") or 0
            item_progress = (done / total) if total else 0.08
            progress = base + max(0, min(0.88, item_progress)) * span
            job.update(status="downloading", progress=round(progress, 1),
                       message=f"DOWNLOADING {index}/{total_items}")
        elif event.get("status") == "finished":
            job.update(status="analyzing", progress=round(base + 0.92 * span, 1),
                       message=f"ANALYZING {index}/{total_items}")

    opts = ytdlp_opts({
        "noplaylist": True,
        "format": "bv*+ba/b",
        "merge_output_format": "mp4",
        "outtmpl": f"{no_ext}.%(ext)s",
        "writethumbnail": True,
        "progress_hooks": [hook],
        "postprocessors": [{"key": "FFmpegVideoRemuxer", "preferedformat": "mp4"}],
    })
    if ffmpeg_location:
        opts["ffmpeg_location"] = ffmpeg_location
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

    downloaded = find_download(no_ext)
    if not downloaded:
        raise RuntimeError("Download finished but no video file was created")
    if downloaded != target and downloaded.suffix.lower() == ".mp4" and not target.exists():
        downloaded.replace(target)
        downloaded = target

    thumb = move_thumb_to_assets(no_ext, downloaded, output_dir)
    metadata = {
        "source": source,
        "mode": body.get("mode", ""),
        "url": url,
        "artist": body.get("artist", "").strip(),
        "collection": body.get("collection", "").strip(),
        "keywords": body.get("keywords", "").strip(),
        "title": title,
        "channel": info.get("channel") or info.get("uploader") or "",
        "date": info.get("upload_date") or info.get("release_date") or "",
        "webpage_url": info.get("webpage_url") or url,
        "thumbnail": str(thumb) if thumb else info.get("thumbnail") or "",
        "file": str(downloaded),
        "filename": downloaded.name,
        "ready_for": str(output_dir),
        "videos_folder": str(videos_dir(output_dir)),
        "assets_folder": str(assets_dir(output_dir)),
        "downloaded_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    metadata_path(downloaded, output_dir).write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    return metadata


def worker(job_id: str, body: dict) -> None:
    job = JOBS[job_id]
    try:
        import yt_dlp
    except Exception as exc:  # noqa: BLE001
        job.update(status="error", message="YT-DLP MISSING",
                   error="Install yt-dlp: python3 -m pip install yt-dlp imageio-ffmpeg")
        return
    try:
        import imageio_ffmpeg
        ffmpeg_location = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:  # noqa: BLE001
        ffmpeg_location = None

    try:
        output_dir = resolve_output_dir(body.get("outputFolder") or body.get("output_folder"))
        ensure_dirs(output_dir)
        config = load_config()
        config["output_folder"] = str(output_dir)
        config["auto_analyze"] = truthy(body.get("autoAnalyze") or body.get("auto_analyze"))
        save_config(config)
        mode = (body.get("mode") or "video").strip().lower()
        auto_analyze = truthy(body.get("autoAnalyze") or body.get("auto_analyze"))
        max_items = max(1, min(int(body.get("limit") or 25), 100))
        input_urls = collect_input_urls(body.get("url", ""), body.get("bookmarksPath", ""))
        if not input_urls:
            raise RuntimeError("URL or bookmarks missing")

        urls: list[str] = []
        errors: list[str] = []
        seen: set[str] = set()
        job.update(status="analyzing", progress=3, message="ANALYZING...")
        for raw_url in input_urls:
            source_url, normalized_kind = normalize_source_url(raw_url)
            if should_expand(mode, source_url, normalized_kind):
                opts = ytdlp_opts({
                    "noplaylist": False,
                    "extract_flat": False if is_instagram_media_url(source_url) else "in_playlist",
                    "playlistend": max_items,
                })
                try:
                    with yt_dlp.YoutubeDL(opts) as ydl:
                        listing = ydl.extract_info(source_url, download=False)
                except Exception as exc:  # noqa: BLE001
                    errors.append(f"{source_url}: {readable_error(exc, source_url)}")
                    continue
                expanded = False
                for entry in (listing or {}).get("entries") or []:
                    entry_url = entry_url_from(entry)
                    if entry_url and entry_url not in seen:
                        seen.add(entry_url)
                        urls.append(entry_url)
                        expanded = True
                if not expanded and source_url not in seen:
                    seen.add(source_url)
                    urls.append(source_url)
            elif source_url not in seen:
                seen.add(source_url)
                urls.append(source_url)

        if not urls:
            raise RuntimeError(errors[0] if errors else "No URLs found")

        files: list[str] = []
        total = len(urls)
        for index, url in enumerate(urls, start=1):
            if job.get("cancel"):
                raise RuntimeError("STOPPED")
            try:
                meta = download_one(yt_dlp, ffmpeg_location, job, body, output_dir, url, index, total)
                if auto_analyze:
                    job.update(status="analyzing", progress=min(98, round(5 + (index / total) * 90, 1)),
                               message=f"VISUAL ANALYSIS {index}/{total}")
                    try:
                        analyzed = analyze_and_rename(Path(meta["file"]), output_dir)
                        meta_path = metadata_path(Path(analyzed["file"]), output_dir)
                        if meta_path.exists():
                            meta = json.loads(meta_path.read_text(encoding="utf-8"))
                    except Exception as exc:  # noqa: BLE001
                        errors.append(f"{url}: analysis skipped: {exc}")
                files.append(meta["file"])
                job.update(files=files, file=meta["file"], metadata=meta)
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{url}: {readable_error(exc, url)}")

        if not files:
            raise RuntimeError(errors[0] if errors else "No video file was created")
        job.update(status="ready", progress=100,
                   message="READY" if len(files) == 1 else f"READY {len(files)} FILES",
                   file=files[-1], files=files, error=" | ".join(errors[:3]) or None)
    except Exception as exc:  # noqa: BLE001
        if str(exc) == "STOPPED":
            job.update(status="stopped", progress=0, message="STOPPED", error=None)
        else:
            job.update(status="error", progress=100, message="ERROR", error=str(exc))


def imports_payload(output_dir: Path | None = None) -> dict:
    target_dir = ensure_dirs(output_dir)
    items = []
    roots = [videos_dir(target_dir), target_dir]
    video_paths = []
    seen_paths: set[Path] = set()
    for root in roots:
        for path in root.glob("*"):
            if path.suffix.lower() in VIDEO_EXTS and path not in seen_paths:
                seen_paths.add(path)
                video_paths.append(path)
    for path in sorted(video_paths, key=lambda p: p.stat().st_mtime, reverse=True):
        meta_path = metadata_path(path, target_dir)
        if not meta_path.exists():
            meta_path = path.with_suffix(".json")
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
        except Exception:
            meta = {}
        items.append({
            "name": path.name,
            "path": str(path),
            "size": path.stat().st_size,
            "modified": path.stat().st_mtime,
            "metadata": meta,
        })
    return {
        "folder": str(target_dir),
        "videos_folder": str(videos_dir(target_dir)),
        "assets_folder": str(assets_dir(target_dir)),
        "items": items,
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "VIDZDownload/1.0"

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("[%s] %s\n" % (time.strftime("%H:%M:%S"), fmt % args))

    def send_bytes(self, code: int, data: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_json(self, code: int, data: dict) -> None:
        self.send_bytes(code, json.dumps(data, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0") or "0")
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        return json.loads(raw or "{}")

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path
        if path in {"/", "/vidzdownload", "/vidzdownator", "/vidz-grabber"}:
            self.send_bytes(200, HTML.encode("utf-8"), "text/html; charset=utf-8")
            return
        if path == "/logo.png":
            for logo_path in LOGO_PATHS:
                if logo_path.exists():
                    self.send_bytes(200, logo_path.read_bytes(), "image/png")
                    return
            self.send_json(404, {"error": "Logo not found"})
            return
        if path == "/api/imports":
            query = parse_qs(parsed.query)
            output_value = (query.get("outputFolder") or query.get("output_folder") or [""])[0]
            output_dir = resolve_output_dir(output_value) if output_value else resolve_output_dir()
            self.send_json(200, imports_payload(output_dir))
            return
        if path == "/api/config":
            output_dir = resolve_output_dir()
            config = load_config()
            self.send_json(200, {
                "output_folder": str(output_dir),
                "default_output_folder": str(DEFAULT_IMPORTS_DIR),
                "videos_folder": str(videos_dir(output_dir)),
                "assets_folder": str(assets_dir(output_dir)),
                "auto_analyze": bool(config.get("auto_analyze")),
            })
            return
        match = re.match(r"^/api/jobs/([a-f0-9]+)$", path)
        if match:
            job = JOBS.get(match.group(1))
            if not job:
                self.send_json(404, {"error": "Unknown job"})
                return
            self.send_json(200, {k: v for k, v in job.items() if k != "cancel"})
            return
        self.send_json(404, {"error": "Not found"})

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/api/download":
            body = self.read_json()
            if not (body.get("url") or body.get("bookmarksPath") or "").strip():
                self.send_json(400, {"error": "URL or bookmarks missing"})
                return
            job_id = uuid.uuid4().hex[:8]
            JOBS[job_id] = {
                "id": job_id,
                "status": "queued",
                "progress": 0,
                "message": "QUEUED",
                "error": None,
                "file": None,
                "files": [],
                "metadata": None,
                "cancel": False,
            }
            threading.Thread(target=worker, args=(job_id, body), daemon=True).start()
            self.send_json(200, {"job_id": job_id})
            return
        if path == "/api/open-folder":
            body = self.read_json()
            output_dir = ensure_dirs(resolve_output_dir(body.get("outputFolder") or body.get("output_folder")))
            config = load_config()
            config["output_folder"] = str(output_dir)
            if "autoAnalyze" in body or "auto_analyze" in body:
                config["auto_analyze"] = truthy(body.get("autoAnalyze") or body.get("auto_analyze"))
            save_config(config)
            try:
                if sys.platform == "darwin":
                    subprocess.Popen(["open", str(output_dir)])
                elif os.name == "nt":
                    os.startfile(str(output_dir))  # type: ignore[attr-defined]
                else:
                    subprocess.Popen(["xdg-open", str(output_dir)])
                self.send_json(200, {"ok": True, "folder": str(output_dir)})
            except Exception as exc:  # noqa: BLE001
                self.send_json(500, {"ok": False, "error": str(exc), "folder": str(output_dir)})
            return
        if path == "/api/config":
            body = self.read_json()
            output_dir = ensure_dirs(resolve_output_dir(body.get("outputFolder") or body.get("output_folder")))
            config = load_config()
            config["output_folder"] = str(output_dir)
            config["auto_analyze"] = truthy(body.get("autoAnalyze") or body.get("auto_analyze"))
            save_config(config)
            self.send_json(200, {
                "ok": True,
                "output_folder": str(output_dir),
                "videos_folder": str(videos_dir(output_dir)),
                "assets_folder": str(assets_dir(output_dir)),
                "auto_analyze": bool(config.get("auto_analyze")),
            })
            return
        if path == "/api/choose-folder":
            body = self.read_json()
            start_dir = ensure_dirs(resolve_output_dir(body.get("outputFolder") or body.get("output_folder")))
            try:
                if sys.platform != "darwin":
                    raise RuntimeError("Folder picker is only available on macOS")
                picked = subprocess.check_output([
                    "osascript",
                    "-e", "set defaultFolder to POSIX file " + json.dumps(str(start_dir)),
                    "-e", 'POSIX path of (choose folder with prompt "Choose VIDZDOWNLOAD output folder" default location defaultFolder)',
                ], text=True).strip()
                output_dir = ensure_dirs(resolve_output_dir(picked))
                config = load_config()
                config["output_folder"] = str(output_dir)
                if "autoAnalyze" in body or "auto_analyze" in body:
                    config["auto_analyze"] = truthy(body.get("autoAnalyze") or body.get("auto_analyze"))
                save_config(config)
                self.send_json(200, {
                    "ok": True,
                    "output_folder": str(output_dir),
                    "videos_folder": str(videos_dir(output_dir)),
                    "assets_folder": str(assets_dir(output_dir)),
                })
            except Exception as exc:  # noqa: BLE001
                self.send_json(500, {"ok": False, "error": str(exc)})
            return
        if path == "/api/analyze-last":
            body = self.read_json()
            output_dir = ensure_dirs(resolve_output_dir(body.get("outputFolder") or body.get("output_folder")))
            config = load_config()
            config["output_folder"] = str(output_dir)
            if "autoAnalyze" in body or "auto_analyze" in body:
                config["auto_analyze"] = truthy(body.get("autoAnalyze") or body.get("auto_analyze"))
            save_config(config)
            raw_file = (body.get("file") or "").strip()
            target = None
            if raw_file:
                candidate = Path(raw_file).expanduser()
                if not candidate.is_absolute():
                    candidate = output_dir / candidate
                if candidate.exists() and candidate.suffix.lower() in VIDEO_EXTS:
                    target = candidate
            if not target:
                target = latest_video(output_dir)
            try:
                if not target:
                    raise RuntimeError("No video file to analyze")
                self.send_json(200, analyze_and_rename(target, output_dir))
            except Exception as exc:  # noqa: BLE001
                self.send_json(500, {"ok": False, "error": str(exc)})
            return
        match = re.match(r"^/api/jobs/([a-f0-9]+)/stop$", path)
        if match:
            job = JOBS.get(match.group(1))
            if not job:
                self.send_json(404, {"error": "Unknown job"})
                return
            job["cancel"] = True
            job.update(status="stopping", message="STOPPING...")
            self.send_json(200, {"ok": True})
            return
        if path == "/api/send":
            self.send_json(200, {"ok": True, "folder": str(resolve_output_dir())})
            return
        self.send_json(404, {"error": "Not found"})


def find_port(start: int = 8765) -> int:
    import socket
    for port in range(start, start + 50):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise RuntimeError("No free local port found")


def main() -> None:
    output_dir = ensure_dirs()
    port = 8765
    if "--port" in sys.argv:
        index = sys.argv.index("--port")
        port = int(sys.argv[index + 1])
    else:
        port = find_port(8765)
    url = f"http://127.0.0.1:{port}/vidzdownload"
    print("VIDZDOWNLOAD")
    print(f"URL:    {url}")
    print(f"OUTPUT: {output_dir}")
    print("STOP:   Ctrl+C")
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    if "--no-browser" not in sys.argv:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
