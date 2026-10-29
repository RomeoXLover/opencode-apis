/**
 * OpenCode APIs - Node.js Integration Example
 * Demonstrates querying the VPS API using native fetch (Node 18+).
 */

const VPS_URL = process.env.OPENCODE_API_URL || 'http://127.0.0.1:8000/v1/chat/completions';
const API_KEY = process.env.OPENCODE_API_KEY || 'sk-opencode-sample-key';

async function main() {
    console.log(`Sending request to OpenCode VPS API: ${VPS_URL}`);

    const payload = {
        model: 'qwen2.5-coder:7b',
        messages: [
            { role: 'system', content: 'You are an expert JavaScript developer.' },
            { role: 'user', content: 'Write an asynchronous retry helper in Node.js.' }
        ],
        temperature: 0.2
    };

    try {
        const response = await fetch(VPS_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${API_KEY}`
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const err = await response.text();
            throw new Error(`HTTP ${response.status}: ${err}`);
        }

        const data = await response.json();
        console.log('\n--- Model Response ---');
        console.log(data.choices[0].message.content);
        console.log('----------------------');
    } catch (err) {
        console.error('Request failed:', err.message);
    }
}

main();
