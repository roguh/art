# Some music made using the Euterpea library for Haskell

Euterpea is a domain specific language in Haskell for writing music.

The following program will play the C4 note for 1 beat (1 quarter note `qn` or `0.25`), and then it'll play the E3 and E4 notes simultaneously for 2 beats (`0.5` or a half note `hn`).

```
play (c 4 qn :+: e 3 0.5)
```

## How to run in Linux

- Install a Haskell compiler
- Install Euterpea
- Install VMPK (Virtual MIDI Piano Keyboard) or another MIDI server
- Run VMPK or your other MIDI server
  - You should see a Keyboard appear
  - You may need to enable the feature so that it opens a MIDI input device
- Run app/Main.markdown
  - This file is a literate Haskell file, you're reading it right now.
  - By default, it'll connect to MIDI output device `2`.

If it doesn't work, try using another MIDI output device, such as device `1`.

### Running with `stack`

If you're using Haskell stack, simply type:

```
stack run
```

## Source code and description

```haskell
import Euterpea
```

This song is played at 64 beats per minute.
`Dur` is Euterpea's type for specifying a rational-valued time duration.

```haskell
bpm :: Dur
bpm = 64
```

The song is in A major.
I think the "base" key is A3, which would be an octave below A4 (440Hz?).
I'm not sure how to change Euterpea to A major, so this `Music` jumps around an octave and doesn't sound right.

```haskell
-- Ignore that this is an unused top-level binding by prefixing the name with an underscore
-- -Wunused-top-binds
_gaga_you_and_i__a_major :: Music Pitch
_gaga_you_and_i__a_major = configure
          $ cs base t
        :+: b base t
        :+: cs base t2
        :+: cs base t2
        :+: cs base t
        :+: b base t
        :+: cs base t3
        :+: rest hn
        :+: d base t
        :+: cs base t
        :+: d base t2
        :+: d base t2
        :+: d base t
        :+: cs base t
        :+: d base t
        :+: cs base t2
        :+: e base t3
        :+: rest hn
        :+: a (1 + base) t2
        :+: fs base t2
        :+: e base t2
        :+: fs base t2
        :+: a (1 + base) t
        :+: fs base t2
        :+: e base t2
        :+: a base t2
        :+: cs base t3
          where t = qn
                t2 = hn
                t3 = dhn
                base = 3
```

I rewrote the song in C major, and Euterpea plays it correctly.

```haskell
gaga_you_and_i :: Music Pitch
gaga_you_and_i = configure 
          -- It's been a long time since you've came around
          $ c base t
        :+: d base t
        :+: e base t2
        :+: e base t2
        :+: e base t
        :+: d base t
        :+: e base t2
        :+: e base t
        :+: e base t3
        :+: rest hn
        :+: c base t
        :+: e base t
        :+: f base t2
        :+: f base t2
        :+: f base t
        :+: e base t
        :+: f base t
        :+: e base t2
        :+: g base t3
        :+: rest hn
        :+: c (1 + base) t2
        :+: a base t2
        :+: g base t2
        :+: a base t2
        :+: c (1 + base) t
        :+: a base t2
        :+: g base t2
        :+: c base t2
        :+: e base t3
          where t = qn
                t2 = hn
                t3 = dhn
                base = 4
```

This function will set the MIDI musical instrument and the tempo.

```haskell
configure :: Music a -> Music a
configure = instrument AcousticGrandPiano . tempo desiredTempo
```

The MIDI tempo is the amount of microseconds per quarter note.
This song is in BPM (e.g. 64 beats per minute).
A quarter note is 1 beat.
So there are 64 beats (quarter notes) in 60 seconds.
There are 64 / 60 microseconds per beat.

Unfortunately, this doesn't sound right so I double the tempo `(2 * bpm)`...

```haskell
  where desiredTempo = 2 * bpm / 60
```


Change the MIDI device if this causes you trouble...

```haskell
midiDevice :: Int
midiDevice = 2
```

The entrypoint will print the song's duration and play the song.

```haskell
main :: IO ()
main = do
  print duration
  print $ (fromRational duration :: Double)
  playDev midiDevice $ song
  where
    duration = dur song
    song = gaga_you_and_i
```

## VIM support

Install the [`haskell-vim`](https://github.com/neovimhaskell/haskell-vim) plugin for good syntax highlighting and other features.

You might need this:

```
set ft=markdown
```
