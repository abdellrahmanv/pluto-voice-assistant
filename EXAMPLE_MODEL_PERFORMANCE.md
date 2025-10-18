# 🤖 Model Performance Analysis - Example Output

*This section appears in the performance report after the summary*

---

## 🤖 Model Performance Analysis

*Detailed performance metrics for each AI model*

---

### 🎤 Speech-to-Text (STT)

```
╔══════════════════════════════════════════════════════════════════════╗
║ 🔵 Model: whisper-tiny                                              ║
╚══════════════════════════════════════════════════════════════════════╝
```

**Configuration:**
```
  model_size: tiny
  device: cpu
  language: en
  temperature: 0.0
  beam_size: 5
  fp16: False
```

**Performance Metrics:**

- **Invocations:** 15 times
- **Average Latency:** 187ms
- **Best Performance:** 145ms
- **Worst Performance:** 234ms
- **Target:** <200ms: Excellent, <500ms: Good

**Performance Score:** 107/100 🟢 EXCELLENT

**Latency Distribution:**

```
Best:     145ms ██████████████████████████████░░░░░░░░░░░░░░░░░░░░
Average:  187ms █████████████████████████████████████░░░░░░░░░░░░░
Worst:    234ms ██████████████████████████████████████████████████
```

**Latency Trend:**

```
▃▄▅▃▄▃▄▅▆▅▄▃▄▅▃▄▃▂▃▄▅▆▅▄▃▄▅▆▅▄▃▄▅▃▄▃▄▅▆▅▄▃▄▅▃▄▃▂
Showing 15 samples over 15 total invocations
```

**Target vs Actual:**

```
Target:   200ms ████████████████████████████████████████████████ 🟢
Actual:   187ms ███████████████████████████████████████████░░░░░ 🟢

✨ 7% faster than target!
```

---

### 🧠 Language Model (LLM)

```
╔══════════════════════════════════════════════════════════════════════╗
║ 🔵 Model: qwen2.5:0.5b-instruct-q4_k_M                              ║
╚══════════════════════════════════════════════════════════════════════╝
```

**Configuration:**
```
  model: qwen2.5:0.5b-instruct-q4_k_M
  host: http://localhost:11434
  temperature: 0.7
  top_p: 0.9
  max_tokens: 150
  max_history: 5
  stream: False
```

**Performance Metrics:**

- **Invocations:** 15 times
- **Average Latency:** 892ms
- **Best Performance:** 678ms
- **Worst Performance:** 1234ms
- **Target:** <1500ms: Excellent, <3000ms: Good

**Performance Score:** 168/100 🟢 EXCELLENT

**Latency Distribution:**

```
Best:     678ms ███████████████████████████░░░░░░░░░░░░░░░░░░░░░░░
Average:  892ms █████████████████████████████████████░░░░░░░░░░░░░
Worst:   1234ms ██████████████████████████████████████████████████
```

**Latency Trend:**

```
▅▆▇█▇▆▅▆▇█▇▆▅▆▇▆▅▄▅▆▇█▇▆▅▆▇█▇▆▅▆▇▆▅▄▅▆▇█▇▆▅▆▇▆▅▄
Showing 15 samples over 15 total invocations
```

**Target vs Actual:**

```
Target:  1500ms ████████████████████████████████████████████████ 🟢
Actual:   892ms █████████████████████████████░░░░░░░░░░░░░░░░░░ 🟢

✨ 41% faster than target!
```

---

### 🔊 Text-to-Speech (TTS)

```
╔══════════════════════════════════════════════════════════════════════╗
║ 🔵 Model: en_US-lessac-medium                                       ║
╚══════════════════════════════════════════════════════════════════════╝
```

**Configuration:**
```
  model_path: C:\Users\Asus\Desktop\pluto\models\en_US-lessac-medium.onnx
  speaker_id: 0
  length_scale: 1.0
  noise_scale: 0.667
  noise_w: 0.8
  sample_rate: 22050
```

**Performance Metrics:**

- **Invocations:** 15 times
- **Average Latency:** 123ms
- **Best Performance:** 98ms
- **Worst Performance:** 167ms
- **Target:** <150ms: Excellent, <300ms: Good

**Performance Score:** 122/100 🟢 EXCELLENT

**Latency Distribution:**

```
Best:      98ms ██████████████████████████████░░░░░░░░░░░░░░░░░░░░
Average:  123ms █████████████████████████████████████░░░░░░░░░░░░░
Worst:    167ms ██████████████████████████████████████████████████
```

**Latency Trend:**

```
▂▃▄▃▂▃▄▅▄▃▂▃▄▃▂▁▂▃▄▅▄▃▂▃▄▅▄▃▂▃▄▃▂▁▂▃▄▅▄▃▂▃▄▃▂▁
Showing 15 samples over 15 total invocations
```

**Target vs Actual:**

```
Target:  150ms ████████████████████████████████████████████████ 🟢
Actual:  123ms ████████████████████████████████████████░░░░░░░░ 🟢

✨ 18% faster than target!
```

---

## 📊 Key Insights

### Model Performance Summary:

1. **🎤 Whisper Tiny (STT)**: Fast and efficient, beating target by 7%
   - Excellent for real-time speech recognition on Raspberry Pi
   - Consistent performance with low variance

2. **🧠 Qwen2.5 0.5B (LLM)**: Outstanding performance, 41% faster than target
   - Quantized model (Q4_K_M) provides great speed-accuracy balance
   - Well-suited for conversational AI on edge devices

3. **🔊 Piper Lessac Medium (TTS)**: Extremely fast, 18% faster than target
   - Neural TTS with natural voice quality
   - Low latency makes conversations feel responsive

### Overall Assessment:

- ✅ All models performing EXCELLENTLY
- ✅ Total pipeline latency well under 2 seconds
- ✅ Great model selection for Raspberry Pi 5
- ✅ No optimization needed - continue monitoring

---

*This detailed model breakdown helps you understand each component's performance individually, making it easier to identify bottlenecks and optimize specific models if needed.*
