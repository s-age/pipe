def save_memory(
    fact: str,
) -> dict:
  """
  Saves a specific piece of information or fact to your long-term memory.

  Use this tool:

  - When the user explicitly asks you to remember something (e.g., "Remember that I like pineapple on pizza", "Please save this: my cat's name is Whiskers").
  - When the user states a clear, concise fact about themselves, their preferences, or their environment that seems important for you to retain for future interactions to provide a more personalized and effective assistance.

  Do NOT use this tool:

  - To remember conversational context that is only relevant for the current session.
  - To save long, complex, or rambling pieces of text. The fact should be relatively short and to the point.
  - If you are unsure whether the information is a fact worth remembering long-term. If in doubt, you can ask the user, "Should I remember that for you?"

  ## Parameters

  - `fact` (string, required): The specific fact or piece of information to remember. This should be a clear, self-contained statement. For example, if the user says "My favorite color is blue", the fact would be "My favorite color is blue".


  Args:
    fact: The specific fact or piece of information to remember. Should be a clear, self-contained statement.
  """
  # This function is a stub for actual memory saving operations.
  # Actual memory saving operations must be implemented in the environment that calls this function.

  return {"save_memory_response": {"output": f"Fact saved: {fact} (stub)"}}
