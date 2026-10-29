# Mobile Debugging Guide

> **Stop console.log() debugging!**
> Mobile apps have complex native layers. Text logs are not enough.
> **This file teaches effective mobile debugging strategies.**

---

## Mobile Debugging Mindset

```
Web Debugging:      Mobile Debugging:
┌──────────────┐    ┌──────────────┐
│  Browser     │    │  JS ⇄ Native │
│  DevTools    │    │  Native UI   │
│  Network Tab │    │  GPU/Memory  │
└──────────────┘    │  Threads     │
                    └──────────────┘
```

**Key Differences:**
1.  **Native Layer:** JS code works, but app crashes? It's likely native (Java/Obj-C).
2.  **Deployment:** You can't just "refresh". State gets lost or stuck.
3.  **Network:** SSL Pinning, proxy settings are harder.
4.  **Device Logs:** `adb logcat` and `Console.app` are your truth.
5.  **Architecture:** React Native's New Architecture (default since 0.76, the only architecture from 0.82) replaces the old asynchronous bridge with JSI, plus Turbo Native Modules and the Fabric renderer. Debug JS with React Native DevTools; debug native code in Xcode/Android Studio.

---

## 🚫 AI DEBUGGING ANTI-PATTERNS

| ❌ Default | ✅ Mobile-Correct |
|------------|-------------------|
| "Add console.logs" | Use React Native DevTools (breakpoints, React Components/Profiler) / Reactotron |
| "Check network tab" | Use Charles Proxy / Proxyman |
| "It works on simulator" | **Test on Real Device** (HW specific bugs) |
| "Reinstall node_modules" | **Clean Native Build** (Gradle/Pod cache) |
| Ignored native logs | Read `logcat` / Xcode logs |

---

## 1. The Toolset

### ⚡ React Native & Expo

| Tool | Purpose | Best For |
|------|---------|----------|
| **React Native DevTools** | Console, breakpoints, React Components & Profiler, Memory (Network/Performance panels in 0.83+) | Default JS debugger since RN 0.76 (Dev Menu → "Open DevTools" or press `j` in Metro) |
| **Reactotron** | State/API/Redux | JS side debugging |
| **Expo Tools** | Element inspector | Quick UI checks |

### 🛠️ Native Layer (The Deep Dive)

| Tool | Platform | Command | Why Use? |
|------|----------|---------|----------|
| **Logcat** | Android | `adb logcat` | Native crashes, ANRs |
| **Console** | iOS | via Xcode | Native exceptions, memory |
| **Layout Insp.** | Android | Android Studio | UI hierarchy bugs |
| **View Insp.** | iOS | Xcode | UI hierarchy bugs |

---

## 2. Common Debugging Workflows

### 🕵️ "The App Just Crashed" (Red Screen vs Crash to Home)

**Scenario A: Red Screen (JS Error)**
- **Cause:** Undefined is not an object, import error.
- **Fix:** Read the stack trace on screen. It's usually clear.

**Scenario B: Crash to Home Screen (Native Crash)**
- **Cause:** Native module failure, memory OOM, permission usage without declaration.
- **Tools:**
    - **Android:** `adb logcat *:E` (Filter for Errors)
    - **iOS:** Open Xcode → Window → Devices → View Device Logs

> **💡 Pro Tip:** If app crashes immediately on launch, it's almost 100% a native configuration issue (Info.plist, AndroidManifest.xml).

### 🌐 "API Request Failed" (Network)

**Web:** Open Chrome DevTools → Network.
**Mobile:** *You usually can't see this easily.*

**Solution 1: React Native DevTools / Reactotron**
- React Native DevTools Network panel (RN 0.83+) records `fetch`, `XMLHttpRequest`, and `<Image>` requests; Reactotron also logs JS-side requests.

**Solution 2: Proxy (Charles/Proxyman)**
- **Hard but powerful.** See ALL traffic even from native SDKs.
- Requires installing SSL cert on device.

### 🐢 "The UI is Laggy" (Performance)

**Don't guess.** measure.
- **React Native:** Performance Monitor (Shake menu).
- **Android:** "Profile GPU Rendering" in Developer Options.
- **Issues:**
    - **JS FPS drop:** Heavy calculation in JS thread.
    - **UI FPS drop:** Too many views, intricate hierarchy, heavy images.

---

## 3. Platform-Specific Nightmares

### Android
- **Gradle Sync Fail:** Usually Java version mismatch or duplicate classes.
- **Emulator Network:** Emulator `localhost` is `10.0.2.2`, NOT `127.0.0.1`.
- **Cached Builds:** `./gradlew clean` is your best friend.

### iOS
- **Pod Issues:** `pod deintegrate && pod install`.
- **Signing Errors:** Check Team ID and Bundle Identifier.
- **Cache:** Xcode → Product → Clean Build Folder.

---

## 📝 DEBUGGING CHECKLIST

- [ ] **Is it a JS or Native crash?** (Red screen or home screen?)
- [ ] **Did you clean build?** (Native caches are aggressive)
- [ ] **Are you on a real device?** (Simulators hide concurrency bugs)
- [ ] **Did you check the native logs?** (Not just terminal output)

> **Remember:** If JavaScript looks perfect but the app fails, look closer at the Native side.
