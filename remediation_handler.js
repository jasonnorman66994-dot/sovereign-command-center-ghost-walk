// remediation_handler.js
// Simulates automated remediation actions for the SOC

function revokeSessionToken(sessionTokenAudit) {
  // Simulate call to IdP (Okta/Azure AD)
  console.log(`[REMEDIATION] SessionToken audit=${sessionTokenAudit} revoked via IdP.`);
}

function isolateWorkstation(wsid) {
  // Simulate network quarantine and HUD update
  console.log(`[REMEDIATION] Workstation ${wsid} isolated from network (HUD: Red/Isolated).`);
  // Emit event for HUD update (to be called from server.js)
  return { wsid, status: 'Isolated', color: 'red' };
}

function notifySOC(user, wsid, sessionTokenAudit) {
  // Simulate alert to SOC operator
  const msg = `[ALERT] Compromise neutralized for ${user} (${wsid}) [SessionTokenAudit: ${sessionTokenAudit}] <2s`;
  console.log(msg);
  return msg;
}

module.exports = {
  revokeSessionToken,
  isolateWorkstation,
  notifySOC
};
