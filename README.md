Aura AR — Blender Add-on Concept

What it is

A personal Blender add-on that collapses the "model → AR → real world" pipeline into a single button click. Built for fast content creation (TikTok, Reels, demo capture) — not for client delivery. Client delivery already runs through AuraRef separately.

The problem it solves

Without the add-on, getting a model from Blender into a placeable real-world AR view requires several manual steps every time:


Export the model as GLB from Blender (File → Export → glTF 2.0)
Upload the GLB somewhere it can be served over HTTPS
Generate a viewer link / QR code pointing at that hosted file
Open the link on a phone, scan, place the model in the room
Record the result


Repeated for every new model, every variation, every take — this adds friction exactly where speed matters most: rapid content iteration.

The workflow with the add-on


Model, texture, and animate normally inside Blender — no change to the creative process
Click "Deploy to AR" inside Blender
The add-on automatically:

Exports the active model as a web-ready GLB
Uploads it to a hosting endpoint
Generates a single shareable link / QR code



Scan the QR code with any phone
The model appears placed in the real room via the phone's native AR view (no app install — works through the browser)
Film it directly for social content
# aura-ar
