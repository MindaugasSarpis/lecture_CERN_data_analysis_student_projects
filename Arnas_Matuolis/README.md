# uludus/fightingapp android

Android application for an AI assisted martial arts learning platform.

Initially created for Tesonet's AI-only hackathon where we won 3rd place. Heavily vibe-coded, but fairly understandable, just very messy and not really clean.

# Main results?
5k cash, 2k google cloud credits, 2 year nordvpn, 5gb saily, cool connections.

# How to launch yourself?
No apk because I can't make releases for this and it'd be large, so you'll have to build it yourself.

You build it pretty much as any other android app - download android studio, clone this project, sync, run in emulator or on device. [This is a great resource if you've never had to do this.](https://developer.android.com/courses/pathways/android-basics-compose-unit-1-pathway-2)

# Screenshots

<img width="250"  src="https://github.com/user-attachments/assets/6b2fba8c-9890-46e5-b2dd-47116a21f6e9" />
<img width="250" src="https://github.com/user-attachments/assets/e6d5a61f-21e4-46d1-8c37-9abfb35df5bc" />
<img width="250" src="https://github.com/user-attachments/assets/62864ab0-4188-418c-b6b7-98a5ed04af48" />
<img width="250" src="https://github.com/user-attachments/assets/c180c2cc-5935-4f78-9605-5dff9aa0e8db" />
<img width="250" src="https://github.com/user-attachments/assets/8847c812-400b-43e4-af34-aa0889e8ba07" />
<img width="250" src="https://github.com/user-attachments/assets/eec17c3a-3837-4ae2-a463-523bd7928005" />
<img width="250" src="https://github.com/user-attachments/assets/296d1fb9-37f4-46f1-b951-9f5bb19e4d00" />
<img width="250" src="https://github.com/user-attachments/assets/0718a10c-d399-4733-965b-aa6deafe94e2" />
<img width="250" src="https://github.com/user-attachments/assets/8858d37a-3257-410e-b37f-578c323b2d6a" />

(the last video is sideways lol, lil backend error but it works whatever)

# App layout
As any other android app - go to app/src/main/java/com/arnasmat/fightingapp to see the app files.

General overview:
```
FightingApplication is for Dependency injection (Hilt)
MainActivity is the application entrypoint.
| data - everything to do with data. We interact with local databases (datastore/sqlite) & remote API through files here.
| di - dependency injection.
| domain - models, domain, etc., various data types, classes we work with
| presentation - everything you see (UI, screens) and the bridge between UI and other layers (ViewModel)
| ui.theme - general theme, design system per se
| util - useful things for other layers, here the only file is sounddetector
```

app/build.gradle.kts for all dependencies.

# What I learned
- Working with camera and videos on android (camerax and medai3 exoplayer on compose)
- Interaction between views & compose
- Dagger-Hilt
- Vibe-coding on android
- Making android apps quick
- Permissions stuff

# Technologies
- Kotlin & coroutines
- General android libs & viewmodels  
- Jetpack Compose & Material3 for UI
- MVVM architecture
- Dagger-Hilt for DI
- Camerax
- Datastore
- Retrofit on OKHttp
- Coil
