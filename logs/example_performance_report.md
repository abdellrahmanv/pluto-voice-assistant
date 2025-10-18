# 🪐 Pluto Performance Report

**Session ID:** `20251018_143022`

**Start Time:** 2025-10-18 14:30:22

**Duration:** 5m 42s

---

## 📊 Performance Score

```mermaid
%%{init: {'theme':'base', 'themeVariables': {'fontSize': '20px'}}}%%
graph LR
    START[" "]:::hidden
    SCORE["✅ GOOD<br/>78/100"]:::good
    START --> SCORE
    classDef hidden fill:none,stroke:none
    classDef excellent fill:#22c55e,stroke:#16a34a,stroke-width:4px,color:#fff,font-size:20px
    classDef good fill:#3b82f6,stroke:#2563eb,stroke-width:4px,color:#fff,font-size:20px
    classDef warning fill:#f59e0b,stroke:#d97706,stroke-width:4px,color:#fff,font-size:20px
    classDef critical fill:#ef4444,stroke:#dc2626,stroke-width:4px,color:#fff,font-size:20px
```

### Session Statistics

```mermaid
%%{init: {'theme':'base'}}%%
graph TD
    CONV["💬 Conversations<br/>12"]:::good
    ERR["✅ Errors<br/>0"]:::excellent
    WARNINGS["✅ Warnings<br/>0"]:::excellent
    classDef excellent fill:#22c55e,stroke:#16a34a,stroke-width:3px,color:#fff
    classDef good fill:#3b82f6,stroke:#2563eb,stroke-width:3px,color:#fff
    classDef warning fill:#f59e0b,stroke:#d97706,stroke-width:3px,color:#fff
    classDef critical fill:#ef4444,stroke:#dc2626,stroke-width:3px,color:#fff
```

### Latency Performance

```mermaid
%%{init: {'theme':'base'}}%%
graph TD
    STT["🎤 STT<br/>245ms<br/>🟡 Acceptable"]:::warning
    LLM["🧠 LLM<br/>1890ms<br/>🟡 Acceptable"]:::warning
    TTS["🔊 TTS<br/>205ms<br/>🟡 Acceptable"]:::warning
    TOTAL["⏱️ TOTAL<br/>2340ms<br/>🟡 Acceptable"]:::warning
    classDef excellent fill:#22c55e,stroke:#16a34a,stroke-width:3px,color:#fff
    classDef warning fill:#f59e0b,stroke:#d97706,stroke-width:3px,color:#fff
    classDef critical fill:#ef4444,stroke:#dc2626,stroke-width:3px,color:#fff
```

### System Resources

```mermaid
%%{init: {'theme':'base'}}%%
graph TD
    CPU["💻 CPU<br/>52.3%<br/>🟡 Moderate"]:::warning
    MEM["🧠 Memory<br/>1245MB<br/>🟢 Good"]:::excellent
    TEMP["🌡️ Temperature<br/>64.5°C<br/>🟢 Cool"]:::excellent
    classDef excellent fill:#22c55e,stroke:#16a34a,stroke-width:3px,color:#fff
    classDef warning fill:#f59e0b,stroke:#d97706,stroke-width:3px,color:#fff
    classDef critical fill:#ef4444,stroke:#dc2626,stroke-width:3px,color:#fff
```

---

## ⏱️ Latency Performance Analysis

### Component Breakdown (Average)

```mermaid
%%{init: {'theme':'base'}}%%
graph TD
    STT["🎤 STT<br/>245ms<br/>🟡 Acceptable"]:::warning
    LLM["🧠 LLM<br/>1890ms<br/>🟡 Acceptable"]:::warning
    TTS["🔊 TTS<br/>205ms<br/>🟡 Acceptable"]:::warning
    TOTAL["⏱️ TOTAL<br/>2340ms<br/>🟡 Acceptable"]:::warning
    classDef excellent fill:#22c55e,stroke:#16a34a,stroke-width:3px,color:#fff
    classDef warning fill:#f59e0b,stroke:#d97706,stroke-width:3px,color:#fff
    classDef critical fill:#ef4444,stroke:#dc2626,stroke-width:3px,color:#fff
```

