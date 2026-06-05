"""Teach Me Mode with SM-2 spaced repetition for Feynman Twin"""
import json
import uuid
import logging
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from config import TEACH_ME_CARDS_FILE, PRIMARY_MODEL, GEMINI_API_KEY

logger = logging.getLogger(__name__)

class SpacedRepetitionEngine:
    """SM-2 algorithm and database manager for quiz cards."""
    
    def __init__(self, file_path: Path = TEACH_ME_CARDS_FILE):
        self.file_path = file_path
        self.data = self._load_data()
        
    def _load_data(self) -> dict:
        if self.file_path.exists():
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading cards file: {e}")
                return self._initialize_data()
        else:
            return self._initialize_data()
            
    def _initialize_data(self) -> dict:
        data = {
            "cards": [],
            "stats": {
                "streak": 0,
                "last_reviewed_date": None,
                "review_dates": []
            }
        }
        self._save_data(data)
        return data
        
    def _save_data(self, data: dict = None):
        if data is None:
            data = self.data
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving cards file: {e}")
            
    def add_card(self, topic: str, question: str, expected_key_points: List[str], source_chunks: Optional[List[str]] = None, created_from: Optional[str] = None) -> dict:
        """Create and add a new card to the database."""
        # Avoid exact duplicate questions
        for c in self.data["cards"]:
            if c["question"].strip().lower() == question.strip().lower():
                logger.info(f"Card already exists for question: {question}")
                return c

        card_id = str(uuid.uuid4())
        card = {
            "id": card_id,
            "topic": topic,
            "question": question,
            "expected_key_points": expected_key_points,
            "source_chunks": source_chunks or [],
            "sm2_data": {
                "easiness_factor": 2.5,
                "interval_days": 1,
                "repetition": 0,
                "next_review": datetime.now().isoformat(),
                "last_reviewed": None
            },
            "created_from": created_from,
            "created_at": datetime.now().isoformat()
        }
        self.data["cards"].append(card)
        self._save_data()
        return card
        
    def get_due_cards(self, limit: int = 5) -> List[dict]:
        """Get due cards for review."""
        now = datetime.now()
        due_cards = []
        for card in self.data["cards"]:
            next_review_str = card.get("sm2_data", {}).get("next_review")
            if not next_review_str:
                due_cards.append(card)
            else:
                try:
                    next_review = datetime.fromisoformat(next_review_str)
                    if next_review <= now:
                        due_cards.append(card)
                except ValueError:
                    due_cards.append(card)
        return due_cards[:limit]

    def remove_card(self, card_id: str) -> bool:
        """Remove a card from the database."""
        initial_len = len(self.data["cards"])
        self.data["cards"] = [c for c in self.data["cards"] if c["id"] != card_id]
        if len(self.data["cards"]) < initial_len:
            self._save_data()
            return True
        return False
        
    def calculate_next_review(self, card_id: str, quality: int) -> dict:
        """Apply the SM-2 algorithm to schedule the card."""
        card = None
        for c in self.data["cards"]:
            if c["id"] == card_id:
                card = c
                break
                
        if not card:
            raise ValueError(f"Card {card_id} not found")
            
        sm2_data = card.setdefault("sm2_data", {
            "easiness_factor": 2.5,
            "interval_days": 1,
            "repetition": 0,
            "next_review": None,
            "last_reviewed": None
        })
        easiness_factor = sm2_data.get("easiness_factor", 2.5)
        repetition = sm2_data.get("repetition", 0)
        interval_days = sm2_data.get("interval_days", 1)
        
        # Update easiness factor
        easiness_factor = easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        if easiness_factor < 1.3:
            easiness_factor = 1.3
            
        # Update repetition and interval
        if quality >= 3:
            if repetition == 0:
                interval_days = 1
            elif repetition == 1:
                interval_days = 6
            else:
                interval_days = int(round(interval_days * easiness_factor))
            repetition += 1
        else:
            repetition = 0
            interval_days = 1
            
        now = datetime.now()
        next_review = (now + timedelta(days=interval_days)).isoformat()
        
        sm2_data.update({
            "easiness_factor": easiness_factor,
            "interval_days": interval_days,
            "repetition": repetition,
            "next_review": next_review,
            "last_reviewed": now.isoformat()
        })
        card["sm2_data"] = sm2_data
        
        self._update_streak()
        self._save_data()
        
        return sm2_data
        
    def _update_streak(self):
        stats = self.data.setdefault("stats", {"streak": 0, "last_reviewed_date": None, "review_dates": []})
        today_str = date.today().isoformat()
        
        if today_str not in stats.setdefault("review_dates", []):
            stats["review_dates"].append(today_str)
            
            # Recompute streak
            dates = sorted([date.fromisoformat(d) for d in stats["review_dates"]])
            if dates:
                streak = 1
                current_date = dates[-1]
                if current_date == date.today() or current_date == date.today() - timedelta(days=1):
                    for i in range(len(dates) - 2, -1, -1):
                        diff = (dates[i+1] - dates[i]).days
                        if diff == 1:
                            streak += 1
                        elif diff > 1:
                            break
                    stats["streak"] = streak
                else:
                    stats["streak"] = 0
            stats["last_reviewed_date"] = datetime.now().isoformat()
            
    def get_stats(self) -> dict:
        cards = self.data["cards"]
        total_cards = len(cards)
        
        mastered_cards = sum(1 for c in cards if c.get("sm2_data", {}).get("repetition", 0) >= 3)
        mastery_percentage = int((mastered_cards / total_cards * 100)) if total_cards > 0 else 0
        
        due_count = len(self.get_due_cards(limit=999999))
        
        stats = self.data.get("stats", {})
        streak = stats.get("streak", 0)
        
        topic_counts = {}
        for c in cards:
            topic = c.get("topic", "general").lower()
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
            
        return {
            "total_cards": total_cards,
            "cards_due": due_count,
            "mastery_percentage": mastery_percentage,
            "streak": streak,
            "topic_breakdown": topic_counts
        }

