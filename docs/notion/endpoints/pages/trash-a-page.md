> ## Documentation Index
> Fetch the complete documentation index at: https://developers.notion.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Trash a page

<Note>
  The API does not support permanently deleting pages.
</Note>

To archive a page via the API, send an [Update page](/reference/patch-page) request with the `archived` (or `in_trash`) body param set to `true`. To restore a page, set `archived` (or `in_trash`) to `false`.

## Example request: archive a Notion page

<CodeGroup>
  ```bash cURL theme={null}
  curl https://api.notion.com/v1/pages/60bdc8bd-3880-44b8-a9cd-8a145b3ffbd7 \
    -H 'Authorization: Bearer '"$NOTION_API_KEY"'' \
    -H "Content-Type: application/json" \
    -H "Notion-Version: 2025-09-03" \
    -X PATCH \
  	--data '{
      "archived": true
  }'
  ```
</CodeGroup>

If you are using Notion’s [JavaScript SDK](https://github.com/makenotion/notion-sdk-js) to interact with the REST API, use the `update` method available for Notion pages.

<CodeGroup>
  ```javascript JavaScript theme={null}
  const { Client } = require("@notionhq/client")

  // Initializing a client
  const notion = new Client({
  	auth: process.env.NOTION_API_KEY,
  })

  const archivePage = async () => {
  	await notion.pages.update({
  	  page_id: pageId,
  	  archived: true, // or in_trash: true
  	});
  }
  ```
</CodeGroup>

If successful, the API responds with a `200` HTTP status code and the archived page object, as in the following example:

<CodeGroup>
  ```json JSON expandable theme={null}
  {
      "object": "page",
      "id": "be633bf1-dfa0-436d-b259-571129a590e5",
      "created_time": "2022-10-24T22:54:00.000Z",
      "last_edited_time": "2023-03-08T18:25:00.000Z",
      "created_by": {
          "object": "user",
          "id": "c2f20311-9e54-4d11-8c79-7398424ae41e"
      },
      "last_edited_by": {
          "object": "user",
          "id": "9188c6a5-7381-452f-b3dc-d4865aa89bdf"
      },
      "cover": null,
      "icon": {
          "type": "emoji",
          "emoji": "🐞"
      },
      "parent": {
          "type": "database_id",
          "database_id": "a1d8501e-1ac1-43e9-a6bd-ea9fe6c8822b"
      },
      "archived": true,
    	"in_trash": true,
      "properties": {
          "Due date": {
              "id": "M%3BBw",
              "type": "date",
              "date": {
                  "start": "2023-02-23",
                  "end": null,
                  "time_zone": null
              }
          },
          "Status": {
              "id": "Z%3ClH",
              "type": "status",
              "status": {
                  "id": "86ddb6ec-0627-47f8-800d-b65afd28be13",
                  "name": "Not started",
                  "color": "default"
              }
          },
          "Title": {
              "id": "title",
              "type": "title",
              "title": [
                  {
                      "type": "text",
                      "text": {
                          "content": "Bug bash",
                          "link": null
                      },
                      "annotations": {
                          "bold": false,
                          "italic": false,
                          "strikethrough": false,
                          "underline": false,
                          "code": false,
                          "color": "default"
                      },
                      "plain_text": "Bug bash",
                      "href": null
                  }
              ]
          }
      },
      "url": "https://www.notion.so/Bug-bash-be633bf1dfa0436db259571129a590e5"
  }
  ```
</CodeGroup>

Refer to the [error codes](/reference/status-codes#error-codes) documentation for possible errors.

## Example request: restore a Notion page

<CodeGroup>
  ```bash cURL theme={null}
  curl https://api.notion.com/v1/pages/60bdc8bd-3880-44b8-a9cd-8a145b3ffbd7 \
    -H 'Authorization: Bearer '"$NOTION_API_KEY"'' \
    -H "Content-Type: application/json" \
    -H "Notion-Version: 2025-09-03" \
    -X PATCH \
  	--data '{
      "archived": false
  }'
  ```
</CodeGroup>

<CodeGroup>
  ```javascript JavaScript theme={null}
  // Restore an archived page using the Notion JavaScript SDK
  const restorePage = async () => {
  	await notion.pages.update({
  	  page_id: pageId,
  	  archived: false,
  	});
  }
  ```
</CodeGroup>

If successful, the API responds with a `200` HTTP status code and the restored [page object](/reference/page). Refer to the [error codes](/reference/status-codes#error-codes) documentation for possible errors.
