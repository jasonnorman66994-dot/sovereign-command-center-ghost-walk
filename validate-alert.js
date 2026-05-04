const Ajv = require('ajv');
const fs = require('fs');
const schema = require('./alert-v2-schema.json');

// Load alert JSON from file or stdin
const alertFile = process.argv[2] || 'example-alert-filled.json';
const data = JSON.parse(fs.readFileSync(alertFile, 'utf-8'));

const ajv = new Ajv({ allErrors: true, strict: false });
const validate = ajv.compile(schema);

const valid = validate(data);
if (valid) {
  console.log('✅ Alert is valid!');
} else {
  console.error('❌ Validation errors:', validate.errors);
  process.exit(1);
}
