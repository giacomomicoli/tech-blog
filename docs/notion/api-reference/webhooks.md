> ## Documentation Index
> Fetch the complete documentation index at: https://developers.notion.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Webhooks

> Learn how your integration can automatically respond to workspace activity in real-time.

export const integrationsDashboardUrl = "https://www.notion.so/profile/integrations";

Webhooks let your integration receive real-time updates from Notion. Whenever a page or database changes, Notion sends a secure HTTP POST request to your webhook endpoint. This allows your application to respond to workspace activity as it happens — whether that's syncing data, triggering automation, or keeping your UI in sync with user activity.

<Frame>
    <img src="https://mintcdn.com/notion-demo/kSI9TVzPayvF1_1o/images/reference/cf4e4b4cbb5de9c5b1277b35386a21574b4960af36c14fe7d648d905377db478-image.png?fit=max&auto=format&n=kSI9TVzPayvF1_1o&q=85&s=1c744340e3bd893d14a8a63faeee7e69" alt="" data-og-width="1334" width="1334" data-og-height="676" height="676" data-path="images/reference/cf4e4b4cbb5de9c5b1277b35386a21574b4960af36c14fe7d648d905377db478-image.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/notion-demo/kSI9TVzPayvF1_1o/images/reference/cf4e4b4cbb5de9c5b1277b35386a21574b4960af36c14fe7d648d905377db478-image.png?w=280&fit=max&auto=format&n=kSI9TVzPayvF1_1o&q=85&s=521391ee5dc450cbb6caec5bb2c10673 280w, https://mintcdn.com/notion-demo/kSI9TVzPayvF1_1o/images/reference/cf4e4b4cbb5de9c5b1277b35386a21574b4960af36c14fe7d648d905377db478-image.png?w=560&fit=max&auto=format&n=kSI9TVzPayvF1_1o&q=85&s=9de2747b3d1ba856c71dbcb460700bc4 560w, https://mintcdn.com/notion-demo/kSI9TVzPayvF1_1o/images/reference/cf4e4b4cbb5de9c5b1277b35386a21574b4960af36c14fe7d648d905377db478-image.png?w=840&fit=max&auto=format&n=kSI9TVzPayvF1_1o&q=85&s=e8dc23e88e340ecaec2de9675106be7a 840w, https://mintcdn.com/notion-demo/kSI9TVzPayvF1_1o/images/reference/cf4e4b4cbb5de9c5b1277b35386a21574b4960af36c14fe7d648d905377db478-image.png?w=1100&fit=max&auto=format&n=kSI9TVzPayvF1_1o&q=85&s=553257aa6d4bfde94165afeebad5b6c4 1100w, https://mintcdn.com/notion-demo/kSI9TVzPayvF1_1o/images/reference/cf4e4b4cbb5de9c5b1277b35386a21574b4960af36c14fe7d648d905377db478-image.png?w=1650&fit=max&auto=format&n=kSI9TVzPayvF1_1o&q=85&s=76ff8cbfba7677e9162eb293568bf631 1650w, https://mintcdn.com/notion-demo/kSI9TVzPayvF1_1o/images/reference/cf4e4b4cbb5de9c5b1277b35386a21574b4960af36c14fe7d648d905377db478-image.png?w=2500&fit=max&auto=format&n=kSI9TVzPayvF1_1o&q=85&s=d9b01c5e813c8b987eec702682ec8457 2500w" />
</Frame>

**Think of it like this:** Instead of repeatedly polling the Notion API to check if anything has changed, Notion will tell you the moment something important happens.

## How webhooks work: A simple example

**Let’s walk through an example from start to finish:**

<Steps>
  <Step>
    Your integration is subscribed to `page.content_updated` events.
  </Step>

  <Step>
    A user edits the title of a page in Notion.
  </Step>

  <Step>
    Within a minute, Notion sends a webhook request to your configured endpoint.
  </Step>

  <Step>
    The event payload includes metadata such as the page ID, the event type, and a timestamp.
  </Step>

  <Step>
    Your server receives the event, verifies it, and calls the Notion API to fetch the updated title using the page ID from the event.
  </Step>

  <Step>
    Your application updates its internal data or takes any other action you’ve defined.
  </Step>
