# 2D Canvas Mechanics and Game Physics

## 1. Game Engine Architecture and Testability

The game area during the `PLAYING` state is managed through an HTML5 `<canvas>` element controlled by the 2D rendering API. To enable a strict TDD methodology, the game engine architecture is divided into two decoupled layers:

- **Physics and State Kernel Layer (`useGameEngine.ts`):** Pure TypeScript module free of DOM or rendering API dependencies. It encapsulates object coordinates, delta time ($t$), trajectory calculations, the 20-second timer logic, and targeting detection algorithms. This layer is 100% testable using Vitest in a deterministic manner without needing to emulate a real `<canvas>` element.
- **Rendering Layer (`GameCanvas.vue`):** View module that subscribes to the state exposed by the Kernel and executes drawing methods (`ctx.fillText`, `ctx.beginPath`, `ctx.arc`, etc.) within the loop driven by `requestAnimationFrame`.

The engine manages four main rendering layers during each cycle:

1. **Space background:** Starfield with slow vertical scrolling (parallax).
2. **Word entities:** Text for each word, highlighting correctly typed letters in a distinct color.
3. **Laser projectiles:** Animated energy beams fired from the ship toward the target word.
4. **Ship and effects:** Rendering of the spaceship and explosion particles.

---

## 2. Main Render Loop (Game Loop) and Deterministic Cycle

To guarantee that the game runs at the same speed regardless of the monitor's refresh rate, all updates are calculated using a delta time ($t$) expressed in seconds elapsed between frames.

In unit tests with Vitest, time progression is simulated by passing fixed values of $t$ to the Kernel functions without requiring the execution of a real `requestAnimationFrame`.

The loop lifecycle executes across four sequential phases:

- **Phase 1: Clear canvas (Clear):** Clearing the Canvas with `ctx.clearRect(0, 0, width, height)`.
- **Phase 2: State update (Update):**
  - Recalculation of active word $Y$ positions: $Y_{\text{new}} = Y_{\text{current}} + (\text{speed} \times t)$.
  - Recalculation of vector trajectories for laser projectiles in flight.
  - Particle physics update (lifespan, opacity, and dispersion).
  - Evaluation of the global 20.0-second timer.
- **Phase 3: Collision and boundary detection (Check):**
  - Verification of projectile impacts against the target word.
  - Verification of words reaching the bottom boundary of the screen ($Y_{\text{word}} \ge Y_{\text{ship}}$).
- **Phase 4: Rendering (Draw):** Drawing all updated elements onto the canvas in the established layer order.

---

## 3. Fall Physics and Spawn Rate Algorithm

Physics rules and spawn timings are defined using constants verified quantitatively in Vitest tests:

- **Fall speed:** Variable range between 120 and 160 pixels per second (px/s), randomly assigned to each word upon spawning to prevent uniform horizontal fall lines.
- **On-screen limit and spawn frequency:**
  - **Maximum simultaneous limit:** Maximum of 3 words on the canvas at the same time.
  - **Match start:** The first 2 words from the pool are introduced simultaneously.
  - **Periodic frequency:** Every 3.5 seconds elapsed on the Kernel timer, the engine evaluates whether the on-screen word count is less than 3 to launch a new word.
- **Pool Reuse and Cooldown:** Upon word destruction or hitting the base, the word enters a 1.5-second cooldown period before reappearing at a random horizontal ($X$) position.

---

## 4. Targeting System Algorithm and Conflict Resolution

User input is processed through a global `keydown` event listener managed by the game Kernel:

- **Neutral state (Empty buffer `""`):** The system waits for the first typed letter.
- **Conflict resolution algorithm (Target Lock by $Y$ position):** If two or more words on screen start with the same pressed letter, the algorithm evaluates the $Y$ coordinate of each match and automatically locks onto the word with the highest $Y$ coordinate (closest to the ground/ship).
  - *TDD Specification:* The unit test simulates the presence of two words at $Y=100$ and $Y=350$ starting with "A"; when simulating the key event "A", the Kernel must return the word at $Y=350$ as the target.
- **Target Lock:** While the buffer contains characters, subsequent key presses are evaluated exclusively against the locked target word.
- **Wrong key effect:** If the pressed key does not match the next character of the target word, the buffer remains intact, the global `wrong_keypresses` counter (used for calculating accuracy %) increments, and a signal is emitted for the visual rejection effect (shake).
- **Target Unlock via Backspace:** The Backspace key removes the last character from the buffer. If the buffer becomes completely empty (`""`), the current target is immediately released.
- **Cleanup on impact:** If the target word touches the base before being completed, the word is removed, the player loses 1 life, and the Kernel input buffer resets to empty (`""`).

---

## 5. Collision System, Lives, and Particles

### Collision by base impact ($Y_{\text{word}} \ge Y_{\text{ship}}$):
- The active word is removed from the canvas and enters cooldown.
- 1 life is deducted from the total of 5 in the Pinia store.
- The typing buffer is reset to `""`.
- **Termination criteria:** If lives reach 0, the Kernel freezes updates and emits a state transition to `GAME_OVER`.

### Collision by successful destruction:
- Upon typing the final character of the target word, the last projectile triggers a destruction event.
- Between 15 and 20 explosion particles are instantiated with random angles and speeds and a lifespan of 300 ms.
- The count of `destroyed_words` increments by +1.
- Target lock is released and the typing buffer resets to `""`.