class TeachMeSession:
    """Manages a single quiz session."""
    
    def __init__(self, engine: SpacedRepetitionEngine):
        self.engine = engine
        self.current_session_cards = []
        self.results = []
        
    def start_session(self, num_questions: int = 5) -> List[dict]:
        """Picks due cards for review. If not enough due, fills with other cards."""
        due_cards = self.engine.get_due_cards(limit=num_questions)
        if len(due_cards) < num_questions:
            all_ids = {c["id"] for c in due_cards}
            other_cards = [c for c in self.engine.data["cards"] if c["id"] not in all_ids]
            due_cards.extend(other_cards[:(num_questions - len(due_cards))])
            
        self.current_session_cards = due_cards
        self.results = []
        return [{
            "id": c["id"],
            "topic": c["topic"],
            "question": c["question"],
            "expected_key_points": c.get("expected_key_points", [])
        } for c in due_cards]
        
    def submit_answer(self, card_id: str, user_answer: str) -> dict:
        """Submit an answer and get Feynman-style feedback & quality score."""
        card = None
        for c in self.engine.data["cards"]:
            if c["id"] == card_id:
                card = c
                break
                
        if not card:
            raise ValueError(f"Card {card_id} not found")
            
        expected_points = card.get("expected_key_points", [])
        
        prompt = f"""You are Richard Feynman. You are evaluating a student's explanation of a physics concept to see how well they understand it.
Topic: {card['topic']}
Question: {card['question']}
Expected Key Points to cover: {", ".join(expected_points)}

Student's Answer: "{user_answer}"

Evaluate their answer based on understanding and clarity. In particular, check which of the expected key points they successfully addressed.
Assign a score from 0 to 5 based on this scale:
- 5: Perfect explanation, uses an excellent analogy, clear and concise, covers all key points.
- 4: Very good explanation, covers most key points with minor omissions.
- 3: Decent explanation, understands the core concept but missed significant key points.
- 2: Poor explanation, has major misconceptions or missed almost all key points.
- 1: Very poor explanation, shows complete lack of understanding or is mostly irrelevant.
- 0: Completely failed to answer or answer is empty.

Provide a feedback message in Feynman's characteristic style. If they missed key points or had misconceptions, explain them simply and encourage them using Socratic prompts or everyday analogies.

Return a JSON object with exactly these keys:
- "score": (integer 0-5)
- "feedback": (Feynman-style explanation and feedback string)
- "key_points_matched": (list of strings indicating which key points they got right)
- "key_points_missed": (list of strings indicating which key points they missed)

Output only valid JSON, do not include any markdown format tags like ```json."""

        try:
            if not GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY not set")
                
            llm = ChatGoogleGenerativeAI(model=PRIMARY_MODEL, google_api_key=GEMINI_API_KEY)
            res = llm.invoke(prompt)
            clean_res = res.content.strip().replace("```json", "").replace("```", "")
            # Sometimes a JSON prefix is present outside ticks
            if clean_res.startswith("json"):
                clean_res = clean_res[4:].strip()
            data = json.loads(clean_res)
            
            score = int(data.get("score", 3))
            feedback = data.get("feedback", "No feedback provided.")
            matched = data.get("key_points_matched", [])
            missed = data.get("key_points_missed", [])
            
        except Exception as e:
            logger.error(f"Error grading answer with LLM: {e}")
            score = 3
            feedback = "I had a bit of trouble grading this. Your explanation seems to touch on the concepts, but make sure to explain it as simply as possible to a child!"
            matched = []
            missed = expected_points
            
        sm2_data = self.engine.calculate_next_review(card_id, score)
        
        result = {
            "card_id": card_id,
            "score": score,
            "feedback": feedback,
            "key_points_matched": matched,
            "key_points_missed": missed,
            "next_review": sm2_data.get("next_review"),
            "correct_answer": " | ".join(expected_points)
        }
        self.results.append(result)
        return result
        
    def get_session_summary(self) -> dict:
        if not self.results:
            return {"score": 0.0, "total": 0, "summary": "No questions answered yet."}
            
        total_score = sum(r["score"] for r in self.results)
        average_score = total_score / len(self.results)
        
        return {
            "score": average_score,
            "total": len(self.results),
            "summary": f"You scored an average of {average_score:.1f}/5 across {len(self.results)} questions."
        }