</Steps>

This flow lets you react quickly to user activity, without polling or guessing when something has changed.

## Getting started with webhooks

### Step 1 - Creating a webhook subscription

To receive webhook events, you’ll need to create a subscription through your integration settings.

**You’ll need to:**

<Steps>
  <Step>
    Visit your <a href={integrationsDashboardUrl}>integration settings</a>.
  </Step>

  <Step>
    Either create a new integration or select an existing one.
  </Step>

  <Step>
    Navigate to the **Webhooks** tab and click **+ Create a subscription**.

    <Frame>
            <img src="https://mintcdn.com/notion-demo/kSI9TVzPayvF1_1o/images/reference/522e40363df1bd7437239b25a1caacc8cc607426f45fc90febfff5f00647aeb4-webhooks-1.png?fit=max&auto=format&n=kSI9TVzPayvF1_1o&q=85&s=d749482045c385e3bd2b0200208e1cb3" alt="" data-og-width="1916" width="1916" data-og-height="1324" height="1324" data-path="images/reference/522e40363df1bd7437239b25a1caacc8cc607426f45fc90febfff5f00647aeb4-webhooks-1.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/notion-demo/kSI9TVzPayvF1_1o/images/reference/522e40363df1bd7437239b25a1caacc8cc607426f45fc90febfff5f00647aeb4-webhooks-1.png?w=280&fit=max&auto=format&n=kSI9TVzPayvF1_1o&q=85&s=ea2d1b9bc9500c8897e96aa9cbcb24ec 280w, https://mintcdn.com/notion-demo/kSI9TVzPayvF1_1o/images/reference/522e40363df1bd7437239b25a1caacc8cc607426f45fc90febfff5f00647aeb4-webhooks-1.png?w=560&fit=max&auto=format&n=kSI9TVzPayvF1_1o&q=85&s=ac0f2e255c78953e0d4e3ef415ea4df2 560w, https://mintcdn.com/notion-demo/kSI9TVzPayvF1_1o/images/reference/522e40363df1bd7437239b25a1caacc8cc607426f45fc90febfff5f00647aeb4-webhooks-1.png?w=840&fit=max&auto=format&n=kSI9TVzPayvF1_1o&q=85&s=bbba5fac6e70090cd3733e8691ed3627 840w, https://mintcdn.com/notion-demo/kSI9TVzPayvF1_1o/images/reference/522e40363df1bd7437239b25a1caacc8cc607426f45fc90febfff5f00647aeb4-webhooks-1.png?w=1100&fit=max&auto=format&n=kSI9TVzPayvF1_1o&q=85&s=a0285fab3a9637f80980426874105314 1100w, https://mintcdn.com/notion-demo/kSI9TVzPayvF1_1o/images/reference/522e40363df1bd7437239b25a1caacc8cc607426f45fc90febfff5f00647aeb4-webhooks-1.png?w=1650&fit=max&auto=format&n=kSI9TVzPayvF1_1o&q=85&s=00d8fa849c3fac3a86cdc3a781adf5e4 1650w, https://mintcdn.com/notion-demo/kSI9TVzPayvF1_1o/images/reference/522e40363df1bd7437239b25a1caacc8cc607426f45fc90febfff5f00647aeb4-webhooks-1.png?w=2500&fit=max&auto=format&n=kSI9TVzPayvF1_1o&q=85&s=37b1c66aa59db4315a4d6f5f7316d593 2500w" />
    </Frame>
  </Step>

  <Step>
    Enter your public **Webhook URL** — this is the public endpoint where you want Notion to send events. It must be a secure (SSL) and publicly available endpoint. Endpoints in localhost are not reachable.

    <Frame>
            <img src="https://mintcdn.com/notion-demo/kSI9TVzPayvF1_1o/images/reference/1ef497d7b9b3622de379e6907cd722167766413693ac9f1885b59eb028b4e7dd-webhooks-2.png?fit=max&auto=format&n=kSI9TVzPayvF1_1o&q=85&s=b0448cd6aabad1fb6be140e4cfddddd9" alt="" data-og-width="1686" width="1686" data-og-height="1386" height="1386" data-path="images/reference/1ef497d7b9b3622de379e6907cd722167766413693ac9f1885b59eb028b4e7dd-webhooks-2.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/notion-demo/kSI9TVzPayvF1_1o/images/reference/1ef497d7b9b3622de379e6907cd722167766413693ac9f1885b59eb028b4e7dd-webhooks-2.png?w=280&fit=max&auto=format&n=kSI9TVzPayvF1_1o&q=85&s=45ccfb2aefa53f95b5f2c786c773fadd 280w, https://mintcdn.com/notion-demo/kSI9TVzPayvF1_1o/images/reference/1ef497d7b9b3622de379e6907cd722167766413693ac9f1885b59eb028b4e7dd-webhooks-2.png?w=560&fit=max&auto=format&n=kSI9TVzPayvF1_1o&q=85&s=049176d0ed5a1b69f10ea4761ee83feb 560w, https://mintcdn.com/notion-demo/kSI9TVzPayvF1_1o/images/reference/1ef497d7b9b3622de379e6907cd722167766413693ac9f1885b59eb028b4e7dd-webhooks-2.png?w=840&fit=max&auto=format&n=kSI9TVzPayvF1_1o&q=85&s=8846f8049f16209d86244f36e64e6660 840w, https://mintcdn.com/notion-demo/kSI9TVzPayvF1_1o/images/reference/1ef497d7b9b3622de379e6907cd722167766413693ac9f1885b59eb028b4e7dd-webhooks-2.png?w=1100&fit=max&auto=format&n=kSI9TVzPayvF1_1o&q=85&s=86b1f0ee3a0b24a49c284b61e00a6e80 1100w, https://mintcdn.com/notion-demo/kSI9TVzPayvF1_1o/images/reference/1ef497d7b9b3622de379e6907cd722167766413693ac9f1885b59eb028b4e7dd-webhooks-2.png?w=1650&fit=max&auto=format&n=kSI9TVzPayvF1_1o&q=85&s=2419cff76c2ec7745c9cd5a4d8a87be8 1650w, https://mintcdn.com/notion-demo/kSI9TVzPayvF1_1o/images/reference/1ef497d7b9b3622de379e6907cd722167766413693ac9f1885b59eb028b4e7dd-webhooks-2.png?w=2500&fit=max&auto=format&n=kSI9TVzPayvF1_1o&q=85&s=a652a94b3e8d23470a123c2db16b3a28 2500w" />
    </Frame>
  </Step>

  <Step>
    Choose which event types you'd like to subscribe to. You can modify these later if needed.
  </Step>

  <Step>
    Click **Create subscription**.

    <Frame>
            <img src="https://mintcdn.com/notion-demo/kSI9TVzPayvF1_1o/images/reference/6e68cad7be75acc8165e29eb2a56a282edba31fdcba78238831466b83a115b8f-webhooks-3.png?fit=max&auto=format&n=kSI9TVzPayvF1_1o&q=85&s=d3b26ec8514419ade5461e627d40def9" alt="" data-og-width="1834" width="1834" data-og-height="1418" height="1418" data-path="images/reference/6e68cad7be75acc8165e29eb2a56a282edba31fdcba78238831466b83a115b8f-webhooks-3.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/notion-demo/kSI9TVzPayvF1_1o/images/reference/6e68cad7be75acc8165e29eb2a56a282edba31fdcba78238831466b83a115b8f-webhooks-3.png?w=280&fit=max&auto=format&n=kSI9TVzPayvF1_1o&q=85&s=a2a0a1e4c27b756bf108deda754f1feb 280w, https://mintcdn.com/notion-demo/kSI9TVzPayvF1_1o/images/reference/6e68cad7be75acc8165e29eb2a56a282edba31fdcba78238831466b83a115b8f-webhooks-3.png?w=560&fit=max&auto=format&n=kSI9TVzPayvF1_1o&q=85&s=bd866abaaa7a90a174b23e4a335a3508 560w, https://mintcdn.com/notion-demo/kSI9TVzPayvF1_1o/images/reference/6e68cad7be75acc8165e29eb2a56a282edba31fdcba78238831466b83a115b8f-webhooks-3.png?w=840&fit=max&auto=format&n=kSI9TVzPayvF1_1o&q=85&s=fd4efde7324efcf00c6761465b4dbd3f 840w, https://mintcdn.com/notion-demo/kSI9TVzPayvF1_1o/images/reference/6e68cad7be75acc8165e29eb2a56a282edba31fdcba78238831466b83a115b8f-webhooks-3.png?w=1100&fit=max&auto=format&n=kSI9TVzPayvF1_1o&q=85&s=821f6111688112b14393f394b3cbd102 1100w, https://mintcdn.com/notion-demo/kSI9TVzPayvF1_1o/images/reference/6e68cad7be75acc8165e29eb2a56a282edba31fdcba78238831466b83a115b8f-webhooks-3.png?w=1650&fit=max&auto=format&n=kSI9TVzPayvF1_1o&q=85&s=99e66032e76e07dd610f93c909b90ac1 1650w, https://mintcdn.com/notion-demo/kSI9TVzPayvF1_1o/images/reference/6e68cad7be75acc8165e29eb2a56a282edba31fdcba78238831466b83a115b8f-webhooks-3.png?w=2500&fit=max&auto=format&n=kSI9TVzPayvF1_1o&q=85&s=c23e6dd3ed1cbcbae8b2226738028068 2500w" />
    </Frame>
  </Step>
