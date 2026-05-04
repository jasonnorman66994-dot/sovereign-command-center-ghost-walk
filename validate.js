// (Express app lines removed for CLI validation)
const Ajv = require('ajv');
const schema = require('./schema.json');
const fs = require('fs');

// Initialize AJV with strict mode and format validation
const ajv = new Ajv({
  allErrors: true,
  strict: false,  // Allow non-standard keywords like "example"
  validateFormats: true,
  useDefaults: true
});

const validate = ajv.compile(schema);

// Validate the example from schema.json
console.log('\n🔍 Validating Identity Threat Alert Payload...\n');
const data = schema.example;
const valid = validate(data);

if (valid) {
  console.log('✅ Schema example is VALID!\n');
  console.log('📋 Alert Type:', data.alert_type);
  console.log('📣 Severity:', data.severity);
  console.log('👤 User:', data.user.email);
  console.log('⚠️ Event Type:', data.event.event_type);
  console.log('🧩 Risk Detections:', data.event.risk_detections.length, 'found');
} else {
  console.error('❌ Validation FAILED!\n');
  console.error('Errors:');
  validate.errors.forEach((err, idx) => {
    console.error(`  [${idx + 1}] ${err.instancePath || 'root'} - ${err.message}`);
  });
  process.exit(1);
}

// Test with custom payloads if provided via CLI
if (process.argv[2]) {
  console.log('\n---\n🔄 Testing custom payload...\n');
  try {
    const customPayload = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
    const customValid = validate(customPayload);
    if (customValid) {
      console.log('✅ Custom payload is VALID!');
    } else {
      console.error('❌ Custom payload validation FAILED:');
      validate.errors.forEach((err, idx) => {
        console.error(`  [${idx + 1}] ${err.instancePath || 'root'} - ${err.message}`);
      });
      process.exit(1);
    }
  } catch (err) {
    console.error('❌ Error reading custom payload:', err.message);
    process.exit(1);
  }
}
