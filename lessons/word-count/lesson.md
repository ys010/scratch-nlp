---
id: word-count
title: "בלש המילים: כמה מילים יש במשפט?"
age_range: 9-11
starter: starter.sb3
estimated_minutes: 40
---

## Overview
This is Mission 1 of the "בלש המילים" (Word Detective) curriculum (see the
project's `index.html` for the full narrative the student has likely already
read: a computer that "reads" a book and writes new sentences on its own).
The student assumes **only basic comfort with Scratch itself** (dragging
blocks, clicking the green flag, finding a category) and **no prior
text-processing concept at all** -- "a sentence is made of characters", "you
can count spaces to count words", and "a loop can look at one letter at a
time" are all new ideas taught here, not assumed. By the end, the student's
project asks for a sentence and correctly says how many words are in it, by
scanning it one character at a time and counting spaces -- the same
technique index.html explains narratively before this lesson hands it to
the tutor to check as the student builds it.

Two Scratch terms the student may not know yet, worth having ready to
explain in your own words (matching index.html's glossary) if they ask:
- **משתנה** (variable) -- a named box that can hold a number or word, and
  can always be opened and changed.
- **לולאה** (loop) -- a block that tells the computer "do this again, and
  again", instead of writing the same block many times.

## Step 1: מקבלים משפט ושומרים אותו
**Goal:** when the green flag is clicked, ask the student for a sentence and store their answer in a variable called `משפט`.
**Tutor opening:** "בואו נתחיל: איך גורמים לתוכנה לשאול אותנו שאלה, ולזכור מה עניתם?" ("Let's start: how do we get the program to ask us a question, and remember what we answered?")
**Success check:** stated against parser output, e.g.
  - sprite has a top-level `event_whenflagclicked` script
  - that script's stack contains `sensing_askandwait`, followed later in the same stack by a `data_setvariableto` block whose `VARIABLE` field is `משפט` and whose `VALUE` input resolves to `sensing_answer` (i.e. the "answer" reporter, not a typed-in literal)
**Hints (escalating):**
  1. "איזו קטגוריית בלוקים חושבים שיודעת 'לשאול' משהו?" (Which block category do you think knows how to "ask" something?)
  2. "חפשו בקטגוריית חיישנים (הצבע התכלת) בלוק ששואל שאלה וממתין לתשובה." (Look in the Sensing category (light blue) for a block that asks a question and waits for an answer.)
  3. "גררו 'כאשר 🏳 נלחץ' מאירועים, מתחתיו 'שאל _ וחכה' מחיישנים, ואז מקטגוריית משתנים גררו את 'קבע _ ל־ _', בחרו בו במשתנה משפט, ובתוך ה־ _ השני גררו את הבלוק 'תשובה' מחיישנים." (Drag "when green flag clicked" from Events, "ask _ and wait" from Sensing under it, then from Variables drag "set _ to _", pick משפט from it, and drag the "answer" block from Sensing into its second slot.)
**Common mistakes:** the student types their own default answer text directly into the `set` block's value slot instead of dragging in the "answer" reporter → the tutor should notice the value is a literal string, not `sensing_answer`, and ask "what happens if you click the flag and type a *different* sentence -- does the program still use what you typed?" rather than naming the fix.

## Step 2: מכינים את המונים
**Goal:** create and initialize two more variables: `מספר_מילים` (word count, starts at 1) and `מקום במשפט` (the scanning position, starts at 1).
**Tutor opening:** "כדי לספור מילים נצטרך שתי תיבות נוספות: אחת שסופרת מילים, ואחת שזוכרת באיזו אות אנחנו מסתכלים עכשיו. אילו שמות הייתם נותנים להן?" (To count words we'll need two more boxes: one that counts words, and one that remembers which letter we're looking at right now. What names would you give them?)
**Success check:**
  - two more `data_setvariableto` blocks appear in the same stack, after the Step 1 blocks: one with `VARIABLE` = `מספר_מילים` and `VALUE` = `1`, one with `VARIABLE` = `מקום במשפט` and `VALUE` = `1`
**Hints (escalating):**
  1. "כמה מילים יש במשפט שאין בו אף רווח? למה כדאי להתחיל לספור מ־1 ולא מ־0?" (How many words are in a sentence with no spaces at all? Why start counting from 1, not 0?)
  2. "צרו שני משתנים חדשים בקטגוריית משתנים, בשם מספר_מילים ובשם מקום במשפט." (Create two new variables in the Variables category, named מספר_מילים and מקום במשפט.)
  3. "הוסיפו עוד שני בלוקי 'קבע _ ל־ _': אחד קובע מספר_מילים = 1, השני קובע מקום במשפט = 1." (Add two more "set _ to _" blocks: one sets מספר_מילים = 1, the other sets מקום במשפט = 1.)
**Common mistakes:** starting both counters at 0 → don't correct directly; ask them to test with a one-word sentence and see what number comes out once the whole project is running (this mistake is easiest to actually see in Step 5, so if they ask now, it's fine to just confirm 1 is a reasonable guess and move on).

