"""
Demo script showing how to use Feynman Digital Twin programmatically
"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from main import FeynmanTwin
from personality import FeynmanPersonality, PersonalityAnalyzer


def demo_basic_query():
    """Demo: Basic question answering"""
    print("\n" + "=" * 70)
    print("DEMO 1: Basic Question Answering")
    print("=" * 70)

    twin = FeynmanTwin()

    questions = [
        "What is the Feynman Technique?",
        "Explain quantum entanglement simply",
        "Why is understanding more important than memorization?",
    ]

    for i, question in enumerate(questions, 1):
        print(f"\n[{i}] Question: {question}")
        print("-" * 50)

        try:
            response, metadata = twin.answer_question(question)
            print(f"Response: {response[:200]}..." if len(response) > 200 else f"Response: {response}")
            print(f"Personality alignment: {metadata['personality_score']:.0%}")
            print(f"Retrieved documents: {metadata['retrieved_docs']}")
        except Exception as e:
            print(f"Error: {e}")


def demo_memory_system():
    """Demo: Memory capabilities"""
    print("\n" + "=" * 70)
    print("DEMO 2: Memory Systems")
    print("=" * 70)

    from memory_system import MemoryManager

    memory = MemoryManager()

    # Add some interactions
    print("\nRecording interactions...")
    memory.record_interaction(
        "What is quantum mechanics?",
        "Quantum mechanics is the study of how the world works at very small scales."
    )
    memory.record_interaction(
        "How do atoms work?",
        "Atoms are composed of electrons, protons, and neutrons..."
    )

    # Store insights
    memory.persistent_memory.add_insight("User is interested in quantum mechanics")
    memory.persistent_memory.add_learned_fact("Quantum mechanics is probabilistic, not deterministic")

    print("\nPersistent Memory Summary:")
    print(memory.persistent_memory.get_memory_summary())

    print("\nSession Summary:")
    print(memory.session_memory.get_conversation_summary())


def demo_personality_analysis():
    """Demo: Personality alignment scoring"""
    print("\n" + "=" * 70)
    print("DEMO 3: Personality Analysis")
    print("=" * 70)

    test_responses = [
        "The electron has a negative charge and orbits the nucleus like a planet around the sun.",
        "Think about this like if you're trying to photograph a fast car - the faster it goes, the blurrier it gets. Similarly, the more precisely you know where an electron is, the less you can know about its momentum.",
        "Quantum superposition is when a particle exists in multiple states simultaneously until measured.",
        "You know, the more I think about it, the more fascinating this becomes. Imagine not knowing whether something is in two places at once until you actually look!",
    ]

    print("\nAnalyzing response quality and Feynman alignment:\n")

    for i, response in enumerate(test_responses, 1):
        score = PersonalityAnalyzer.score_feynman_alignment(response)
        feedback = PersonalityAnalyzer.provide_feedback(score)

        print(f"Response {i}:")
        print(f"  Text: {response[:60]}...")
        print(f"  Score: {score:.0%}")
        print(f"  Feedback: {feedback}\n")


def demo_teaching_style():
    """Demo: Teaching style enhancement"""
    print("\n" + "=" * 70)
    print("DEMO 4: Teaching Style")
    print("=" * 70)

    from personality import TeachingStyler

    original = "Photons are particles of light that travel at the speed of light in a vacuum."

    print(f"Original response:\n{original}\n")

    enhanced = TeachingStyler.make_socratic(original)
    print(f"Enhanced with Socratic method:\n{enhanced}\n")

    simplified = TeachingStyler.simplify_explanation(original)
    print(f"Simplified:\n{simplified}\n")


def demo_personality_traits():
    """Demo: Feynman personality traits"""
    print("\n" + "=" * 70)
    print("DEMO 5: Feynman's Personality Traits")
    print("=" * 70)

    print("\nFeynman's System Prompt:")
    print("-" * 70)
    print(FeynmanPersonality.get_system_prompt()[:500] + "...")

    print("\n\nFeynman's Teaching Philosophy Intro:")
    intro = FeynmanPersonality.create_engaging_intro("learning")
    print(f"'{intro}'")

    print("\n\nRelevant Analogy for Quantum Mechanics:")
    analogy = FeynmanPersonality.get_analogies_for_topic("quantum mechanics")
    print(f"'{analogy}'")


def demo_batch_processing():
    """Demo: Batch processing multiple questions"""
    print("\n" + "=" * 70)
    print("DEMO 6: Batch Processing")
    print("=" * 70)

    twin = FeynmanTwin()

    questions = [
        "What makes a good scientist?",
        "How do you approach learning a new subject?",
        "Why is curiosity important?",
    ]

    print(f"\nProcessing {len(questions)} questions in batch...\n")

    try:
        results = twin.batch_query(questions)

        for i, result in enumerate(results, 1):
            print(f"{i}. Q: {result['question']}")
            print(f"   Response: {result['response'][:100]}...")
            print(f"   Score: {result['metadata']['personality_score']:.0%}\n")
    except Exception as e:
        print(f"Error in batch processing: {e}")


def main():
    """Run all demos"""
    import argparse

    parser = argparse.ArgumentParser(description="Feynman Twin Demo")
    parser.add_argument(
        "--demo",
        type=int,
        choices=[1, 2, 3, 4, 5, 6],
        help="Run specific demo (1-6)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all demos",
    )

    args = parser.parse_args()

    if args.all or not args.demo:
        try:
            demo_personality_traits()
            demo_personality_analysis()
            demo_teaching_style()
            demo_memory_system()
            # demo_basic_query()  # Requires RAG setup and API key
            # demo_batch_processing()  # Requires RAG setup and API key
        except Exception as e:
            print(f"Error running demos: {e}")
            print("\nNote: Some demos require RAG setup and Gemini API key")
    else:
        demo_funcs = {
            1: demo_basic_query,
            2: demo_memory_system,
            3: demo_personality_analysis,
            4: demo_teaching_style,
            5: demo_personality_traits,
            6: demo_batch_processing,
        }
        try:
            demo_funcs[args.demo]()
        except Exception as e:
            print(f"Error: {e}")

    print("\n" + "=" * 70)
    print("Demos complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
