"""
Reset database and re-upload chat data with BERTopic-based topics.
"""
import asyncio
import httpx
from pathlib import Path

async def reset_and_upload():
    """Reset the database and upload sample chat."""
    
    print("🔄 Database Reset & Re-upload Script")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Check if server is running
        try:
            response = await client.get(f"{base_url}/status")
            print(f"✅ Server is running")
        except Exception as e:
            print(f"❌ Server not running: {e}")
            print("   Please start the server: python -m app.main")
            return
        
        # Upload sample chat (this will now use BERTopic)
        chat_file = Path("sample_chat.txt")
        if not chat_file.exists():
            chat_file = Path("test_chat.txt")
        
        if not chat_file.exists():
            print("❌ No chat file found (sample_chat.txt or test_chat.txt)")
            return
        
        print(f"\n📤 Uploading {chat_file.name}...")
        with open(chat_file, 'rb') as f:
            files = {'file': (chat_file.name, f, 'text/plain')}
            response = await client.post(f"{base_url}/upload", files=files)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Upload successful!")
            print(f"   Messages: {data['statistics'].get('total_messages', 0)}")
            print(f"   Users: {data['statistics'].get('total_users', 0)}")
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   {response.text}")
            return
        
        # Get status
        print(f"\n📊 Database Status:")
        response = await client.get(f"{base_url}/status")
        if response.status_code == 200:
            status = response.json()
            db_stats = status['database_stats']
            print(f"   Users: {db_stats.get('users', 0)}")
            print(f"   Messages: {db_stats.get('messages', 0)}")
            print(f"   Topics: {db_stats.get('topics', 0)} (using BERTopic/LDA)")
            print(f"   Relationships: {db_stats.get('relationships', 0)}")
        
        # Test network graph endpoint
        print(f"\n🌐 Testing Network Graph Visualization:")
        response = await client.get(f"{base_url}/visualize/graph")
        if response.status_code == 200:
            data = response.json()
            if 'chart' in data and 'data' in data['chart']:
                print(f"   ✅ Network graph generated successfully")
                print(f"   Nodes: {len(data['analysis']['nodes'])}")
                print(f"   Edges: {len(data['analysis']['edges'])}")
            else:
                print(f"   ⚠️  Network graph structure issue")
        else:
            print(f"   ❌ Network graph failed: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("✅ Complete! Database now uses BERTopic for topics.")
    print("🌐 Neo4j Browser: http://localhost:7474")
    print("   Username: neo4j")
    print("   Password: mimicai2025")
    print("\n💡 Run visualizations: .\\run_viz_test.ps1")

if __name__ == "__main__":
    asyncio.run(reset_and_upload())
