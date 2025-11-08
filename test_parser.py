"""Test script for WhatsApp parser with different formats."""

import sys
sys.path.append('.')

from app.parser import WhatsAppParser

# Test with the new format
test_content = """[2022/7/21 05:11:12] Sunaya: ‎消息和通话已进行端到端加密。只有此聊天中的成员可以查看、收听或分享。
[2022/7/21 05:11:12] Eric Gao: Hi Sunaya, this is Eric from the Linux group. Just received that email from Mr. Juan, are you in Plaza Inn too?
[2022/7/21 05:21:28] Sunaya: Yes
[2022/7/21 05:22:02] Sunaya: My flight's on the 22nd
[2022/7/21 05:22:17] Sunaya: And I have to quarantine for a day
[2022/7/21 05:23:24] Sunaya: So I'll be there till 23-24
[2022/7/21 05:35:21] Eric Gao: oh ok
[2022/7/21 05:35:37] Eric Gao: I would quarantine for 5 days as I arrived on 19th, and I would leave on 24th
[2022/7/21 06:12:56] Sunaya: Are you staying there too?
[2022/7/21 06:13:20] Sunaya: Oh nice. We might run into each other there
[2022/7/21 06:15:10] Sunaya: Just saw the email, looks like we'll be traveling together"""

parser = WhatsAppParser()
messages = parser.parse_file(test_content)

print(f"\n✅ Parsed {len(messages)} messages\n")

for i, msg in enumerate(messages, 1):
    print(f"{i}. [{msg.timestamp}] {msg.username}: {msg.message[:60]}{'...' if len(msg.message) > 60 else ''}")

# Get statistics
stats = parser.get_statistics(messages)
print(f"\n📊 Statistics:")
print(f"   Total messages: {stats['total_messages']}")
print(f"   Unique users: {stats['unique_users']}")
print(f"   Users: {', '.join(stats['users'])}")
print(f"   Text messages: {stats['text_messages']}")
print(f"   Media messages: {stats['media_messages']}")
print(f"   Date range: {stats['date_range']['start']} to {stats['date_range']['end']}")
