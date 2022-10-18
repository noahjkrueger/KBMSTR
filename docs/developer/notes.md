https://www.gutenberg.org/

https://stackoverflow.com/questions/31552716/multiprocessing-queue-full

## Assumptions
- 10 finger typing, thumbs on keyboard, each finger is responsible for a set of keys

![finger responsibility](fingers.png)

- Fingers start in positions 10, 11, 12, 13, 16, 17, 18, 19
- When a finger moves, it remains in that position until needed again
  + This may not be accurate to real world typing
- distances on keys are defined as and every pair is reflexive (i.e distances (x,y) = (y, x)):
  + Moving finger horizontally one key (ex. 13->14) has a distance of 1.0
