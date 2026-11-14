# Electric Eel: level-angle and Hunyuan upload correction

Preston reported Hunyuan rejecting the eel because the subject ratio was below 50%. The original square upload bounding boxes occupied only 4.7% (front) and 5.5% (back) of their 1024-square canvases. The common scale preserved raw pixel proportions but was unsuitable for the API occupancy requirement.

A tight crop of take-a improved framing but its rear silhouette still covered only 41.5% of the crop under a local alpha mask. That crop set is retained as diagnostic work, not a verified solution. The old front/rear projection also showed a vertical ladder of body collars inconsistent with a level camera.

One built-in image edit produced take-b-level: straight horizontal body in profiles, compact end-on front/back, violet armor/copper collars/blue capacitor retained. Prompt saved verbatim. Original output C:/Users/pmcga/.codex/generated_images/01a1b4cb-ea6f-73d3-b13c-1b8d1c8bb35d/exec-d025895a-c5e3-4dfb-a9db-fe34cf2844a9.png. Raw preserved unchanged, SHA256 af60edcda881e9c8b7fc8fc47c091f3c080b9207418fcb26dbe56134a5579122. Previous take-a remains unchanged. Exact image-generation usage/cost unavailable.

Current upload files in hunyuan_uploads_v1 are individual tightly cropped WHITE RGB rectangular PNGs. No scaling, stretching or body cropping during packaging; 4px white border. Background haze excluded through the four connected alpha>=128 silhouettes. All dimensions remain between 128 and 5000 pixels and far below the documented size cap.

Local foreground mask coverage: front 57.36%, back 56.68%, left 73.61%, right 74.28%. Bounding-box coverage is 93.5-95.1%. This is local verification, not a successful remote Hunyuan validation: the provider detector is not documented as identical to this mask. Exact model topology still needs review. No replacement 3D model was generated or verified.

Use electric_eel_hunyuan_uploads.zip from this take's hunyuan_uploads_v1 directory. Upload each named PNG in its matching view slot, not the raw grid or old square views. Tencent API guidance: https://www.tencentcloud.com/document/product/1284/75540 recommends a single object on a simple background occupying over half the image. No paid API submission or fal key access occurred.