## Step 3: בונים לולאה שעוברת על כל אות
**Goal:** wrap a `repeat until` loop around the rest of the script, with a stopping condition that becomes true once the scanning position has passed the end of the sentence.
**Tutor opening:** "עכשיו העין שלנו צריכה לעבור על כל אות במשפט, אחת אחרי השנייה, עד שהיא מגיעה לסוף. איזו לולאה חושבים שמתאימה למשימה כזאת -- אחת שרצה מספר קבוע של פעמים, או אחת שממשיכה עד שתנאי מסוים מתקיים?" (Now our eye needs to go over every letter in the sentence, one after another, until it reaches the end. Which kind of loop fits a job like this -- one that runs a fixed number of times, or one that keeps going until some condition becomes true?)
**Success check:**
  - a `control_repeat_until` block appears after the Step 1-2 blocks
  - its `CONDITION` input contains an `operator_gt` reporter whose two operands are (in either order) a reference to the `מקום במשפט` variable and an `operator_length` reporter over the `משפط` variable
**Hints (escalating):**
  1. "מה ההבדל בין 'חזור 10 פעמים' לבין 'חזור עד ש־'? איזה מהם לא צריך לדעת מראש כמה פעמים לחזור?" (What's the difference between "repeat 10 times" and "repeat until"? Which one doesn't need to know in advance how many times to repeat?)
  2. "גררו 'חזור עד ש־ _' מקטגוריית בקרה, וחברו לתוכו השוואה מ'אופרטורים'." (Drag "repeat until _" from Control, and attach a comparison from Operators inside it.)
  3. "לתוך ההשוואה שימו את המשתנה מקום במשפט בצד אחד, ואת הבלוק 'אורך של _' (גם הוא מאופרטורים, עם משפט בתוכו) בצד השני, כך שהתנאי אומר: מקום במשפט > אורך של משפט." (Into the comparison, put the מקום במשפט variable on one side and the "length of _" block (also from Operators, with משפط inside it) on the other, so the condition reads: מקום במשפט > אורך של משפט.)
**Common mistakes:** **the RTL comparison-block bug.** In a Hebrew Scratch build, the `<`/`>` comparison block can *display* its two sides in a way that doesn't match which value actually ends up in which slot -- so a student can build exactly what the hint says and still get the opposite of what they intended (the loop never runs, or never stops). This is a real bug in Scratch's editor, not a mistake in the student's thinking. If the loop behaves backwards (stops immediately, or never stops / the flag click seems to freeze), don't say "that's wrong" -- say "interesting, let's test it: type a short sentence and see what happens. If it doesn't stop, or stops right away, try dragging the comparison block out on its own for a second, swapping which value is on which side, and putting it back." Never tell them to use `<` instead of `>`, or vice versa, without them testing first -- the correct-looking fix depends on how the bug happened to bite in their specific build.

## Step 4: בודקים אם זו רווח וסופרים מילה
**Goal:** inside the loop, check whether the letter at the current position is a space, and if so, add 1 to the word count.
**Tutor opening:** "אנחנו יודעים שכל פעם שיש רווח, נגמרה עוד מילה. איך אפשר לבדוק, בתוך הלולאה, אם האות שאנחנו מסתכלים עליה עכשיו היא בדיוק רווח?" (We know that every time there's a space, another word has ended. How can we check, inside the loop, whether the letter we're currently looking at is exactly a space?)
**Success check:**
  - inside the `control_repeat_until`'s substack, a `control_if` block appears
  - its `CONDITION` contains an `operator_equals` reporter, one side of which is an `operator_letter_of` reporter (over `מקום במשפט` and `משפט`) and the other side a literal single space character
  - its substack contains a `data_changevariableby` block on `מספר_מילים` with value `1`
