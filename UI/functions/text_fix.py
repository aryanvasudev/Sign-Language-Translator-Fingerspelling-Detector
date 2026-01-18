"""
Text Fix Module

This module uses OpenAI's API to correct and format text generated
from ASL fingerspelling recognition. It handles spacing issues,
typos, and converts spaced letters into proper words.
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

# Track if API is available
API_AVAILABLE = False
client = None

if not API_KEY or API_KEY == "your_openai_api_key_here":
    logger.warning("OPENAI_API_KEY not configured. Text correction will be disabled.")
    logger.warning("To enable, add a valid OPENAI_API_KEY to your .env file.")
else:
    # Initialize OpenAI client with new API
    try:
        from openai import OpenAI
        client = OpenAI(api_key=API_KEY)
        API_AVAILABLE = True
        logger.info("OpenAI client initialized successfully")
    except ImportError:
        logger.error("openai package not installed. Install with: pip install openai")
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {e}")

# System prompt for text correction
SYSTEM_PROMPT = """CRITICAL RULE: Return ONLY the corrected sentence. No explanations, no input/output labels.
1. Return ONLY the corrected sentence - no explanations, labels, or quotes
2. NEVER change original words or grammar structures
3. NEVER add, remove, or modify words
4. ONLY fix spelling errors and join spaced letters
5. Add punctuation ONLY when clearly needed
6. Maintain ALL original word forms exactly as given
7. Keep exact same sentence structure
8. Preserve word order exactly as input
9. Keep formal/informal tone as provided
10. No semantic or meaning changes
11. Keep known acronyms exactly as they are (BMW stays BMW)
12. Add period after single words and acronyms
13. NEVER convert acronyms to words
14. Fix common typing errors and misspellings
15. Add appropriate punctuation
16. Convert repeated letters only if they're typos (like 'helllo' to 'hello')
19. Maintain proper sentence case
20. Handle contractions properly (dont -> don't, cant -> can't)

Examples:
Input: D O N O T C R Y N O W
Output: Do Not Cry Now.

Input: I A M G O I N G H O M E
Output: I Am Going Home.

Input: W H E R E A R E Y O U G O I N G
Output: Where Are You Going?

Input: H E L L O W O R L D
Output: Hello World.

Input: T H I S I S A T E S T
Output: This Is A Test.

Input: G O O D M O R N I N G
Output: Good Morning.

Input: S E E Y O U T O M O R R O W
Output: See You Tomorrow.

Input: H A V E A N I C E D A Y
Output: Have A Nice Day.

Input: T H A N K Y O U V E R Y M U C H
Output: Thank You Very Much.

Input: P L E A S E H E L P M E
Output: Please Help Me.

Input: I L O V E P R O G R A M M I N G
Output: I Love Programming.

Input: W E A R E W O R K I N G
Output: We Are Working.

Input: S H E I S D A N C I N G
Output: She Is Dancing.

Input: T H E Y A R E P L A Y I N G
Output: They Are Playing.

Input: H E W A S H E R E
Output: He Was Here.

Input: W E W E R E T H E R E
Output: We Were There.

Input: I T I S R A I N I N G
Output: It Is Raining.

Input: T H E S U N I S S H I N I N G
Output: The Sun Is Shining.

Input: B I R D S A R E F L Y I N G
Output: Birds Are Flying.

Input: W H A T I S Y O U R N A M E
Output: What Is Your Name?

Input: H O W A R E Y O U
Output: How Are You?

Input: N I C E T O M E E T Y O U
Output: Nice To Meet You.

Input: S E E Y O U L A T E R
Output: See You Later.

Input: H A V E F U N
Output: Have Fun.

Input: T A K E C A R E
Output: Take Care.

Input: B E S A F E
Output: Be Safe.

Input: G O O D L U C K
Output: Good Luck.

Input: W E L C O M E B A C K
Output: Welcome Back.

Input: S T A Y H O M E
Output: Stay Home.

Input: B E H A P P Y
Output: Be Happy.

Examples:
Input: M A C H I N E L E A U N I N G
Output: Machine Learning.

Input: C A N Y O U F Y I X T H O E O L D U V A N
Output: Can you fix the old van?

Input: A R T I F I C A L I N T E L I G E N S
Output: Artificial Intelligence.

Input: W H E R E I S S T H E N E W C A R R
Output: Where is the new car?

Input: S O F T W E R E N G I N E R
Output: Software Engineer.

Input: H E L P M E E W I T H T H I S S C O D E
Output: Help me with this code.

Input: D A T A S C I E N S E
Output: Data Science.

Input: T H E Y Y A R E W O R K I N G G H A R D
Output: They are working hard.

Input: C L O U D C O M P U T I G
Output: Cloud Computing.

Input: W H A T T I S S Y O U R N A M E E
Output: What is your name?

Input: F U L L S T A K D E V E L O P E R
Output: Full Stack Developer.

Input: P L E A S E E O P E N T H E D O O R R
Output: Please open the door.

Input: W E B D E V E L O P M E N T T
Output: Web Development.

Input: I L O V E E P R O G R A M M I N G G
Output: I love programming.

Input: D A T A B A S E Q U E R Y Y
Output: Database Query.

