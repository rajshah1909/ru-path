"""
Test file for RU-PATH Chatbot
Run with: python test_chatbot.py
"""

import os
from dotenv import load_dotenv
from src.data_loader import DataLoader
from src.chatbot import ParkingChatbot

# Load environment variables
load_dotenv()


def test_chatbot():
    """Test the chatbot with sample conversations"""
    
    print("=" * 60)
    print("RU-PATH Chatbot Test (DeepSeek API)")
    print("=" * 60)
    print()
    
    # Check if API key is set
    if not os.getenv('DEEPSEEK_API_KEY'):
        print("ERROR: DEEPSEEK_API_KEY not found in environment variables")
        print("Please create a .env file with your DeepSeek API key")
        print("\nExample .env file:")
        print("DEEPSEEK_API_KEY=your_api_key_here")
        return
    
    # Initialize components
    print("Initializing chatbot with DeepSeek...")
    try:
        data_loader = DataLoader()
        chatbot = ParkingChatbot(data_loader)
        print(f"✅ Loaded {data_loader.get_lots_count()} parking lots")
    except Exception as e:
        print(f"❌ Error initializing chatbot: {str(e)}")
        return
    print()
    
    # Simulate a conversation
    session_id = "test_session"
    conversation_history = []
    
    # Test messages
    test_messages = [
        "Hi, I need help finding parking",
        "I'm a student",
        "I'm going to College Avenue",
        "Just for a few hours during the day"
    ]
    
    print("Starting test conversation...")
    print("-" * 60)
    
    for user_message in test_messages:
        print(f"\n🧑 User: {user_message}")
        
        try:
            # Get bot response
            response = chatbot.process_message(
                user_message=user_message,
                session_id=session_id,
                conversation_history=conversation_history
            )
            
            print(f"\n🤖 Bot: {response}")
            
            # Update conversation history
            conversation_history.append({
                'role': 'user',
                'content': user_message
            })
            conversation_history.append({
                'role': 'assistant',
                'content': response
            })
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            break
        
        print("-" * 60)
    
    print("\n✅ Test completed!")
    print(f"Total messages: {len(conversation_history)}")


def test_data_loader():
    """Test the data loader"""
    print("\n" + "=" * 60)
    print("Testing Data Loader")
    print("=" * 60)
    
    data_loader = DataLoader()
    
    print(f"\n✅ Total parking lots: {data_loader.get_lots_count()}")
    print(f"✅ Campuses: {', '.join(data_loader.get_campuses())}")
    
    # Test search
    print("\n--- Student parking on College Avenue ---")
    results = data_loader.search_lots(campus="College Avenue", permit_type="student")
    for lot in results:
        print(f"  🅿️  {lot['lot_name']}: {lot['notes']}")
    
    # Test visitor parking
    print("\n--- Visitor parking ---")
    visitor_lots = data_loader.get_lots_by_permit("visitor")
    for lot in visitor_lots:
        print(f"  🅿️  {lot['lot_name']} on {lot['campus']}: {lot['time_restrictions']}")


def interactive_test():
    """Interactive testing mode"""
    print("\n" + "=" * 60)
    print("Interactive Chatbot Test (DeepSeek API)")
    print("=" * 60)
    print("Type 'quit' to exit\n")
    
    # Check API key
    if not os.getenv('DEEPSEEK_API_KEY'):
        print("❌ ERROR: DEEPSEEK_API_KEY not found")
        print("\nPlease create a .env file with:")
        print("DEEPSEEK_API_KEY=your_api_key_here")
        return
    
    # Initialize
    print("Initializing chatbot...")
    try:
        data_loader = DataLoader()
        chatbot = ParkingChatbot(data_loader)
        print(f"✅ Chatbot ready! ({data_loader.get_lots_count()} parking lots loaded)")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return
    
    session_id = "interactive_session"
    conversation_history = []
    
    print("\nStart chatting...\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye!")
                break
            
            # Get response
            response = chatbot.process_message(
                user_message=user_input,
                session_id=session_id,
                conversation_history=conversation_history
            )
            
            print(f"\nBot: {response}\n")
            
            # Update history
            conversation_history.append({'role': 'user', 'content': user_input})
            conversation_history.append({'role': 'assistant', 'content': response})
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'interactive':
        interactive_test()
    elif len(sys.argv) > 1 and sys.argv[1] == 'data':
        test_data_loader()
    else:
        # Run automated test
        print("Running automated test...")
        print("Use 'python test_chatbot.py interactive' for interactive mode")
        print("Use 'python test_chatbot.py data' to test data loader only\n")
        test_chatbot()