### Performance vs Targets

```mermaid
%%{init: {'theme':'base'}}%%
xychart-beta
    title "Latency: Target vs Actual"
    x-axis [STT, LLM, TTS, Total]
    y-axis "Latency (ms)" 0 --> 3000
    bar "🎯 Target" [200, 1500, 150, 2000]
    bar "📊 Actual" [245, 1890, 205, 2340]
```

### Response Time Trends

#### 🎤 STT Latency Timeline

```mermaid
%%{init: {'theme':'base', 'themeVariables': {'xyChart': {'backgroundColor': 'transparent'}}}}%%
xychart-beta
    title "STT Response Time"
    x-axis [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    y-axis "Latency (ms)" 0 --> 350
    line [245, 189, 234, 210, 198, 267, 223, 215, 241, 256, 198, 234]
```

#### 🧠 LLM Latency Timeline

```mermaid
%%{init: {'theme':'base', 'themeVariables': {'xyChart': {'backgroundColor': 'transparent'}}}}%%
xychart-beta
    title "LLM Response Time"
    x-axis [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    y-axis "Latency (ms)" 0 --> 2500
    line [1890, 1750, 1820, 2100, 1950, 1880, 1920, 1850, 1780, 2050, 1890, 1920]
```

#### 🔊 TTS Latency Timeline

```mermaid
%%{init: {'theme':'base', 'themeVariables': {'xyChart': {'backgroundColor': 'transparent'}}}}%%
xychart-beta
    title "TTS Response Time"
    x-axis [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    y-axis "Latency (ms)" 0 --> 300
    line [205, 198, 210, 223, 189, 215, 201, 207, 198, 212, 205, 199]
```

#### ⏱️ TOTAL Latency Timeline

```mermaid
%%{init: {'theme':'base', 'themeVariables': {'xyChart': {'backgroundColor': 'transparent'}}}}%%
xychart-beta
    title "TOTAL Response Time"
    x-axis [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    y-axis "Latency (ms)" 0 --> 3000
    line [2340, 2137, 2264, 2533, 2337, 2362, 2344, 2272, 2219, 2518, 2293, 2353]
```

---

## 💻 System Resource Analysis

### System Health Overview

```mermaid
%%{init: {'theme':'base'}}%%
graph TD
    CPU["💻 CPU<br/>52.3%<br/>🟡 Moderate"]:::warning
    MEM["🧠 Memory<br/>1245MB<br/>🟢 Good"]:::excellent
    TEMP["🌡️ Temperature<br/>64.5°C<br/>🟢 Cool"]:::excellent
    classDef excellent fill:#22c55e,stroke:#16a34a,stroke-width:3px,color:#fff
    classDef warning fill:#f59e0b,stroke:#d97706,stroke-width:3px,color:#fff
    classDef critical fill:#ef4444,stroke:#dc2626,stroke-width:3px,color:#fff
```

### CPU Usage Over Time

**Peak:** 60.1% | **Average:** 52.3%

```mermaid
%%{init: {'theme':'base'}}%%
xychart-beta
    title "CPU Usage (Target: <50% Good, <70% OK)"
    x-axis ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20"]
    y-axis "CPU %" 0 --> 100
    line [45.2, 52.1, 48.9, 55.3, 60.1, 58.4, 51.2, 49.8, 47.5, 50.0, 54.3, 56.7, 52.1, 48.9, 51.5, 53.8, 49.2, 50.7, 52.3, 48.1]
```

### Memory Usage Over Time

**Peak:** 1275MB | **Average:** 1245MB

```mermaid
%%{init: {'theme':'base'}}%%
xychart-beta
    title "Memory Usage (Target: <1500MB Good, <2500MB OK)"
    x-axis ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20"]
    y-axis "Memory (MB)" 0 --> 1500
    line [1180, 1210, 1195, 1230, 1255, 1248, 1220, 1235, 1242, 1260, 1275, 1268, 1240, 1250, 1265, 1258, 1245, 1252, 1247, 1238]
```

