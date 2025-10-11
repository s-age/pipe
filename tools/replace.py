def replace(
    file_path: str,
    instruction: str,
    old_string: str,
    new_string: str,
) -> dict:
  """Replaces text within a file. Replaces a single occurrence. This tool requires providing significant context around the change to ensure precise targeting. Always use the read_file tool to examine the file's current content before attempting a text replacement.
      
      The user has the ability to modify the `new_string` content. If modified, this will be stated in the response.
      
      Expectation for required parameters:
      1. `file_path` MUST be an absolute path; otherwise an error will be thrown.
      2. `old_string` MUST be the exact literal text to replace (including all whitespace, indentation, newlines, and surrounding code etc.).
      3. `new_string` MUST be the exact literal text to replace `old_string` with (also including all whitespace, indentation, newlines, and surrounding code etc.). Ensure the resulting code is correct and idiomatic and that `old_string` and `new_string` are different.
      4. `instruction` is the detailed instruction of what needs to be changed. It is important to Make it specific and detailed so developers or large language models can understand what needs to be changed and perform the changes on their own if necessary. 
      5. NEVER escape `old_string` or `new_string`, that would break the exact literal text requirement.
      **Important:** If ANY of the above are not satisfied, the tool will fail. CRITICAL for `old_string`: Must uniquely identify the single instance to change. Include at least 3 lines of context BEFORE and AFTER the target text, matching whitespace and indentation precisely. If this string matches multiple locations, or does not match exactly, the tool will fail.
      6. Prefer to break down complex and long changes into multiple smaller atomic calls to this tool. Always check the content of the file after changes or not finding a string to match.
      **Multiple replacements:** If there are multiple and ambiguous occurences of the `old_string` in the file, the tool will also fail.

  Args:
    file_path: The absolute path to the file to modify. Must start with '/'.
    instruction: A clear, semantic instruction for the code change, acting as a high-quality prompt for an expert LLM assistant. It must be self-contained and explain the goal of the change.

      A good instruction should concisely answer:
      1.  WHY is the change needed? (e.g., "To fix a bug where users can be null...")
      2.  WHERE should the change happen? (e.g., "...in the 'renderUserProfile' function...")
      3.  WHAT is the high-level change? (e.g., "...add a null check for the 'user' object...")
      4.  WHAT is the desired outcome? (e.g., "...so that it displays a loading spinner instead of crashing.")

      **GOOD Example:** "In the 'calculateTotal' function, correct the sales tax calculation by updating the 'taxRate' constant from 0.05 to 0.075 to reflect the new regional tax laws."

      **BAD Examples:**
      - "Change the text." (Too vague)
      - "Fix the bug." (Doesn't explain the bug or the fix)
      - "Replace the line with this new line." (Brittle, just repeats the other parameters)

    old_string: The exact literal text to replace, preferably unescaped. Include at least 3 lines of context BEFORE and AFTER the target text, matching whitespace and indentation precisely. If this string is not the exact literal text (i.e. you escaped it) or does not match exactly, the tool will fail.
    new_string: The exact literal text to replace `old_string` with, preferably unescaped. Provide the EXACT text. Ensure the resulting code is correct and idiomatic.
  """
  # This function is a stub for actual file system operations.
  # Actual file system operations must be implemented in the environment that calls this function.

  return {"replace_response": {"output": f"Replacing text in {file_path} (stub)"}}
