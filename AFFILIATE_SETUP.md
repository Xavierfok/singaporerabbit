# Affiliate Setup (one-time, ~30 min)

5 commercial-intent guides went live with affiliate placeholder tags. Replace `YOUR_AMAZON_SG_TAG` and `YOUR_SHOPEE_AFF` once you have real IDs.

## Files affected

```
git grep YOUR_AMAZON_SG_TAG src/content/guides/
git grep YOUR_SHOPEE_AFF src/content/guides/
```

5 files, each has ~10 affiliate links (Amazon SG + Shopee).

## 1. Amazon Associates Singapore

- Sign up: https://affiliate-program.amazon.com/signup (select Singapore as your country)
- Wait for approval (usually 1-3 days, sometimes longer)
- Once approved, your tracking ID looks like `yourname-22` for Amazon SG
- Add the ID to all guides: `git grep -l YOUR_AMAZON_SG_TAG src/content/guides/ | xargs sed -i '' 's/YOUR_AMAZON_SG_TAG/yourname-22/g'`

Note: Amazon SG affiliate has lower commission rates (1-4%) than other regions. Volume helps.

## 2. Shopee Affiliate Program

- Sign up: https://affiliate.shopee.sg/
- Complete the application (Shopee approves most applicants)
- Once approved, your `aff_id` is a numeric ID
- Add the ID: `git grep -l YOUR_SHOPEE_AFF src/content/guides/ | xargs sed -i '' 's/YOUR_SHOPEE_AFF/123456/g'`

Shopee SG affiliate has higher commission rates than Amazon (4-15% depending on category), especially on pet products.

## 3. After replacing tags

```
npm run check && npm run check:directory
git diff src/content/guides/best-*.mdx | head
git add src/content/guides/best-*.mdx
git commit -m "chore(affiliate): wire amazon SG and shopee tracking IDs"
git push
npm run deploy
```

## 4. Affiliate compliance

The guides already include the `affiliate_disclosure: true` frontmatter which renders the disclosure block at the top. They also include a line in the closing disclaimer mentioning affiliate links. This satisfies SG ad guidelines and Google's reviewer guidelines.

Do not:
- Add affiliate links to non-product guides (only the 5 `best-*` guides should have them)
- Set `affiliate_disclosure: true` on non-affiliate guides (would mislead readers)
- Add tracking parameters to internal links (only outbound product links)

## 5. Tracking revenue

- Amazon Associates dashboard: lifetime + this month earnings
- Shopee Affiliate dashboard: same
- Cross-reference with GA4: outbound link clicks track to `affiliate_click` event (TODO: wire this in if needed once volume justifies)

## 6. Optional: build more commercial guides later

Once these 5 prove themselves (3-6 months), candidate next batch:
- `best-rabbit-litter-singapore` (paper, pellet, hay-based)
- `best-rabbit-carriers-vet-trips-singapore`
- `best-rabbit-grooming-tools-singapore` (slicker, nail clippers, scissors)
- `best-rabbit-playpens-x-pens-singapore`
- `best-rabbit-cooling-products-singapore` (cooling mats, fans, ceramic tiles)
