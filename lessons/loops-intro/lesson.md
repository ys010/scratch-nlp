---
id: loops-intro
title: Intro to loops
age_range: 8-12
starter: starter.sb3
estimated_minutes: 20
---

## Overview
The student makes a sprite move, then learns that a `repeat` block can do
the same thing over and over without stacking up copies of the same block,
and finally adds a turn inside the repeat so the sprite draws a shape
(a rough square or star) instead of a straight line. This is the core idea
behind loops: doing something more than once without repeating yourself.

## Step 1: Make it move
**Goal:** make the sprite move when the green flag is clicked.
**Tutor opening:** "Can you make your character move when we click the green flag?"
**Success check:** stated against parser output, e.g.
  - sprite has a top-level `event_whenflagclicked` script
  - that script's stack contains a `motion_movesteps` block
**Hints (escalating):**
  1. "What category of blocks do you think makes something move?"
  2. "Look in the Motion category (the blue blocks)."
  3. "Drag 'when green flag clicked' from Events, then attach 'move 10 steps' from Motion right underneath it."
**Common mistakes:** the student clicks the `move` block directly to test it, with no hat block attached → the tutor should ask them to click the green flag itself, since that's how every later step will be checked too.

## Step 2: Do it again, and again
**Goal:** replace (or wrap) the single move with a `repeat` block, so the sprite keeps moving.
**Tutor opening:** "What if you wanted it to take a bunch of little steps forward? Is there a faster way than gluing a lot of move blocks together?"
**Success check:**
  - sprite has a `control_repeat` block
  - that `control_repeat`'s substack contains a `motion_movesteps` block (containment, not just presence -- a repeat block sitting next to an unrelated move block does not count)
**Hints (escalating):**
  1. "Is there a block that says 'do this again and again' instead of just once?"
  2. "Check the Control category (the yellow blocks)."
  3. "Drag 'repeat (10)' from Control, then drag your 'move' block so it snaps inside the repeat's mouth."
**Common mistakes:** the `repeat` block is attached to the script but the `move` block sits after it rather than inside it → ask "Try running it -- does it look like it's repeating, or does it only move once?" rather than naming the fix.

## Step 3: Turn it into a shape
**Goal:** add a turn block inside the same repeat, so the sprite draws a shape instead of a straight line.
**Tutor opening:** "Right now it repeats moving in a straight line. What do you think would happen if it also turned a little bit each time?"
**Success check:**
  - the same `control_repeat`'s substack contains both a `motion_movesteps` block and a `motion_turnright` or `motion_turnleft` block
**Hints (escalating):**
  1. "What block might change which way the sprite is facing?"
  2. "Look for a turning block in the Motion category."
  3. "Drag 'turn right 15 degrees' into the repeat, right after the move block."
**Common mistakes:** the turn block is placed after the repeat instead of inside it (sprite turns once, then repeats a straight line) → ask "Try clicking the flag a few times -- does it turn every time around, or just once at the end?"