**Hints (escalating):**
  1. "יש בלוק שיכול 'להוציא' רק אות אחת ממילה שלמה, לפי מספר מקום. איזו קטגוריה חושבים שמסתירה בלוק כזה?" (There's a block that can "pull out" just one letter from a whole word, by position number. Which category do you think hides a block like that?)
  2. "בקטגוריית אופרטורים יש בלוק 'תו (_) של (_)' -- הוא מחזיר את האות שנמצאת במקום מסוים בתוך מילה." (The Operators category has a "letter (_) of (_)" block -- it returns the letter at a certain position inside a word.)
  3. "בתוך הלולאה גררו 'אם _ אז' מבקרה, ובתוכו השוואה '_ = _': בצד אחד תו (מקום במשפט) של (משפט), ובצד השני רווח בודד (' '). בתוך ה'אם', גררו 'שנה את מספר_מילים ב־ 1' ממשתנים." (Inside the loop, drag "if _ then" from Control, and inside it an equals comparison: on one side letter (מקום במשפט) of (משפט), on the other a single space (" "). Inside the "if", drag "change מספר_מילים by 1" from Variables.)
**Common mistakes:** comparing against an empty string or a different character instead of an actual typed space → ask "try a sentence with two words separated by a space -- does the count come out right?" rather than pointing at the specific block.

## Step 5: מזיזים את העין קדימה ומכריזים את התשובה
**Goal:** inside the loop but after the `if`, move the scanning position forward by 1 every time around (space or not); after the loop ends, say the final word count.
**Tutor opening:** "בכל סיבוב של הלולאה, העין שלנו צריכה לזוז קדימה לאות הבאה -- גם אם הייתה שם רווח וגם אם לא. איפה בלולאה הייתם שמים בלוק כזה?" (On every trip around the loop, our eye needs to move forward to the next letter -- whether or not there was a space there. Where in the loop would you put a block like that?)
**Success check:**
  - inside the `control_repeat_until`'s substack, *after* the `control_if` block (a sibling, not nested inside it), a `data_changevariableby` block on `מקום במשפט` with value `1`
  - after the `control_repeat_until` block (outside the loop entirely), a `looks_say` block whose message includes a reference to the `מספר_מילים` variable
**Hints (escalating):**
  1. "אם הבלוק שמזיז את העין יהיה בתוך ה'אם', מתי הוא ירוץ -- כל סיבוב, או רק כשיש רווח?" (If the block that moves the eye is placed inside the "if", when will it run -- every loop, or only when there's a space?)
  2. "חברו בלוק נוסף מתחת ל'אם', אבל עדיין בתוך הלולאה." (Attach another block below the "if", but still inside the loop.)
  3. "בתוך הלולאה, אחרי ה'אם' (לא בתוכו!), הוסיפו 'שנה את מקום במשפט ב־ 1'. ואחרי סוף הלולאה, מקטגוריית מראה, הוסיפו 'אמור _' עם המשפט 'יש במשפט ' + מספר_מילים + ' מילים' בתוכו." (Inside the loop, after the "if" -- not inside it! -- add "change מקום במשפט by 1". After the loop ends, from Looks, add "say _" with the sentence "יש במשפט " + מספר_מילים + " מילים" built into it.)
**Common mistakes:** the "move the eye forward" block ends up nested inside the `if` instead of after it → the loop never terminates on a sentence with a run of non-space letters in a row (it will look "stuck" -- test by running it, don't just read the blocks). The `say` block ends up *inside* the loop instead of after it → the sprite announces a growing, wrong count on every single letter instead of once at the end.

## Challenge (matches index.html's "עכשיו אתם הבלשים")
Once all 5 steps pass, offer these only if the student wants more (don't push):
- **קל:** what happens with two spaces in a row in the middle of the sentence? Have them predict before running it.
- **לגיבורים:** add a new variable that remembers the longest word seen so far. (Hint: you'll need a variable that collects letters one at a time until a space, and to check its length every time you hit a new space.)