### CPU Temperature Over Time

**Peak:** 64.5°C | **Average:** 61.8°C

```mermaid
%%{init: {'theme':'base'}}%%
xychart-beta
    title "CPU Temperature (Target: <65°C Cool, <75°C OK)"
    x-axis ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20"]
    y-axis "Temperature (°C)" 0 --> 100
    line [58.5, 60.2, 61.5, 62.8, 63.5, 64.2, 64.5, 63.8, 62.5, 61.2, 60.5, 61.8, 62.5, 63.2, 62.8, 61.5, 60.8, 60.2, 59.5, 58.8]
```

> 🟢 **INFO:** Temperature 64.5°C is within acceptable range
> - Normal operation, but cooling could improve longevity

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

## 📈 Detailed Performance Metrics

### Latency Statistics (Min / Mean / Max)

**🎤 STT** (12 samples)

```mermaid
%%{init: {'theme':'base'}}%%
xychart-beta
    title "STT Latency Distribution"
    x-axis ["Min", "Mean", "Max"]
    y-axis "Latency (ms)" 0 --> 293
    bar [189, 245, 267]
```

**🧠 LLM** (12 samples)

```mermaid
%%{init: {'theme':'base'}}%%
xychart-beta
    title "LLM Latency Distribution"
    x-axis ["Min", "Mean", "Max"]
    y-axis "Latency (ms)" 0 --> 2310
    bar [1750, 1890, 2100]
```

**🔊 TTS** (12 samples)

```mermaid
%%{init: {'theme':'base'}}%%
xychart-beta
    title "TTS Latency Distribution"
    x-axis ["Min", "Mean", "Max"]
    y-axis "Latency (ms)" 0 --> 245
    bar [189, 205, 223]
```

**⏱️ END-TO-END** (12 samples)

```mermaid
%%{init: {'theme':'base'}}%%
xychart-beta
    title "END-TO-END Latency Distribution"
    x-axis ["Min", "Mean", "Max"]
    y-axis "Latency (ms)" 0 --> 2786
    bar [2137, 2340, 2533]
```

### System Resource Range

**💻 CPU Usage**

```mermaid
%%{init: {'theme':'base'}}%%
xychart-beta
    title "CPU Usage Distribution"
    x-axis ["Min", "Mean", "Max"]
    y-axis "CPU %" 0 --> 100
    bar [45.2, 52.3, 60.1]
```

**🧠 Memory Usage**

```mermaid
%%{init: {'theme':'base'}}%%
xychart-beta
    title "Memory Usage Distribution"
    x-axis ["Min", "Mean", "Max"]
    y-axis "Memory (MB)" 0 --> 1530
    bar [1180, 1245, 1275]
```

**🌡️ CPU Temperature**

```mermaid
%%{init: {'theme':'base'}}%%
xychart-beta
    title "Temperature Distribution"
    x-axis ["Min", "Mean", "Max"]
    y-axis "Temperature (°C)" 0 --> 100
    bar [58.5, 61.8, 64.5]
```

---

## ✅ No Issues Detected

Session completed without errors or warnings.

---

## 💡 Recommendations

### Performance Improvements

🟡 **Latency:** Total response time could be improved (>2340ms)
   - LLM is the bottleneck - consider model optimization
   - Check system load during conversations
🟡 **STT Performance:** Speech recognition is slow (>245ms)
   - Whisper Tiny should be <250ms on RPi 4
   - Check CPU availability during STT processing
🟠 **LLM Performance:** Language model inference is slow (>1890ms)
   - This is expected on RPi 4 with Qwen2.5:0.5B
   - Consider: RPi 5, or cloud-based LLM (OpenAI API)
🟡 **CPU Usage:** CPU usage is high (52.3%)
   - Normal for active conversations, but monitor stability

---
