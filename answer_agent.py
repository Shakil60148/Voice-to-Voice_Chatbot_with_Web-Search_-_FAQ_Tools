import os
import json
from dotenv import load_dotenv
from fuzzywuzzy import process
from tavily import TavilyClient
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class AnswerAgent:
    def __init__(self, qa_database_path='qa_database.json'):
        """
        Initialize the Answer Agent
        
        Args:
            qa_database_path: Path to the QA database JSON file
        """
        # Load the QA database
        self.qa_database = self._load_qa_database(qa_database_path)
        
        # Initialize Tavily client for web searches
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
        if not self.tavily_api_key:
            logger.warning("Tavily API key not found. Web search will not be available.")
        else:
            self.tavily_client = TavilyClient(api_key=self.tavily_api_key)
    
    def _load_qa_database(self, qa_database_path):
        """
        Load the QA database from a JSON file
        
        Args:
            qa_database_path: Path to the QA database JSON file
            
        Returns:
            Dictionary containing the QA database
        """
        try:
            with open(qa_database_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading QA database: {e}")
            # Return an empty database if loading fails
            return {"questions": []}
    
    def find_best_match_in_database(self, query, threshold=80):
        """
        Find the best match for the query in the QA database
        
        Args:
            query: The query to match
            threshold: The minimum similarity score (0-100) to consider a match
            
        Returns:
            The answer if a match is found, None otherwise
        """
        if not query or not self.qa_database["questions"]:
            return None
        
        # Extract all questions from the database
        questions = [q["question"] for q in self.qa_database["questions"]]
        
        # Find the best match
        best_match, score = process.extractOne(query, questions)
        
        logger.info(f"Best match: '{best_match}' with score {score}")
        
        # Return the answer if the score is above the threshold
        if score >= threshold:
            for item in self.qa_database["questions"]:
                if item["question"] == best_match:
                    return item["answer"]
        
        return None
    
    def search_web(self, query):
        """
        Search the web for an answer using Tavily
        
        Args:
            query: The query to search for
            
        Returns:
            The search results as a string
        """
        if not self.tavily_api_key:
            return "Web search is not available because the Tavily API key is missing."
        
        try:
            # Perform the search
            logger.info(f"Searching web for: {query}")
            search_result = self.tavily_client.search(query=query, search_depth="advanced")
            
            # Extract the content
            if search_result and "results" in search_result:
                # Create a formatted response
                formatted_response = "Here's what I found on the web:\n\n"
                
                for i, result in enumerate(search_result["results"][:3], 1):
                    formatted_response += f"{i}. {result.get('title', 'No title')}\n"
                    formatted_response += f"   {result.get('content', 'No content')[:300]}...\n\n"
                
                return formatted_response
            else:
                return "I couldn't find relevant information on the web for your question."
        
        except Exception as e:
            logger.error(f"Error searching the web: {e}")
            return f"Sorry, there was an error while searching the web: {str(e)}"
    
    def get_answer(self, query):
        """
        Get an answer for the query by first checking the QA database
        and then searching the web if necessary
        
        Args:
            query: The query to answer
            
        Returns:
            The answer as a string
        """
        # First check if the query matches something in the database
        database_answer = self.find_best_match_in_database(query)
        
        if database_answer:
            return {
                "source": "database",
                "answer": database_answer
            }
        
        # If not found in the database, search the web
        web_answer = self.search_web(query)
        
        return {
            "source": "web",
            "answer": web_answer
        }


# For testing
if __name__ == "__main__":
    agent = AnswerAgent()
    
    # Test with a question in the database
    test_query = "What is a voice assistant?"
    result = agent.get_answer(test_query)
    print(f"Query: {test_query}")
    print(f"Source: {result['source']}")
    print(f"Answer: {result['answer']}")
    
    # Test with a question not in the database
    test_query = "What is the weather like today?"
    result = agent.get_answer(test_query)
    print(f"\nQuery: {test_query}")
    print(f"Source: {result['source']}")
    print(f"Answer: {result['answer']}")
