// Test script to verify the voice command integration
const fetch = require('node-fetch');

async function testVoiceIntegration() {
  console.log('🧪 Testing Voice Command Integration...\n');
  
  const backendUrl = 'http://localhost:8001';
  const testCommands = [
    'play some jazz music',
    'pause the radio',
    'next station',
    'search for classical music',
    'tune to rock station'
  ];

  for (const command of testCommands) {
    try {
      console.log(`🎤 Testing: "${command}"`);
      
      const response = await fetch(`${backendUrl}/api/voice/interpret`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: command,
          context: 'radio_control'
        }),
      });

      if (!response.ok) {
        console.error(`❌ Error: ${response.status}`);
        continue;
      }

      const result = await response.json();
      console.log(`✅ Intent: ${result.intent}`);
      console.log(`📊 Confidence: ${Math.round(result.confidence * 100)}%`);
      console.log(`📝 Parameters:`, result.parameters);
      console.log(`💡 Explanation: ${result.explanation}\n`);
      
    } catch (error) {
      console.error(`❌ Error testing "${command}":`, error.message);
    }
  }
  
  console.log('🎉 Voice integration test completed!');
}

testVoiceIntegration().catch(console.error);