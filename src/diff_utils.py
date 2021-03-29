"""
More information about the underling diff library can be found here:
https://pypi.org/project/diff-match-patch/

The source code for the diff library is here:
https://github.com/google/diff-match-patch

These utility functions are simply wrappers around the diff library to server our purposes from the client as simply as possible.

Here is the output of the demo function:

Output:
@@ -0,0 +1,12 @@
+hellojupiter

@@ -2,11 +2,9 @@
 ello
-jupiter
+pluto

hellojupiter
hellopluto
"""

from diff_match_patch import diff_match_patch

def demo():
  text0 = ""
  text1 = "hellojupiter"
  text2 = "hellopluto"

  diff1 = create_diff(text0, text1)
  diff2 = create_diff(text1, text2)

  text1_generated = generate_text(diff1, text0)
  text2_generated = generate_text(diff2, text1)

  print(diff1)
  print(diff2)
  print(text1_generated)
  print(text2_generated)

def create_diff(originalStr, newStr) -> str:
  # Convert surrogate pairs into single unicode points
  originalStr = originalStr.encode('utf-16', 'surrogatepass').decode('utf-16')
  newStr = newStr.encode('utf-16', 'surrogatepass').decode('utf-16')

  dmp = diff_match_patch()
  patches = dmp.patch_make(originalStr, newStr)
  diff = dmp.patch_toText(patches)
  return diff

def generate_text(diff, baseText) -> str:
  # Convert surrogate pairs into single unicode points
  baseText = baseText.encode('utf-16', 'surrogatepass').decode('utf-16')

  dmp = diff_match_patch()
  patches = dmp.patch_fromText(diff)
  text_generated, _ = dmp.patch_apply(patches, baseText)
  return text_generated