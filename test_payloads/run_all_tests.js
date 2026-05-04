// Batch validate and format all payloads in test_payloads folder
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const payloadDir = path.join(__dirname);
const payloadFiles = fs.readdirSync(payloadDir).filter(f => f.endsWith('.json'));

console.log('--- Batch Validation & Formatting ---');

payloadFiles.forEach(file => {
  const filePath = path.join(payloadDir, file);
  console.log(`\n=== Testing: ${file} ===`);
  try {
    execSync(`node ../validate.js ${file}`, { stdio: 'inherit', cwd: payloadDir });
    execSync(`python ../telegram_formatter.py ${file}`, { stdio: 'inherit', cwd: payloadDir });
    execSync(`node ../telegram-formatter.js ${file}`, { stdio: 'inherit', cwd: payloadDir });
    console.log('✅ All tests passed for', file);
  } catch (err) {
    console.error('❌ Test failed for', file);
  }
});

console.log('\n--- Batch Test Complete ---');
