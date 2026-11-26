# Pookie — Pocket Creature

Pookie is a small interactive desktop creature built with Python and Pygame for the Pocket Creature mini challenge. It lives in a warm pastel window, reacts when you pet it or feed it a bonbon, and lets you customize your name on the fly.

## Project Description

Pookie is a little mochi-headed creature wearing a cozy brown hoodie with a two-leaf sprout on top. When the app starts, Pookie hops up to greet you by name in a speech bubble. In idle mode, the head sways gently while the body stays settled. Clicking Pookie makes it close its eyes happily and send a floating heart upward, while clicking the lower-right bonbon button launches a bonbon in an arc toward Pookie's mouth. While eating, the sprout disappears and chewing sound effects play; once Pookie finishes, the sprout pops back with sparkles, a soft glow ring, and a celebratory bounce. You can also click the top-left blue person icon to change the username anytime.

## Challenges & Experience

Aligning Pookie's head with the hoodie while keeping movement natural took some tuning—adjusting `head_bottom_y`, `midbottom`, and keeping the idle head sway subtle made a big difference. Sequencing the bonbon's arc into the eating animation, chewing audio, and sprout comeback effect without overlapping sounds was another fun puzzle to solve. Working through Git commands and keeping the repository clean on GitHub also made wrapping up the project much smoother.

## Demo

Watch the demonstration video here: [Pookie Demonstration](https://github.com/Amani-Bouchnak/Pookie_Creature/issues/1)

## Technologies Used

- **Python** and **Pygame** for the game loop, sprite rendering, animations, UI, and sound playback
- **Git & GitHub** for version control and hosting the repository
- Custom 2D sprite assets (`pookie_body.png`, head states, `bonbon.png`, `heart.png`) and `.wav` sound effects (`bonbonflying.wav`, `sound-effect-of-chewing-food.wav`)

## How to Run

1. Clone the repository and open a terminal in the project folder:
   ```bash
   git clone [https://github.com/Amani-Bouchnak/Pookie_Creature.git](https://github.com/Amani-Bouchnak/Pookie_Creature.git)
   cd Pookie_Creature