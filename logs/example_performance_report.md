# 🪐 Pluto Performance Report

**Session ID:** `20251018_143022`

**Start Time:** 2025-10-18 14:30:22

**Duration:** 5m 42s

---

## 📊 Executive Summary

| Metric | Value |
|--------|-------|
| **Conversations** | 12 |
| **Errors** | 0 |
| **Warnings** | 0 |
| **Avg End-to-End Latency** | 2340ms |
| **Avg STT Latency** | 245ms |
| **Avg LLM Latency** | 1890ms |
| **Avg TTS Latency** | 205ms |
| **Avg CPU Usage** | 52.3% |
| **Avg Memory Usage** | 1245MB |
| **Peak Temperature** | 64.5°C |

---

## ⏱️ Latency Performance

### Component Latency Comparison

```mermaid
%%{init: {'theme':'base'}}%%
graph LR
    STT["STT<br/>245ms"]
    LLM["LLM<br/>1890ms"]
    TTS["TTS<br/>205ms"]
    TOTAL["TOTAL<br/>2340ms"]
```

### Latency Over Time

#### STT Latency Timeline

```mermaid
%%{init: {'theme':'base', 'themeVariables': {'xyChart': {'backgroundColor': 'transparent'}}}}%%
xychart-beta
    title "STT Response Time"
    x-axis [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    y-axis "Latency (ms)" 0 --> 350
    line [245, 189, 234, 210, 198, 267, 223, 215, 241, 256, 198, 234]
```

#### LLM Latency Timeline

```mermaid
%%{init: {'theme':'base', 'themeVariables': {'xyChart': {'backgroundColor': 'transparent'}}}}%%
xychart-beta
    title "LLM Response Time"
    x-axis [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    y-axis "Latency (ms)" 0 --> 2500
    line [1890, 1750, 1820, 2100, 1950, 1880, 1920, 1850, 1780, 2050, 1890, 1920]
```

#### TTS Latency Timeline

```mermaid
%%{init: {'theme':'base', 'themeVariables': {'xyChart': {'backgroundColor': 'transparent'}}}}%%
xychart-beta
    title "TTS Response Time"
    x-axis [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    y-axis "Latency (ms)" 0 --> 300
    line [205, 198, 210, 223, 189, 215, 201, 207, 198, 212, 205, 199]
```

#### TOTAL Latency Timeline

```mermaid
%%{init: {'theme':'base', 'themeVariables': {'xyChart': {'backgroundColor': 'transparent'}}}}%%
xychart-beta
    title "TOTAL Response Time"
    x-axis [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    y-axis "Latency (ms)" 0 --> 3000
    line [2340, 2137, 2264, 2533, 2337, 2362, 2344, 2272, 2219, 2518, 2293, 2353]
```

---

## 💻 System Resources

### CPU Usage Over Time

```mermaid
%%{init: {'theme':'base'}}%%
xychart-beta
    title "CPU Usage"
    x-axis [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    y-axis "CPU %" 0 --> 100
    line [45.2, 52.1, 48.9, 55.3, 60.1, 58.4, 51.2, 49.8, 47.5, 50.0, 54.3, 56.7, 52.1, 48.9, 51.5, 53.8, 49.2, 50.7, 52.3, 48.1]
```

### Memory Usage Over Time

```mermaid
%%{init: {'theme':'base'}}%%
xychart-beta
    title "Memory Usage"
    x-axis [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    y-axis "Memory (MB)" 0 --> 1500
    line [1180, 1210, 1195, 1230, 1255, 1248, 1220, 1235, 1242, 1260, 1275, 1268, 1240, 1250, 1265, 1258, 1245, 1252, 1247, 1238]
```

### CPU Temperature Over Time

```mermaid
%%{init: {'theme':'base'}}%%
xychart-beta
    title "CPU Temperature"
    x-axis [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    y-axis "Temperature (°C)" 0 --> 100
    line [58.5, 60.2, 61.5, 62.8, 63.5, 64.2, 64.5, 63.8, 62.5, 61.2, 60.5, 61.8, 62.5, 63.2, 62.8, 61.5, 60.8, 60.2, 59.5, 58.8]
```

---

## 📅 Conversation Timeline

```mermaid
%%{init: {'theme':'base'}}%%
gantt
    title Conversation Flow
    dateFormat X
    axisFormat %M:%S
    Conversation 1 :conv1, 0, 2500
    Conversation 2 :conv2, 5000, 7500
    Conversation 3 :conv3, 10000, 12500
    Conversation 4 :conv4, 15000, 17500
    Conversation 5 :conv5, 20000, 22500
    Conversation 6 :conv6, 25000, 27500
    Conversation 7 :conv7, 30000, 32500
    Conversation 8 :conv8, 35000, 37500
    Conversation 9 :conv9, 40000, 42500
    Conversation 10 :conv10, 45000, 47500
```

---

## 📈 Detailed Statistics

### Latency Breakdown

| Component | Count | Min | Max | Mean | Median | P95 |
|-----------|-------|-----|-----|------|--------|-----|
| **STT** | 12 | 189ms | 267ms | 245ms | 234ms | 262ms |
| **LLM** | 12 | 1750ms | 2100ms | 1890ms | 1890ms | 2065ms |
| **TTS** | 12 | 189ms | 223ms | 205ms | 205ms | 218ms |
| **TOTAL** | 12 | 2137ms | 2533ms | 2340ms | 2344ms | 2511ms |

### System Resource Statistics

| Resource | Min | Max | Mean |
|----------|-----|-----|------|
| **CPU Usage** | 45.2% | 60.1% | 52.3% |
| **Memory Usage** | 1180MB | 1275MB | 1245MB |
| **CPU Temperature** | 58.5°C | 64.5°C | 61.8°C |

---

## ✅ No Issues Detected

Session completed without errors or warnings.

---
