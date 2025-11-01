import re
from typing import List, Set
from difflib import SequenceMatcher

class ArgumentValidator:
    """Validates debate arguments for quality and novelty"""
    
    def __init__(self, min_length: int = 10, max_similarity: float = 0.7, min_words: int = 5):
        self.min_length = min_length
        self.max_similarity = max_similarity
        self.min_words = min_words  # Added for compatibility
    
    def is_valid_argument(self, argument: str, used_arguments: List[str]) -> bool:
        """Check if argument meets quality standards"""
        return (
            self.has_minimum_length(argument) and
            self.has_substance(argument) and 
            self.is_novel(argument, used_arguments) and
            self.is_relevant(argument) and
            not self._is_placeholder(argument)  # Added check
        )
    
    def has_minimum_length(self, argument: str) -> bool:
        """Check if argument meets minimum length requirement"""
        if not argument or not isinstance(argument, str):
            return False
        words = argument.split()
        return len(words) >= self.min_length and len(argument.strip()) >= 20
    
    def has_substance(self, argument: str) -> bool:
        """Check if argument has substantive content"""
        # Remove common filler phrases
        filler_phrases = [
            "i think", "i believe", "in my opinion", "it seems to me",
            "let me say", "as we know", "generally speaking"
        ]
        
        clean_argument = argument.lower()
        for phrase in filler_phrases:
            clean_argument = clean_argument.replace(phrase, "")
        
        # Check if substantial content remains
        words = clean_argument.split()
        unique_words = set(words)
        return len(unique_words) >= 5 and len(words) >= 8
    
    def is_novel(self, argument: str, used_arguments: List[str]) -> bool:
        """Check if argument is sufficiently different from previous ones"""
        if not used_arguments:
            return True
        
        argument_clean = self.normalize_text(argument)
        
        for used_arg in used_arguments[-5:]:  # Check against last 5 arguments
            used_clean = self.normalize_text(used_arg)
            similarity = self.calculate_similarity(argument_clean, used_clean)
            
            if similarity > self.max_similarity:
                return False
        
        return True
    
    def is_relevant(self, argument: str) -> bool:
        """Basic relevance check - can be enhanced with topic analysis"""
        # Check for common debate quality indicators
        quality_indicators = [
            r'\bbecause\b', r'\btherefore\b', r'\bhowever\b', 
            r'\bevidence\b', r'\bresearch\b', r'\bstudies\b',
            r'\bdata\b', r'\banalysis\b', r'\baccording\b',
            r'\bshould\b', r'\bmust\b', r'\bwould\b'
        ]
        
        argument_lower = argument.lower()
        matches = sum(1 for indicator in quality_indicators 
                     if re.search(indicator, argument_lower))
        
        return matches >= 1
    
    def _is_placeholder(self, argument: str) -> bool:
        """Check if argument contains placeholder text"""
        placeholder_patterns = [
            r'\[.*?\]',  # [placeholder text]
            r'<.*?>',    # <placeholder>
            r'TODO',
            r'FIXME',
            r'XXX',
            r'\[Error',  # Error messages
        ]
        
        arg_upper = argument.upper()
        for pattern in placeholder_patterns:
            if re.search(pattern, arg_upper):
                return True
        
        return False
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for similarity comparison"""
        # Convert to lowercase and remove punctuation
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts using sequence matching"""
        return SequenceMatcher(None, text1, text2).ratio()
    
    def get_validation_feedback(self, argument: str, used_arguments: List[str]) -> str:
        """Get specific feedback on why an argument failed validation"""
        if not self.has_minimum_length(argument):
            return "Argument is too short. Please provide more detailed reasoning (at least 10 words, 20 characters)."
        
        if self._is_placeholder(argument):
            return "Argument contains placeholder or error text. Please provide a real argument."
        
        if not self.has_substance(argument):
            return "Argument lacks substantive content. Avoid filler phrases and provide concrete points."
        
        if not self.is_novel(argument, used_arguments):
            return "Argument is too similar to previous arguments. Please provide a novel perspective."
        
        if not self.is_relevant(argument):
            return "Argument lacks clear reasoning indicators. Use logical connectors like 'because', 'therefore', etc."
        
        return "Argument is valid."
    
    def get_validation_errors(self, argument: str, used_arguments: List[str]) -> List[str]:
        """Get detailed validation errors for an argument (for compatibility with base_agent.py)
        
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        if not argument or not isinstance(argument, str):
            errors.append("Argument is empty or not a string")
            return errors
        
        if not self.has_minimum_length(argument):
            errors.append(f"Argument too short (minimum {self.min_length} words, 20 characters)")
        
        if self._is_placeholder(argument):
            errors.append("Argument contains placeholder or error text")
        
        if not self.has_substance(argument):
            errors.append("Argument lacks substantive content")
        
        if not self.is_novel(argument, used_arguments):
            errors.append(f"Argument too similar to previous arguments (threshold: {self.max_similarity})")
        
        if not self.is_relevant(argument):
            errors.append("Argument lacks clear reasoning indicators")
        
        return errors