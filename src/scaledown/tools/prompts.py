######################################
# Expert Persona
######################################

EXPERT_PERSONA_PROMPT = """ROLE: You are a domain expert with deep knowledge in the relevant field. Draw upon your expertise to provide the most accurate and comprehensive response possible."""

######################################
# Uncertainty Quantification
######################################

UNCERTAINTY_PROMPT = """CONFIDENCE ASSESSMENT: After providing your answer, explicitly state your confidence level as a percentage (0-100%). If your confidence is below 90%, clearly indicate which parts you are uncertain about."""


######################################
# Zeroshot Chain-of-Thought
######################################

COT_PROMPT = """REASONING PROCESS: Explicitly show your step-by-step reasoning process. Work through the problem methodically, showing each logical step."""

######################################
# Zeroshot Chain-of-Verification
######################################

COVE_PROMPT = """VERIFICATION PROCEDURE: Use the following verification approach:
1. INITIAL ANSWER: Provide your initial answer to the question
2. VERIFICATION QUESTIONS: Generate 3-5 specific verification questions to check your initial answer
3. VERIFICATION RESPONSES: Answer each verification question thoroughly
4. FINAL VERIFIED ANSWER: Based on the verification, provide your refined final answer in the final answer section

IMPORTANT: Even if the task asks for a specific format (like numbered lists), you must still show the complete verification process first, then provide the final answer in the requested format."""


######################################
# Task Final Answer Format
######################################



######################################
# WIKIDATA COMPONENTS
######################################

WIKIDATA_TASK_PROMPT = """Answer the below question which is asking for a list of persons. """

WIKIDATA_FINAL_ANSWER_FORMAT = """
FINAL ANSWER FORMAT: Regardless of your reasoning processes or methodology, after all intermediate steps, you MUST end your response with a clearly delimited final answer section:

=== FINAL ANSWER ===
[Provide your final answer here as a numbered list with exactly the format shown below]

1. [Entity Name Only]
2. [Entity Name Only]
3. [Entity Name Only]
...
[Maximum 10 entities, no additional details, no explanations]
=== END FINAL ANSWER ===
"""

WIKIDATA_EXAMPLES_PROMPT = """
EXAMPLEs: Here is some examples of the question and the output you should return.

Example Question: Who are some movie actors who were born in Boston?
Example Output: 
[Some intermediate answer if requested]
=== FINAL ANSWER ===
1. Donnie Wahlberg
2. Chris Evans
3. Mark Wahlberg
4. Ben Affleck
5. Uma Thurman
=== END FINAL ANSWER ===

Example Question: Who are some football players who were born in Madrid?
Example Output: 
[Some intermediate answer if requested]
=== FINAL ANSWER ===
1. Sergio Ramos
2. Marcos Alonso
3. David De Gea
4. Fernando Torres
=== END FINAL ANSWER ===

Example Question: Who are some politicians who were born in Washington?
Example Output: 
[Some intermediate reasoning if requested]
=== FINAL ANSWER ===
1. Barack Obama
2. Bill Clinton
3. Bil Sheffield
4. George Washington
=== END FINAL ANSWER ===
"""


WIKIDATA_QUESTION_PROMPT = """
Now here is the actual question:
Question: {question}"""



######################################
# WIKIDATA CATEGORY
######################################

BASELINE_PROMPT_WIKI_CATEGORY = """Answer the below question which is asking for a list of entities (names, places, locations etc). Output should be a numbered list and only contains the relevant & concise enitites as answer. NO ADDITIONAL DETAILS.

Example Question: Name some movies directed by Steven Spielberg.
Example Answer: 1. Jaws
2. Jurassic Park
3. Indiana Jones
4. E.T.
5. TENET

Example Question: Name some football stadiums from the Premier League.
Example Answer: 1. Old Trafford
2. Anfield
3. Stamford Bridge
4. Santiago Bernabeu

Question: {question}
"""


######################################
# MULTISPAN QA
######################################

BASELINE_PROMPT_MULTI_QA = """Answer the below question correctly and in a concise manner without much details. Only answer what the question is asked. NO ADDITIONAL DETAILS.

Question: {question}
"""

######################################
# SIMPLEQA COMPONENTS
######################################

SIMPLEQA_TASK_PROMPT = """Answer the below factual question with a single, precise answer. Provide only the specific information requested."""

SIMPLEQA_FINAL_ANSWER_FORMAT = """
FINAL ANSWER FORMAT: Regardless of your reasoning processes or methodology, after all intermediate steps, you MUST end your response with a clearly delimited final answer section:

=== FINAL ANSWER ===
[Provide your single, precise answer here - no additional details or explanations]
=== END FINAL ANSWER ===
"""

SIMPLEQA_EXAMPLES_PROMPT = """
EXAMPLES: Here are some examples of the question and output format you should follow.

Example Question: Who received the IEEE Frank Rosenblatt Award in 2010?
Example Output: 
[Some intermediate reasoning if requested]
=== FINAL ANSWER ===
Michio Sugeno
=== END FINAL ANSWER ===

Example Question: What's the name of the women's liberal arts college in Cambridge, Massachusetts?
Example Output: 
[Some intermediate reasoning if requested]
=== FINAL ANSWER ===
Radcliffe College
=== END FINAL ANSWER ===

Example Question: How much money, in euros, was the surgeon held responsible for Stella Obasanjo's death ordered to pay her son?
Example Output: 
[Some intermediate reasoning if requested]
=== FINAL ANSWER ===
120,000
=== END FINAL ANSWER ===
"""

SIMPLEQA_QUESTION_PROMPT = """
Now here is the actual question:
Question: {question}"""