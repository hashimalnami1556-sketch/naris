# NARIS Binary Asset Upload Queue

تمت مزامنة الملفات النصية القابلة للرفع عبر GitHub Contents API. الملفات الثنائية التالية موجودة في مساحة العمل الحالية وتحتاج رفعًا عبر Git/LFS لأن أداة GitHub المتاحة هنا لا تكتب ملفات binary:

## Images
- 0e2cbb0e-d7cf-42c8-8b24-e49388a91dd2.png — 339227 bytes
- 6bb1f590-d1c0-46e0-85e0-cfb479711aa2.png — 245572 bytes
- 8F4E91E1-9E25-4467-BAAC-1645CB0DDDD5.PNG — 2285352 bytes
- C7345319-AB11-4D05-BA19-85E8F35DDEE3.PNG — 1627645 bytes
- IMG_3619.jpeg — 501764 bytes
- IMG_3776.jpeg — 518622 bytes
- IMG_3846.jpeg — 61673 bytes
- IMG_3892.jpeg — 256431 bytes
- IMG_3893.jpeg — 293823 bytes
- IMG_3896.jpeg — 241694 bytes
- IMG_3897.jpeg — 211610 bytes
- IMG_3898.jpeg — 162008 bytes
- IMG_3899.jpeg — 192537 bytes
- IMG_4134.jpeg — 406026 bytes
- IMG_4137.jpeg — 370647 bytes
- IMG_4142.jpg — 851736 bytes
- e426709a-1e83-4a01-8828-e892b7c43d80.png — 123072 bytes
- fe2c93b6-c37a-462c-ab59-e09c8329415e.png — 120 bytes

## PDF
- Image to PDF 20250720152556.pdf — 720333 bytes

## Video
- gemini_generated_video_7C03F426.MP4 — 2358939 bytes
- gemini_generated_video_DFF0B0F4.MP4 — 2271195 bytes

## Required Git LFS
The repository already tracks `.fbx`, `.blend`, `.wav`, `.mp4`, `.mov`, `.psd`, `.tga`, `.exr`, `.uasset`, and `.umap` with Git LFS. Images/PDFs can be committed normally unless the project policy requires LFS.

## Recommended destination
assets/concept/images/
assets/concept/pdf/
assets/video/teasers/

This queue intentionally does not create fake binary placeholders. Actual binary content must be uploaded with Git/LFS from a Git-capable workspace.
