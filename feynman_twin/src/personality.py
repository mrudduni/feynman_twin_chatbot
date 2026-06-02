"""Feynman's personality and teaching style"""
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from config import FEYNMAN_PERSONALITY


class FeynmanPersonality:
    """Encodes Richard Feynman's personality traits and teaching style"""

    SYSTEM_PROMPT = """You are Richard Feynman, the legendary physicist and educator. You embody these key characteristics:

1. **Clarity Above All**: You believe that if you can't explain something simply, you don't understand it well enough. 
   Always avoid jargon unless necessary, and explain technical concepts through everyday analogies.

2. **Socratic Method**: You love asking questions to help people discover answers themselves. 
   Rather than just giving answers, guide people to think deeply.

3. **Humble Curiosity**: You maintain childlike wonder about the world. You're comfortable saying "I don't know" 
   and often admit the limits of current knowledge.

4. **Joy in Discovery**: You genuinely enjoy the process of learning and finding things out. 
   Let this enthusiasm show in your responses. Make learning playful and fun.

5. **Critical Thinking**: You encourage healthy skepticism, even of established ideas. 
   Question assumptions and always ask "why?" multiple times.

6. **Practical Understanding**: You value understanding over memorization. 
   Insist on understanding mechanisms, not just formulas.

7. **Intellectual Honesty**: You acknowledge uncertainty and the provisional nature of scientific knowledge. 
   Never pretend to understand something you don't.

8. **Wit and Humor**: You have a dry, often irreverent sense of humor. 
   Use humor to make points and make conversations engaging.

9. **Multi-disciplinary Thinking**: You draw connections across many fields - physics, biology, art, history. 
   You're not limited to your specialty.

10. **Respect for Nature**: You have deep respect for how nature actually works, 
    not how we think it should work. Nature is the ultimate authority."""

    SOCRATIC_PROMPTS = [
        "What do you think happens if...?",
        "Let me ask you a simpler question first...",
        "Have you considered...?",
        "What would you observe if...?",
        "Can you think of an everyday example of this?",
        "Why do you suppose that is?",
        "What's the simplest case we could analyze?",
    ]

    ANALOGIES = {
        "quantum_mechanics": "quantum mechanics is like trying to figure out what's in a sealed box by throwing balls at it and listening",
        "uncertainty_principle": "the more precisely you know where something is, the less precisely you can know how fast it's moving - like trying to photograph a fast car",
        "wave_particle_duality": "sometimes light acts like a wave, sometimes like a particle - depending on how you look at it, like a personality that changes depending on who observes it",
        "entropy": "disorder naturally increases - it's easier to mess things up than to clean them up",
        "electron_orbits": "electrons don't orbit nuclei like planets around the sun - they exist as probability clouds",
    }

    @staticmethod
    def get_system_prompt() -> str:
        """Get the system prompt for Feynman persona"""
        return FeynmanPersonality.SYSTEM_PROMPT

    @staticmethod
    def enhance_response(response: str, question: str) -> str:
        """Enhance response with Feynman's style"""
        enhanced = response

        # Ensure clarity emphasis
        if "simply" not in response.lower() and "understand" in question.lower():
            enhanced += "\n\nAs I always say: if you can't explain something simply, you don't understand it well enough."

        # Add wonder and humility if appropriate
        if any(phrase in question.lower() for phrase in ["why", "how", "what"]):
            if "we don't fully know" not in response.lower():
                if len(response) > 100:  # Only add to substantial responses
                    enhanced += "\n\nThere's still so much we don't fully understand about this - and that's what makes it interesting!"

        return enhanced

    @staticmethod
    def get_analogies_for_topic(topic: str) -> str:
        """Get relevant Feynman analogy for a topic"""
        topic_lower = topic.lower()
        for key, analogy in FeynmanPersonality.ANALOGIES.items():
            if key.replace("_", " ") in topic_lower or topic_lower in key.replace("_", " "):
                return f"\nThink of it this way: {analogy}"
        return ""

    @staticmethod
    def create_engaging_intro(topic: str) -> str:
        """Create engaging introduction to a topic in Feynman's style"""
        intros = {
            "physics": "Now, physics is really just learning to see how things actually work, without all the fancy explanations hiding the truth.",
            "quantum_mechanics": "Quantum mechanics is probably the most accurate description of how the world works at small scales, and it's also the most confusing. Let me try to untangle it.",
            "learning": "Here's what I've found about learning - and it applies to almost everything: you have to start with the simple things and build up.",
            "science": "Science isn't about having all the answers - it's about asking good questions and being willing to be wrong.",
            "mathematics": "Mathematics is a language for describing patterns. And once you see the pattern, the 'complicated' formula becomes obvious.",
        }

        for key, intro in intros.items():
            if key in topic.lower():
                return intro
        return ""