</Steps>

At this point, your webhook is created but not yet verified. To complete the setup, you’ll need to confirm that your endpoint can receive and respond to verification.

### Step 2 - Verifying the subscription

When you create a subscription, Notion sends a one-time POST request to your webhook URL. The body of the request contains a `verification_token`, which proves that Notion can successfully reach your endpoint.

**Example payload with `verification_token`**:

<CodeGroup>
  ```json JSON theme={null}
  {
    "verification_token": "secret_EXAMPLE_TOKEN_REDACTED"
  }
  ```
</CodeGroup>

**You’ll need to:**

<Steps>
  <Step>
    Inspect the incoming request at your endpoint and extract the `verification_token` from the JSON payload.

    1. (Optional): Securely store this token for payload validation setup later, [in step 3](#step-3-validating-event-payloads-recommended).
  </Step>

  <Step>
    Go back to the **Webhooks** tab within your Notion integration UI and click **⚠️ Verify** on the bottom left of the page

    <Frame>
            <img src="https://mintcdn.com/notion-demo/kSI9TVzPayvF1_1o/images/reference/6e68cad7be75acc8165e29eb2a56a282edba31fdcba78238831466b83a115b8f-webhooks-3.png?fit=max&auto=format&n=kSI9TVzPayvF1_1o&q=85&s=d3b26ec8514419ade5461e627d40def9" alt="" data-og-width="1834" width="1834" data-og-height="1418" height="1418" data-path="images/reference/6e68cad7be75acc8165e29eb2a56a282edba31fdcba78238831466b83a115b8f-webhooks-3.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/notion-demo/kSI9TVzPayvF1_1o/images/reference/6e68cad7be75acc8165e29eb2a56a282edba31fdcba78238831466b83a115b8f-webhooks-3.png?w=280&fit=max&auto=format&n=kSI9TVzPayvF1_1o&q=85&s=a2a0a1e4c27b756bf108deda754f1feb 280w, https://mintcdn.com/notion-demo/kSI9TVzPayvF1_1o/images/reference/6e68cad7be75acc8165e29eb2a56a282edba31fdcba78238831466b83a115b8f-webhooks-3.png?w=560&fit=max&auto=format&n=kSI9TVzPayvF1_1o&q=85&s=bd866abaaa7a90a174b23e4a335a3508 560w, https://mintcdn.com/notion-demo/kSI9TVzPayvF1_1o/images/reference/6e68cad7be75acc8165e29eb2a56a282edba31fdcba78238831466b83a115b8f-webhooks-3.png?w=840&fit=max&auto=format&n=kSI9TVzPayvF1_1o&q=85&s=fd4efde7324efcf00c6761465b4dbd3f 840w, https://mintcdn.com/notion-demo/kSI9TVzPayvF1_1o/images/reference/6e68cad7be75acc8165e29eb2a56a282edba31fdcba78238831466b83a115b8f-webhooks-3.png?w=1100&fit=max&auto=format&n=kSI9TVzPayvF1_1o&q=85&s=821f6111688112b14393f394b3cbd102 1100w, https://mintcdn.com/notion-demo/kSI9TVzPayvF1_1o/images/reference/6e68cad7be75acc8165e29eb2a56a282edba31fdcba78238831466b83a115b8f-webhooks-3.png?w=1650&fit=max&auto=format&n=kSI9TVzPayvF1_1o&q=85&s=99e66032e76e07dd610f93c909b90ac1 1650w, https://mintcdn.com/notion-demo/kSI9TVzPayvF1_1o/images/reference/6e68cad7be75acc8165e29eb2a56a282edba31fdcba78238831466b83a115b8f-webhooks-3.png?w=2500&fit=max&auto=format&n=kSI9TVzPayvF1_1o&q=85&s=c23e6dd3ed1cbcbae8b2226738028068 2500w" />
    </Frame>
  </Step>

  <Step>
    Paste the `verification_token` value into the form and click **Verify subscription.**

    <Frame>
            <img src="https://mintcdn.com/notion-demo/kSI9TVzPayvF1_1o/images/reference/42b82e16a49278f78ecfdfb6a8f5acafe1ae251376bdc636d43c68abf4f685e5-webhooks-4.png?fit=max&auto=format&n=kSI9TVzPayvF1_1o&q=85&s=88f55f71314ea42a4ca48806f1921e29" alt="" data-og-width="2026" width="2026" data-og-height="1412" height="1412" data-path="images/reference/42b82e16a49278f78ecfdfb6a8f5acafe1ae251376bdc636d43c68abf4f685e5-webhooks-4.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/notion-demo/kSI9TVzPayvF1_1o/images/reference/42b82e16a49278f78ecfdfb6a8f5acafe1ae251376bdc636d43c68abf4f685e5-webhooks-4.png?w=280&fit=max&auto=format&n=kSI9TVzPayvF1_1o&q=85&s=f5a4d8f9859c481995be20d4796b6987 280w, https://mintcdn.com/notion-demo/kSI9TVzPayvF1_1o/images/reference/42b82e16a49278f78ecfdfb6a8f5acafe1ae251376bdc636d43c68abf4f685e5-webhooks-4.png?w=560&fit=max&auto=format&n=kSI9TVzPayvF1_1o&q=85&s=c81f5725eefe875c56253f8c3e83baf6 560w, https://mintcdn.com/notion-demo/kSI9TVzPayvF1_1o/images/reference/42b82e16a49278f78ecfdfb6a8f5acafe1ae251376bdc636d43c68abf4f685e5-webhooks-4.png?w=840&fit=max&auto=format&n=kSI9TVzPayvF1_1o&q=85&s=e2823914d3735f3a471ef207db37e1e6 840w, https://mintcdn.com/notion-demo/kSI9TVzPayvF1_1o/images/reference/42b82e16a49278f78ecfdfb6a8f5acafe1ae251376bdc636d43c68abf4f685e5-webhooks-4.png?w=1100&fit=max&auto=format&n=kSI9TVzPayvF1_1o&q=85&s=92f3757424f206c3fae51c1220d0c7ff 1100w, https://mintcdn.com/notion-demo/kSI9TVzPayvF1_1o/images/reference/42b82e16a49278f78ecfdfb6a8f5acafe1ae251376bdc636d43c68abf4f685e5-webhooks-4.png?w=1650&fit=max&auto=format&n=kSI9TVzPayvF1_1o&q=85&s=4568abc7a97527feedcbb63c2d03cca3 1650w, https://mintcdn.com/notion-demo/kSI9TVzPayvF1_1o/images/reference/42b82e16a49278f78ecfdfb6a8f5acafe1ae251376bdc636d43c68abf4f685e5-webhooks-4.png?w=2500&fit=max&auto=format&n=kSI9TVzPayvF1_1o&q=85&s=fc3fddccab801edea27e1d93171683f0 2500w" />
    </Frame>

    If you did not receive a `verification_token`, you can click **Resend token** from the webhook verification modal.
  </Step>
</Steps>

Once submitted, your webhook subscription is considered active, and will start receiving events.

<Info>
  **Changing your webhook URL or event subscriptions**

  You can only change the webhook URL before verification. After verification, if you need to change the URL, you must delete and recreate the subscription. You can change the subscribed events at any time.
</Info>

### Step 3 - Validating event payloads (Recommended)

To help ensure the security of your integration, Notion includes a cryptographic signature with every webhook event we send. This allows you to verify that the payload was sent by Notion and hasn’t been modified in transit.

While payload validation is optional, we recommend implementing it for any production environment.

<Info>
  **Using a no-code or low-code platform?**

  If you're using a no-code or low-code platform (like Zapier, Make, or Pipedream), you may not have access to custom code for signature verification — and that’s okay. Validation is encouraged, but not required for webhooks to work.
</Info>

#### How it works

In the previous step, Notion sent a one-time `verification_token` to your webhook URL. You’ll use this token to verify the authenticity of all subsequent webhook events.

Every webhook request from Notion includes an `X-Notion-Signature` header, which contains an HMAC-SHA256 hash of the request body, signed with your `verification_token`.

**Sample `X-Notion-Signature` from Notion**:

<CodeGroup>
  ```json JSON theme={null}
  {
    "X-Notion-Signature": "sha256=461e8cbcba8a75c3edd866f0e71280f5a85cbf21eff040ebd10fe266df38a735"
  }
  ```
</CodeGroup>

To validate the request, you can use the `verification_token` along with the event's payload to recompute the signature and verify the request's authenticity. If they match, the payload is trustworthy.

**Sample code for computing the signature and validating the webhook payload:**

<CodeGroup>
  ```javascript JavaScript theme={null}
  import { createHmac, timingSafeEqual } from "crypto"

  // Retrieve the `verification_token` from the initial request
  // (subscription verification; Step 2)
  const verificationToken = "secret_EXAMPLE_TOKEN_REDACTED"

  // This body should come from your request body for subsequent validations
  const body = {"verification_token":"secret_EXAMPLE_TOKEN_REDACTED"}

  const calculatedSignature = `sha256=${createHmac("sha256", verificationToken).update(JSON.stringify(body)).digest("hex")}`

  const isTrustedPayload = timingSafeEqual(
    Buffer.from(calculatedSignature),
    Buffer.from(headers["X-Notion-Signature"]),
  )

  if (!isTrustedPayload) {
    // Ignore the event
    return
  }
  ```

  ```python Python theme={null}
  import hmac
  import hashlib
  import json

  # Retrieve the `verification_token` from initial request
  # (subscription verification; Step 2)
  verification_token = "secret_EXAMPLE_TOKEN_REDACTED"

  # This body should come from your request body for subsequent validations
  body = {"verification_token": "secret_EXAMPLE_TOKEN_REDACTED"}

  # Calculate the signature
  body_json = json.dumps(body, separators=(",", ":"))  # Minified JSON, matches JSON.stringify
  hmac_obj = hmac.new(
      verification_token.encode("utf-8"),
      body_json.encode("utf-8"),
      hashlib.sha256
  )
  calculated_signature = "sha256=" + hmac_obj.hexdigest()

  # Assume headers is a dict containing HTTP headers
  # Example:
  # headers = {"X-Notion-Signature": "<signature from request>"}

  # Use hmac.compare_digest for timing-safe comparison
  is_trusted_payload = hmac.compare_digest(
      calculated_signature,
      headers["X-Notion-Signature"]
  )

  if not is_trusted_payload:
      # Ignore the event
      return
  ```

  ```ruby Ruby theme={null}
  require 'openssl'
  require 'json'

  # Retrieve the verification_token from initial request
  verification_token = "secret_EXAMPLE_TOKEN_REDACTED"

  # This body should come from your request body for subsequent validations
  body = { "verification_token" => "secret_EXAMPLE_TOKEN_REDACTED" }

  # Calculate the signature (minified JSON to match JSON.stringify)
  body_json = JSON.generate(body)
  digest = OpenSSL::HMAC.hexdigest("SHA256", verification_token, body_json)
  calculated_signature = "sha256=#{digest}"

  # Assume headers is a Hash containing HTTP headers
  # Example:
  # headers = { "X-Notion-Signature" => "<signature from request>" }

  # Constant-time comparison
  is_trusted_payload = ActiveSupport::SecurityUtils.secure_compare(
    calculated_signature,
    headers["X-Notion-Signature"]
  )

  unless is_trusted_payload
    # Ignore the event
    return
  end
  ```
</CodeGroup>

Implementing this validation step is a small lift that adds a strong layer of security to your webhook integration. If you ever rotate or recreate your webhook subscription, be sure to update your stored `verification_token`.

## Testing your webhook subscription

Once your webhook subscription is set up and verified, it’s a good idea to test that everything is working as expected.

Below are three common test scenarios you can try, each corresponding to a supported event type. These tests simulate typical content updates and help ensure your endpoint is receiving and processing events correctly.

### Test 1 - Change a page title

This test checks your webhook’s ability to handle aggregated events, which are delivered with a short delay to avoid sending redundant updates.

**You’ll need to:**

<Steps>
  <Step>
    In your Notion workspace, add the integration to a page.
  </Step>

  <Step>
    Change the title of that page.
  </Step>

  <Step>
    Wait a minute or two because aggregated events like `page.content_updated` are batched and may not be sent immediately.
  </Step>

  <Step>
    Check your server logs or webhook handler. You should receive a `page.content_updated` event.
  </Step>

  <Step>
    Use the entity.id value from the payload to call the `retrieve a page` endpoint and confirm the new title.
  </Step>
</Steps>

### Test 2 - Add a comment

This test checks event delivery for comments, which require specific capabilities.

**You’ll need to:**

<Steps>
  <Step>
    In a page your integration has access to, add a new comment.
  </Step>

  <Step>
    Your webhook should receive a `comment.created` event within a few seconds.
  </Step>
</Steps>

**Important:**

To receive this event, your integration must include the `comment read` capability in its configuration. You can confirm this in the **Capabilities** tab of your integration’s settings.

### Test 3 - Modify a database schema

This test verifies that structural changes to databases are triggering events.

**You’ll need to:**

<Steps>
  <Step>
    Open any database your integration is connected to.
  </Step>

  <Step>
    Make a schema change — for example, add a new property (column), rename an existing one, or delete a property.
  </Step>

  <Step>
    Your webhook should receive a `data_source.schema_updated` (in the new 2025-09-03 API version) or `database.schema_updated` (deprecated after 2022-06-28 API version) event shortly after the change.
  </Step>
</Steps>

## Troubleshooting tips

If your webhook isn’t receiving events as expected, here are a few things to double-check. These are the most common reasons developers miss events during setup or testing.

### 🔒 1. Check access permissions

Make sure the integration has access to the object that triggered the event. For example, if a new page is created inside a private page your integration doesn’t have access to, the event won’t be triggered.

### ✅ 2. Confirm capabilities

Some event types require specific capabilities to be enabled for your integration.

For instance, to receive `comment.created` events, your integration must have the "**comment read**" capability selected. Without it, even if your integration has access to the page, the comment event won’t be delivered.

You can view and update your integration’s capabilities in the **Capabilities** section of your integration settings.

### ⏳ 3. Understand aggregated event timing

Not all webhook events are sent immediately. Some, like page.content\_updated, are aggregated to reduce noise from frequent edits (e.g., typing, formatting, moving blocks). This is normal and helps group multiple rapid changes into a single webhook event.

See [Event Delivery ](/reference/webhooks-events-delivery#event-delivery)for a deeper explanation.

<Tip>
  **Tip:**

  If you're testing and expecting an instant response, start with non-aggregated events like `comment.created` or `page.locked`.
</Tip>

### ☑️ Confirm your subscription status

Even if everything else is configured correctly, your webhook won’t receive events unless the subscription is active.

Head to the **Webhooks** tab under your integration settings and make sure your subscription is **active**. If the status shows as **paused**, **pending verification**, or if the subscription was deleted, events won’t be delivered to your endpoint.
