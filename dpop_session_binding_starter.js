// DPoP/session binding starter for SvelteKit/React (Node.js backend)
// This example uses jose for JWT and key management
// npm install jose

import { generateKeyPair, exportJWK, SignJWT, jwtVerify } from 'jose';

// 1. On login, generate a key pair and bind session token to public key
export async function issueSessionToken(userId) {
  const { publicKey, privateKey } = await generateKeyPair('ES256');
  const pubJwk = await exportJWK(publicKey);
  // Store pubJwk in DB, associate with userId/session
  const token = await new SignJWT({ userId })
    .setProtectedHeader({ alg: 'ES256' })
    .setIssuedAt()
    .setExpirationTime('2h')
    .setJti(crypto.randomUUID())
    .setClaim('dpop_pub', pubJwk)
    .sign(privateKey);
  return { token, privateKey }; // Send token to client, keep privateKey in browser
}

// 2. On each request, client signs a DPoP proof with privateKey
// (Client-side: use jose to sign a DPoP JWT with privateKey, send as header)

// 3. On backend, verify DPoP proof and match pubJwk to session
export async function verifySessionToken(token, dpopProof) {
  const { payload } = await jwtVerify(token, /* get publicKey from DB by userId/session */);
  const dpopPub = payload.dpop_pub;
  // Verify dpopProof JWT is signed by dpopPub
  // If not, reject session as hijacked
}

// This pattern ensures a stolen session token is useless without the device's private key.
// For production, use HTTPS, secure key storage, and rotate keys as needed.
