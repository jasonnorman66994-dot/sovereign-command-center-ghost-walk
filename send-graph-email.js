const { ClientSecretCredential } = require("@azure/identity");
const { Client } = require("@microsoft/microsoft-graph-client");
require("isomorphic-fetch");

const tenantId = "54fa77b9-eaf6-4246-98be-4c171050b6bb";
const clientId = "3f99c3e6-c8be-4142-a482-bbb26b6e92a9";
const clientSecret = "YOUR_CLIENT_SECRET"; // Use your secret here, but keep it private!
const userEmail = "YOUR_EMAIL@outlook.com"; // The recipient

const credential = new ClientSecretCredential(tenantId, clientId, clientSecret);

async function sendMail(subject, body) {
  const graphClient = Client.initWithMiddleware({
    authProvider: {
      getAccessToken: async () => {
        const token = await credential.getToken("https://graph.microsoft.com/.default");
        return token.token;
      }
    }
  });

  await graphClient.api('/users/' + userEmail + '/sendMail').post({
    message: {
      subject,
      body: { contentType: "Text", content: body },
      toRecipients: [{ emailAddress: { address: userEmail } }]
    }
  });

  console.log("Email sent!");
}

// Example usage:
sendMail("SOC Alert JSON Validation Results", "Your validation summary here.");