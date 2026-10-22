#!/bin/bash
# Final renders: main camera + 4 alternate views, then bloom post.
cd "$(dirname "$0")/.."
blender -b -P scene/build.py -- --out out/final/raw_main.png --pct 100 --samples 384 --cam main 2>&1 | grep -E "RENDERED|Error"
python3 scene/post.py out/final/raw_main.png out/final/01_ana_gorunum.png
i=2
for c in back desk sofa top; do
  blender -b -P scene/build.py -- --out out/final/raw_$c.png --pct 100 --samples 256 --cam $c 2>&1 | grep -E "RENDERED|Error"
  if [ $c = top ]; then cp out/final/raw_$c.png out/final/0${i}_$c.png; else python3 scene/post.py out/final/raw_$c.png out/final/0${i}_$c.png 0.3; fi
  i=$((i+1))
done
echo ALLDONE