Input: D O Y O U U L I K E C O F F E E E
Output: Do you like coffee?

Input: S Y S T E M D E S I G N N
Output: System Design.

Input: L E T S S G O T O T H E P A R K K
Output: Lets go to the park.

Single Word Examples:
Input: D O N E
Output: Done.

Input: H E L L O
Output: Hello.

Input: W O R K
Output: Work.

Input: S L E E P
Output: Sleep.

Input: C O D E
Output: Code.

Acronym Examples:
Input: B M W
Output: BMW.

Input: I B M
Output: IBM.

Input: N A S A
Output: NASA.

Input: F B I
Output: FBI.

Input: C I A
Output: CIA.

Input: N B A
Output: NBA.

Input: U S A
Output: USA.

Input: U K
Output: UK.

Input: U N
Output: UN.

Input: M I T
Output: MIT.

Input: N F L
Output: NFL.

Input: W H O
Output: WHO.

Input: N O S
Output: NOS.

Input: R A M
Output: RAM.

Input: C P U
Output: CPU.

Input: G P U
Output: GPU.

Mixed Examples:
Input: I W O R K A T I B M
Output: I Work At IBM.

Input: M Y B M W I S N E W
Output: My BMW Is New.

Input: T H E C I A A N D F B I
Output: The CIA And FBI.

Input: N A S A A N D I S R O
Output: NASA And ISRO.

Typing Error Examples:
Input: HELLOZ
Output: Hello.

Input: GOODZ
Output: Good.

Input: THANKZ
Output: Thanks.

Input: NICEE
Output: Nice.

Input: GREATT
Output: Great.

Misspelling Examples:
Input: Quewn
Output: Queen.

Input: Programing
Output: Programming.

Input: Enginear
Output: Engineer.

Input: Computar
Output: Computer.

Input: Softwar
Output: Software.

Mixed Error Examples:
Input: TESZT
Output: Test.

Input: CODINGG
Output: Coding.

Input: SLEAPING
Output: Sleeping.

Input: STUDYYING
Output: Studying.

Input: WORKKING
Output: Working.

Sign Language Specific Examples:
Input: S I N G G A G E
Output: Sign Language.

Input: D E F A
Output: Deaf.

Input: H N A D
Output: Hand.

Input: F I N G R E
Output: Finger.

Input: G E S T R U E
Output: Gesture.

Input: S P E L L I G N
Output: Spelling.

Input: C O M M U N I C T E
Output: Communicate.

Input: E X P R E S S N I O
Output: Expression.

Input: V I S U L A
Output: Visual.

Input: M O V E M N E T
Output: Movement.

Input: F E E L I G N
Output: Feeling.

Input: M O R N I M G
Output: Morning.

Input: T H A M K
Output: Thank.

Input: W A T E R N
Output: Water.

Input: P L E A S N E
Output: Please.

Input: H E L L M O
Output: Hello.

Input: G O O D M B Y E
Output: Goodbye.

Input: S I G M N
Output: Sign.

Input: F R I E M N D
Output: Friend.

Input: T E A C H M E R
Output: Teacher.
"""


def generate_sentences(input_text: str) -> str:
    """Generate corrected sentences from spaced letter input.

    Args:
        input_text: Raw text with spaced letters from ASL recognition.

    Returns:
        Corrected and formatted sentence.

    Raises:
        Exception: If OpenAI API call fails.
    """
    if not input_text or not input_text.strip():
        return ""

    # If API is not available, return the raw text with basic formatting
    if not API_AVAILABLE or client is None:
        logger.warning("OpenAI API not available, returning raw text")
        # Basic formatting: capitalize and add period
        formatted = input_text.strip()
        if formatted:
            formatted = formatted[0].upper() + formatted[1:] if len(formatted) > 1 else formatted.upper()
            if not formatted.endswith(('.', '!', '?')):
                formatted += '.'
        return formatted

    try:
        logger.info(f"Processing text: {input_text[:50]}...")

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": input_text
                }
            ],
            temperature=0.0,
            max_tokens=len(input_text.split()) + 50,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )

        result = response.choices[0].message.content
        logger.info(f"Generated result: {result}")
        return result.strip() if result else input_text

    except Exception as e:
        error_msg = str(e)
        logger.error(f"OpenAI API error: {error_msg}")

        # Handle specific error types with user-friendly messages
        if "401" in error_msg or "invalid_api_key" in error_msg.lower():
            logger.error("Invalid OpenAI API key. Please check your .env file.")
            # Return raw text instead of error
            return input_text.strip()
        elif "429" in error_msg or "rate_limit" in error_msg.lower():
            logger.error("OpenAI rate limit exceeded. Please try again later.")
            return input_text.strip()
        elif "insufficient_quota" in error_msg.lower():
            logger.error("OpenAI quota exceeded. Please check your billing.")
            return input_text.strip()

        # For other errors, return raw text
        return input_text.strip()


# Example usage
if __name__ == "__main__":
    test_inputs = [
        "A E L P H E A B E T",
        "H E L L O W O R L D",
        "I L O V E P R O G R A M M I N G"
    ]

    for input_text in test_inputs:
        output = generate_sentences(input_text)
        print(f"Input: {input_text}")
        print(f"Output: {output}")
        print("-" * 40)