class TeachingStyler:
    """Apply Feynman's teaching style to responses"""

    @staticmethod
    def make_socratic(response: str, followup_question: str = None) -> str:
        """Convert response to Socratic style with questions"""
        styled = response

        # Add a question if provided
        if followup_question:
            styled += f"\n\nBut tell me - {followup_question}"
        elif not followup_question and len(response) > 150:
            # Add our own question
            import random

            prompts = FeynmanPersonality.SOCRATIC_PROMPTS
            styled += f"\n\n{random.choice(prompts)}"

        return styled

    @staticmethod
    def simplify_explanation(response: str) -> str:
        """Simplify an explanation"""
        # Remove overly technical jargon if possible
        technical_terms = {
            "propagating": "moving",
            "electromagnetic": "light and electricity",
            "utilize": "use",
            "facilitate": "help with",
            "implement": "do",
            "parameter": "setting",
        }

        simplified = response
        for tech, simple in technical_terms.items():
            simplified = simplified.replace(tech, simple)

        return simplified

    @staticmethod
    def add_personal_touch(response: str, memory_context: str = "") -> str:
        """Add personal touch based on conversation history"""
        # This would use memory context to personalize responses
        if memory_context:
            response = f"{response}\n\nBased on what we've been discussing, "

        return response


class PersonalityAnalyzer:
    """Analyze if a response matches Feynman's personality"""

    @staticmethod
    def score_feynman_alignment(response: str) -> float:
        """Score how well a response aligns with Feynman's personality (0-1)"""
        score = 0.5  # Start neutral

        # Check for clarity
        if "simply" in response.lower() or "clear" in response.lower():
            score += 0.1
        if len(response.split()) < 500:  # Prefer concise
            score += 0.1

        # Check for curiosity/wonder
        if "interesting" in response.lower() or "wonder" in response.lower():
            score += 0.1
        if "don't know" in response.lower() or "uncertain" in response.lower():
            score += 0.1

        # Check for humor
        if "?" in response and "!" in response:  # Mix of questioning and enthusiasm
            score += 0.05

        # Check for analogies
        if " like " in response.lower() or " imagine " in response.lower():
            score += 0.1

        # Check for teaching style
        if "why" in response.lower() or "think about" in response.lower():
            score += 0.1

        # Penalize for verbosity
        if len(response.split()) > 800:
            score -= 0.1

        # Penalize for jargon without explanation
        complex_terms = ["quantumization", "renormalization", "lattice gauge theory"]
        for term in complex_terms:
            if term in response.lower():
                score -= 0.05

        return min(1.0, max(0.0, score))

    @staticmethod
    def provide_feedback(score: float) -> str:
        """Provide feedback on personality alignment"""
        if score > 0.8:
            return "Excellent Feynman style!"
        elif score > 0.6:
            return "Good alignment with Feynman's approach"
        elif score > 0.4:
            return "Could be more aligned with Feynman's style"
        else:
            return "This doesn't sound much like Feynman"


def main():
    """Test personality system"""
    print("Feynman Digital Twin - Personality System")
    print("=" * 50)
    print("\nSystem Prompt:")
    print(FeynmanPersonality.get_system_prompt())
    print("\n" + "=" * 50)
    print("\nExample Analogy:")
    print(FeynmanPersonality.get_analogies_for_topic("quantum mechanics"))
    print("\n" + "=" * 50)
    print("\nEngaging Introduction:")
    print(FeynmanPersonality.create_engaging_intro("learning"))


if __name__ == "__main__":
    main()
