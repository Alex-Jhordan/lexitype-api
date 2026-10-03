# UI Component Structure

## 1. Vue 3 Component Tree Hierarchy

The user interface of LexiType Space is structured modularly. The root of the application (`App.vue`) acts as the main orchestrator that renders the corresponding component according to the active value in the Pinia state machine store.

Each component features explicit identifiers (`data-testid`) on its key elements to enable clean automation with Vitest + Vue Test Utils and Playwright, preventing brittleness caused by Tailwind CSS class changes.

* **`App.vue`**
  * **`InstructionsModal.vue`** (Rendered in `INSTRUCTIONS` state)
  * **`TopicInputScreen.vue`** (Rendered in `TOPIC_INPUT` state)
  * **`FuelLoadingScreen.vue`** (Rendered in `LLM_LOADING` state)
  * **`ServiceUnavailableScreen.vue`** (Rendered in `SERVICE_UNAVAILABLE` state)
  * **`GameScreen.vue`** (Rendered in `PLAYING` state)
    * **`GameHeader.vue`** (Top bar: elapsed game time and 5-life container)
    * **`GameCanvas.vue`** (Interactive HTML5 Canvas 2D)
    * **`TypingInputDisplay.vue`** (Bottom bar with real-time visualization of typed text)
  * **`GameOverModal.vue`** (Rendered in `GAME_OVER` state)
    * **`GlossarySection.vue`** (Left column: static list of the 5 words and their definitions)
    * **`MetricsSection.vue`** (Right column: WPM, accuracy, and destroyed vs. fallen words)

## 2. Definition of Screens, Modals, and TDD Testing Specifications

### `InstructionsModal.vue` (`INSTRUCTIONS`)

* **Purpose:** Display initial rules and game controls to the player.
* **UI Elements:**
  * Main title in retro-arcade typography and a brief thematic description.
  * Visual rule summary: 5 starting lives, keyboard usage for shooting, and words that accelerate as they are destroyed.
  * Primary button (`data-testid="start-btn"`) labeled "Start".
* **TDD Test (Vitest / Component Test):**
  * Verify that clicking `start-btn` triggers the Pinia store mutation to transition state from `INSTRUCTIONS` to `TOPIC_INPUT`.

### `TopicInputScreen.vue` (`TOPIC_INPUT`)

* **Purpose:** Capture the player's topic of interest to send to the backend.
* **UI Elements:**
  * Main text field (`<input data-testid="topic-input">`) styled with Tailwind CSS, auto-focused on screen load.
  * Submit button (`data-testid="submit-topic-btn"`) disabled if input fails validation (minimum 2 characters).
  * Helper message (placeholder): "e.g. Vue.js, Quantum Mechanics, Gastronomy".
* **TDD Test (Vitest / Component Test):**
  * Confirm that `submit-topic-btn` remains disabled with `""` or `"A"`.
  * Confirm that with `"Vue.js"` the button becomes enabled, and submitting changes the state to `LLM_LOADING` while invoking the API service call.

### `FuelLoadingScreen.vue` (`LLM_LOADING`)

* **Purpose:** Provide friendly visual feedback during LLM API response latency.
* **UI Elements:**
  * SVG vector silhouette of the spaceship (`data-testid="fuel-ship-svg"`).
  * Vertical fuel animation and horizontal animated indicator in neon cyan (`cyan-500`) while the API request is pending.
  * Elapsed API wait time, updated once per second.
* **TDD Test (Vitest / Component Test):**
  * Verify correct rendering of the component while the `fetch /api/generate-words` promise is pending.

### `ServiceUnavailableScreen.vue` (`SERVICE_UNAVAILABLE`)

* **Purpose:** Inform the user in case of network failures or API errors (HTTP 503/timeout).
* **UI Elements:**
  * Vector illustration of the spaceship with a visual maintenance indicator.
  * Informational message: "The ship is undergoing repairs. Please try again later."
  * Action button (`data-testid="retry-btn"`): "Try Again".
* **TDD Test (Vitest / Component Test):**
  * Verify that pressing `retry-btn` clears errors and returns the application to the `TOPIC_INPUT` state.

### `GameScreen.vue` (`PLAYING`)

* **Purpose:** Encapsulate the active real-time gaming experience.
* **UI Elements:**
  * **`GameHeader`:** Elapsed-time clock (`data-testid="game-timer"`) on the left and 5 Lucide heart icons (`data-testid="heart-icon"`) on the right.
  * **`GameCanvas`:** HTML5 Canvas 2D canvas (`data-testid="game-canvas"`).
  * **`TypingInputDisplay`:** Bottom container (`data-testid="typing-display"`) showing characters entered in the buffer.
* **TDD Test (Vitest / Component Test):**
  * Confirm that losing 1 life in the game Kernel changes a heart icon state in `GameHeader` to lost/red.
  * Confirm that `typing-display` content reflects the active buffer in real-time.

### `GameOverModal.vue` (`GAME_OVER`)

* **Purpose:** Present educational outcomes and performance metrics at game completion.
* **Structure and UI Elements:**
  * **Glossary (Left column):** Static display of the 5 LLM-generated elements. Shows accented `display_word` alongside `meaning`.
  * **Metrics (Right column):** Numerical panel displaying WPM (`data-testid="wpm-metric"`), Accuracy (`data-testid="accuracy-metric"`), destroyed appearances (`data-testid="destroyed-words-metric"`), and fallen appearances (`data-testid="fallen-words-metric"`). Recycled terms count again for each later outcome.
  * **Modal footer:** Prominent button (`data-testid="play-again-btn"`): "Play Again".
* **TDD Test (Vitest / Component Test):**
  * Verify that mounting the component in `GAME_OVER` triggers the confetti function (`canvas-confetti`).
  * Verify that the left column renders exactly the 5 store words with their correct `display_word` values.
  * Confirm that pressing `play-again-btn` resets game values and transitions state to `TOPIC_INPUT`.

## 3. Design System and Styling with Tailwind CSS

The visual style follows a retro-arcade space theme using Tailwind CSS color palettes and utilities:

### Background and Container Palette

* **Global Base Background (Body and Canvas):** `bg-slate-950`, representing deep space.
* **Modal and Card Containers:** `bg-zinc-900` with semi-transparent borders (`border-zinc-800`) and a backdrop blur effect (`bg-zinc-900/90 backdrop-blur-md`).

### Base Text and Neutral Palette

* **White / Light Gray (`text-slate-100` / `text-zinc-300`):** Untyped characters of floating words inside the Canvas 2D, informational labels, secondary titles, and glossary descriptions.
* **Neutral Gray (`text-zinc-500` / `border-zinc-700`):** Final metric values that do not reach the high performance threshold, inactive element borders, and visual dividers.

### Neon Accent Palette

* **Neon Cyan (`cyan-500`):** Laser projectiles, ship fuel bar, and active typing interface in the bottom container.
* **Neon Green (`emerald-500`):** Correctly typed letters within canvas words, as well as final metric numerical values in the results modal when achieving high performance (Accuracy >= 90% or WPM >= 40).
* **Neon Red (`rose-500`):** Visual damage indicator on the ship, lost life hearts, and count of fallen words.

### Typography and Custom Fonts

* **Main Titles and Metrics Font:** "Press Start 2P" (imported from Google Fonts), applied to modal titles, final WPM metrics, and counters.
* **Interface and Reading Font (Monospaced):** "JetBrains Mono" (imported from Google Fonts) via the `font-mono` class, used for canvas words, the text input field, and glossary definitions.